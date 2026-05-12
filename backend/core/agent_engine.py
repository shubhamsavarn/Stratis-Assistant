import os
import re
import logging
from typing import Dict, Any, List
from sqlalchemy import create_engine, text
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("InsightFlow.Agent")


# =============================================================================
# SECTION 1: SINGLETON CONFIGURATION
# Purpose: All heavy resources (LLM, Embeddings, DB) are initialized ONCE 
#          and reused across every request to avoid redundant loading.
# =============================================================================

class BackendConfig:
    """
    Singleton configuration and resource manager.
    
    Why Singleton? Loading HuggingFace embeddings takes ~3 seconds and consumes
    ~200MB of RAM. Without a singleton, every API call would re-load these,
    causing severe latency and memory issues under load.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackendConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # --- Paths & Model Names from Environment ---
        self.db_path = os.getenv("DATABASE_PATH", "data/insights_assistant.db")
        self.chroma_path = os.getenv("CHROMA_PATH", "data/chroma_db")
        self.model_name = os.getenv("LLM_MODEL", "qwen2.5:0.5b")
        self.embed_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        # --- Initialize SQL Engine (SQLAlchemy) ---
        # SQLAlchemy manages connection pooling internally.
        self.sql_engine = create_engine(f"sqlite:///{self.db_path}")

        # --- Initialize Embedding Model (Heavy, ~200MB) ---
        logger.info(f"Loading Embedding Model: {self.embed_model}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embed_model)

        # --- Initialize LLM via Ollama ---
        logger.info(f"Connecting to Ollama LLM: {self.model_name}")
        self.llm = ChatOllama(model=self.model_name, temperature=0)

        # --- Database Schema Metadata ---
        # This schema string is injected into every SQL-generation prompt so the
        # LLM knows the exact table and column names. This prevents hallucination
        # of non-existent tables.
        self.schema_info = """
Tables available in the SQLite database:

1. movies
   Columns: movie_id (INT), title (TEXT), genre (TEXT), release_year (INT), budget (INT), revenue (INT)
   Description: Core catalog of all movie titles with financial performance data.

2. marketing_spend
   Columns: campaign_id (INT), movie_id (INT, FK->movies), spend (INT), channel (TEXT), campaign_name (TEXT)
   Description: Marketing campaign expenditure linked to specific movies.

3. regional_performance
   Columns: region_id (INT), region_name (TEXT), total_revenue (INT), active_users (INT)
   Description: Geographic performance metrics across global markets.

4. reviews
   Columns: review_id (INT), movie_id (INT, FK->movies), rating (INT), comment (TEXT)
   Description: Audience reviews and ratings for movies.

5. viewers
   Columns: viewer_id (INT), name (TEXT), age (INT), country (TEXT), subscription_type (TEXT), city (TEXT)
   Description: User/viewer demographic and subscription data.

6. watch_activity
   Columns: activity_id (INT), viewer_id (INT, FK->viewers), movie_id (INT, FK->movies), watch_date (TEXT), duration_minutes (INT)
   Description: Individual viewing session logs with timestamps and duration.

Key Relationships:
- movies.movie_id links to marketing_spend.movie_id, reviews.movie_id, watch_activity.movie_id
- viewers.viewer_id links to watch_activity.viewer_id
"""

        self._initialized = True
        logger.info("BackendConfig initialized successfully.")


# Instantiate global config on module load
config = BackendConfig()


# =============================================================================
# SECTION 2: SECURITY LAYER
# Purpose: Validates all LLM-generated SQL before execution to prevent
#          destructive operations (DROP, DELETE, etc.)
# =============================================================================

class SQLValidator:
    """
    Validates SQL queries before execution.
    
    Why? The LLM generates SQL dynamically. Without validation, a prompt-injection
    attack could trick the LLM into generating 'DROP TABLE movies;'. This class
    acts as a firewall between the LLM output and the database.
    """
    BLOCKED_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER",
        "TRUNCATE", "GRANT", "REVOKE", "CREATE", "EXEC",
        "ATTACH", "DETACH", "PRAGMA"
    ]

    @staticmethod
    def is_safe(query: str) -> bool:
        """Returns True only if the query contains no destructive operations."""
        query_upper = query.upper().strip()
        # Must start with SELECT
        if not query_upper.startswith("SELECT"):
            return False
        return not any(kw in query_upper for kw in SQLValidator.BLOCKED_KEYWORDS)

    @staticmethod
    def clean(raw_sql: str) -> str:
        """
        Cleans LLM-generated SQL by removing markdown artifacts and extra text.
        The LLM often wraps SQL in ```sql ... ``` blocks or adds explanations.
        Also fixes common hallucination patterns from small models.
        """
        # Remove markdown code blocks
        cleaned = re.sub(r'```\w*\n?', '', raw_sql)
        # Take only the first statement (before any semicolon)
        cleaned = cleaned.strip().split(";")[0].strip()
        # Remove any leading "SQL:" or "sql:" labels
        cleaned = re.sub(r'^(?:sql\s*:\s*)', '', cleaned, flags=re.IGNORECASE)
        # Fix triple-dot references: movies.marketing_spend.spend → marketing_spend.spend
        # Small LLMs often chain table names incorrectly
        cleaned = re.sub(r'(\w+)\.(\w+)\.(\w+)', r'\2.\3', cleaned)
        return cleaned


# =============================================================================
# SECTION 3: INTELLIGENT AGENT
# Purpose: The core decision-making engine. Uses LLM-based routing to handle
#          ANY question — data queries, report lookups, or general conversation.
# =============================================================================

class RobustAgent:
    """
    Production-grade AI Agent with three capabilities:
    
    1. SQL Tool   → For quantitative questions (numbers, rankings, comparisons)
    2. RAG Tool   → For qualitative questions (reports, strategies, context)
    3. Chat Tool  → For general conversation, greetings, or ambiguous questions
    
    The routing decision is made by the LLM itself, not by hardcoded keywords,
    enabling the agent to handle ANY question intelligently.
    """

    # Maximum number of SQL generation retries before falling back
    MAX_SQL_RETRIES = 3

    def __init__(self):
        self.config = config

    # -----------------------------------------------------------------
    # STEP 1: HYBRID ROUTING (Keywords first, then LLM for ambiguity)
    # -----------------------------------------------------------------

    # Keywords that strongly indicate a SQL query is needed
    SQL_KEYWORDS = [
        "best", "top", "worst", "highest", "lowest", "most", "least",
        "revenue", "budget", "spend", "spent", "cost", "profit",
        "how many", "count", "total", "average", "sum",
        "compare", "vs", "versus", "difference",
        "list", "show", "display", "give me", "find",
        "movie", "movies", "title", "titles", "film",
        "viewer", "viewers", "subscriber", "user", "users",
        "genre", "comedy", "action", "sci-fi", "drama", "horror", "thriller",
        "city", "region", "country", "market",
        "engagement", "perform", "performance", "rating", "review",
        "marketing", "campaign", "channel",
        "watch", "duration", "activity",
        "2024", "2025", "year",
    ]

    # Keywords that strongly indicate a PDF/report search is needed
    PDF_KEYWORDS = [
        "report", "summary", "executive", "strategy", "roadmap",
        "policy", "guidelines", "why is", "explain why", "trending",
        "legacy", "definition", "context", "campaign analysis",
        "quarterly", "q1", "q2", "q3", "q4", "recommendation",
        "explains", "explain", "weak", "insight", "insights",
        "recommend", "recommendations", "actions", "leadership",
        "what should", "next quarter", "growing fastest",
    ]

    # Keywords that indicate general conversation
    CHAT_KEYWORDS = [
        "hello", "hi", "hey", "thanks", "thank you", "bye", "goodbye",
        "who are you", "what can you do", "help me", "what is this",
    ]

    def _get_tool_choice(self, query: str) -> str:
        """
        Hybrid routing strategy:
        
        1. FAST PATH: Check keywords first for obvious cases (instant, no LLM call)
        2. SMART PATH: Use LLM only for genuinely ambiguous questions
        
        Why hybrid? The Qwen 0.5b model is fast but sometimes misclassifies
        clear data questions as "pdf". Keywords catch the obvious 80% of cases,
        and the LLM handles the creative 20%.
        
        Returns: "sql", "pdf", or "chat"
        """
        q_lower = query.lower().strip()

        # Helper: check if keyword exists as a whole word/phrase (not substring)
        def has_keyword(text: str, keyword: str) -> bool:
            return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text))

        # --- FAST PATH: Keyword Pre-Screening ---
        # Check chat keywords first (greetings are always chat)
        # Only match if the query is SHORT (< 5 words) or starts with a greeting
        words = q_lower.split()
        is_greeting = len(words) <= 4 and any(has_keyword(q_lower, kw) for kw in self.CHAT_KEYWORDS)
        if is_greeting:
            logger.info(f"Router (Keyword): '{query}' → chat")
            return "chat"

        # Check PDF and SQL keywords (use word boundary matching)
        pdf_score = sum(1 for kw in self.PDF_KEYWORDS if has_keyword(q_lower, kw))
        sql_score = sum(1 for kw in self.SQL_KEYWORDS if has_keyword(q_lower, kw))

        # If one clearly dominates, skip the LLM
        if sql_score >= 2 and sql_score > pdf_score:
            logger.info(f"Router (Keyword): '{query}' → sql (score: {sql_score})")
            return "sql"
        if pdf_score >= 2 and pdf_score > sql_score:
            logger.info(f"Router (Keyword): '{query}' → pdf (score: {pdf_score})")
            return "pdf"
        if sql_score == 1 and pdf_score == 0:
            logger.info(f"Router (Keyword): '{query}' → sql (score: {sql_score})")
            return "sql"
        if pdf_score == 1 and sql_score == 0:
            logger.info(f"Router (Keyword): '{query}' → pdf (score: {pdf_score})")
            return "pdf"

        # --- SMART PATH: LLM for Ambiguous Queries ---
        routing_prompt = f"""You are a query router for a movie analytics system.

Given the user's question, classify it into exactly ONE category:

- "sql" → The question asks about specific data, numbers, rankings, comparisons, counts, lists, or anything answerable from a database of movies, viewers, marketing spend, regional performance, reviews, or watch activity.
- "pdf" → The question asks about strategies, reports, executive summaries, campaign analysis, content roadmaps, policies, or qualitative business insights.
- "chat" → The question is a greeting, general conversation, or doesn't relate to movie/entertainment analytics.

Respond with ONLY one word: sql, pdf, or chat

Question: {query}
Category:"""

        try:
            response = self.config.llm.invoke(routing_prompt).content.strip().lower()
            if "sql" in response:
                tool = "sql"
            elif "pdf" in response:
                tool = "pdf"
            else:
                tool = "chat"
            logger.info(f"Router (LLM): '{query}' → {tool}")
            return tool
        except Exception as e:
            logger.error(f"Routing Error: {e}. Falling back to 'chat'.")
            return "chat"

    # -----------------------------------------------------------------
    # STEP 2a: SQL TOOL (Structured Data Retrieval)
    # -----------------------------------------------------------------
    def _execute_sql_tool(self, query: str) -> Dict[str, Any]:
        """
        Generates and executes a SQL query using the LLM.
        
        Flow:
        1. Send the schema + question to LLM → receive generated SQL
        2. Validate the SQL for safety (no DROP/DELETE)
        3. Execute against SQLite
        4. If execution fails, retry with error feedback (self-healing)
        5. Synthesize results into plain English
        """
        sql_prompt = f"""You are a SQLite expert. Generate ONLY a SQL SELECT query.

CRITICAL RULES:
- Use ONLY the exact table and column names listed below. Do NOT use aliases like T1, T2.
- Do NOT invent or guess column names. If unsure, use SELECT * FROM table_name LIMIT 10.
- In JOINs, reference columns as table_name.column_name (e.g. marketing_spend.spend, NOT movies.marketing_spend.spend).
- Return ONLY the raw SQL. No explanations, no markdown, no code blocks.
- Use LIMIT 10 for open-ended questions.

Schema:
- movies: movie_id, title, genre, release_year, budget, revenue
- marketing_spend: campaign_id, movie_id, spend, channel, campaign_name
- regional_performance: region_id, region_name, total_revenue, active_users
- reviews: review_id, movie_id, rating, comment
- viewers: viewer_id, name, age, country, subscription_type, city
- watch_activity: activity_id, viewer_id, movie_id, watch_date, duration_minutes

Examples:
Q: Which titles performed best in 2025?
A: SELECT title, revenue FROM movies WHERE release_year = 2025 ORDER BY revenue DESC LIMIT 10

Q: Compare Dark Orbit vs Last Kingdom.
A: SELECT title, revenue, budget FROM movies WHERE title IN ('Dark Orbit', 'Last Kingdom')

Q: Which city had the strongest engagement last month?
A: SELECT viewers.city, SUM(watch_activity.duration_minutes) as engagement FROM viewers JOIN watch_activity ON viewers.viewer_id = watch_activity.viewer_id GROUP BY viewers.city ORDER BY engagement DESC LIMIT 1

Q: Which genre is growing fastest?
A: SELECT genre, SUM(revenue) as total_revenue FROM movies GROUP BY genre ORDER BY total_revenue DESC LIMIT 5

Q: What audience segments are most engaged?
A: SELECT viewers.subscription_type, viewers.age, SUM(watch_activity.duration_minutes) as total_watch_time FROM viewers JOIN watch_activity ON viewers.viewer_id = watch_activity.viewer_id GROUP BY viewers.subscription_type, viewers.age ORDER BY total_watch_time DESC LIMIT 5

Q: What is the total marketing spend per movie?
A: SELECT movies.title, SUM(marketing_spend.spend) as total_spend FROM movies JOIN marketing_spend ON movies.movie_id = marketing_spend.movie_id GROUP BY movies.title ORDER BY total_spend DESC

Q: Which region has the most active users?
A: SELECT region_name, active_users FROM regional_performance ORDER BY active_users DESC LIMIT 5

Now answer this question:
Q: {query}
A:"""

        generated_sql = ""
        last_error = ""

        for attempt in range(self.MAX_SQL_RETRIES):
            try:
                # If retrying, include the error so LLM can self-correct
                if attempt > 0 and last_error:
                    retry_prompt = f"""{sql_prompt}

Your previous SQL attempt failed with this error: {last_error}
Please fix the query and try again. Return ONLY the corrected SQL:"""
                    raw_response = self.config.llm.invoke(retry_prompt).content
                else:
                    raw_response = self.config.llm.invoke(sql_prompt).content

                generated_sql = SQLValidator.clean(raw_response)
                logger.info(f"SQL Attempt {attempt + 1}: {generated_sql}")

                # Safety check
                if not SQLValidator.is_safe(generated_sql):
                    logger.warning(f"BLOCKED unsafe SQL: {generated_sql}")
                    return {
                        "answer": "I cannot execute that type of query for security reasons.",
                        "data": None,
                        "type": "text",
                        "thought": f"Blocked SQL: {generated_sql}"
                    }

                # Execute the query
                with self.config.sql_engine.connect() as conn:
                    result = conn.execute(text(generated_sql))
                    data = [dict(row) for row in result.mappings()]

                if not data:
                    return {
                        "answer": "The query executed successfully but returned no matching records. Try broadening your question.",
                        "data": None,
                        "type": "text",
                        "thought": f"Empty Result Set from: {generated_sql}"
                    }

                # Synthesize a human-readable answer from the data
                synth_prompt = f"""You are an executive analytics assistant. Given the data below, provide a clear, professional summary that directly answers the question.

Data: {data[:20]}
Question: {query}

Provide a concise summary with key insights:"""

                answer = self.config.llm.invoke(synth_prompt).content

                return {
                    "answer": answer,
                    "data": data,
                    "type": "table",
                    "thought": f"SQL Query: {generated_sql}"
                }

            except Exception as e:
                last_error = str(e)
                logger.error(f"SQL Attempt {attempt + 1} failed: {e}")
                continue

        # All retries exhausted — fall back to PDF context
        logger.warning(f"SQL failed after {self.MAX_SQL_RETRIES} attempts. Falling back to Vector Store.")
        return self._execute_pdf_tool(query, fallback_note=f"SQL generation failed ({last_error}). Searching reports instead.")

    # -----------------------------------------------------------------
    # STEP 2b: PDF/RAG TOOL (Unstructured Document Retrieval)
    # -----------------------------------------------------------------
    def _execute_pdf_tool(self, query: str, fallback_note: str = "") -> Dict[str, Any]:
        """
        Searches the ChromaDB vector store for relevant document chunks
        and synthesizes an answer from the retrieved context.
        
        Why ChromaDB? It stores mathematical "embeddings" of document text,
        allowing semantic search (meaning-based) rather than keyword search.
        """
        try:
            # IMPORTANT: collection_name must match what ingest.py uses ("internal_reports")
            vector_db = Chroma(
                persist_directory=self.config.chroma_path,
                collection_name="internal_reports",
                embedding_function=self.config.embeddings
            )
            docs = vector_db.similarity_search(query, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])

            if not context.strip():
                return {
                    "answer": "I couldn't find any relevant information in the internal reports.",
                    "data": None,
                    "type": "text",
                    "thought": "Vector store returned no results."
                }

            synth_prompt = f"""You are an executive analytics assistant. Answer the question using ONLY the context provided below.
If the context doesn't contain relevant information, say so honestly.

Context from Internal Reports:
{context}

Question: {query}

Provide a clear, professional answer:"""

            answer = self.config.llm.invoke(synth_prompt).content
            thought_msg = "Retrieved from internal reports via Vector Store."
            if fallback_note:
                thought_msg = f"{fallback_note} {thought_msg}"

            return {
                "answer": answer,
                "data": None,
                "type": "text",
                "thought": thought_msg
            }

        except Exception as e:
            logger.error(f"Vector Store Error: {e}")
            return {
                "answer": "I encountered an error searching the internal reports. Please try again.",
                "data": None,
                "type": "text",
                "thought": f"Vector Store Exception: {e}"
            }

    # -----------------------------------------------------------------
    # STEP 2c: CHAT TOOL (General Conversation)
    # -----------------------------------------------------------------
    def _execute_chat_tool(self, query: str) -> Dict[str, Any]:
        """
        Handles general conversation, greetings, and questions that don't
        require data retrieval.
        
        This ensures the agent never returns an error for casual questions
        like "Hello", "What can you do?", or "Thank you".
        """
        chat_prompt = f"""You are InsightFlow AI (NOT Qwen, NOT any other name). You are a professional analytics assistant built for a movie entertainment company.

Your name is InsightFlow AI. Never say you are Qwen or Alibaba Cloud.

You can help with:
1. Movie data analysis (revenue, budgets, genres, ratings)
2. Viewer demographics and watch patterns
3. Marketing spend and campaign performance
4. Regional market analysis
5. Internal report summaries (executive reports, policies, roadmaps)

If the user greets you, introduce yourself as InsightFlow AI and list what you can help with.
If the question is unclear, ask for clarification.

User: {query}
InsightFlow AI:"""

        try:
            answer = self.config.llm.invoke(chat_prompt).content
            return {
                "answer": answer,
                "data": None,
                "type": "text",
                "thought": "General conversation (no data tools used)."
            }
        except Exception as e:
            logger.error(f"Chat Tool Error: {e}")
            return {
                "answer": "I'm having trouble processing that right now. Could you try rephrasing your question?",
                "data": None,
                "type": "text",
                "thought": f"Chat Exception: {e}"
            }

    # -----------------------------------------------------------------
    # MAIN ENTRY POINT
    # -----------------------------------------------------------------
    def invoke(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for ALL query processing.
        
        Complete Flow:
        1. LLM Router classifies the question → sql / pdf / chat
        2. Appropriate tool is executed
        3. If SQL fails, automatically falls back to PDF search
        4. Response is always returned (never crashes)
        """
        logger.info(f"═══ New Request: {query} ═══")

        # Step 1: Let the LLM decide which tool to use
        tool = self._get_tool_choice(query)

        # Step 2: Execute the chosen tool
        if tool == "sql":
            return self._execute_sql_tool(query)
        elif tool == "pdf":
            return self._execute_pdf_tool(query)
        else:
            return self._execute_chat_tool(query)


def get_agent_executor():
    """Factory function for FastAPI dependency injection."""
    return RobustAgent()
