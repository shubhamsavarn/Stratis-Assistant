import os
import json
import logging
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InsightFlow.Agent")

DB_PATH = "data/insights_assistant.db"
CHROMA_PATH = "data/chroma_db"
SQL_ENGINE = create_engine(f"sqlite:///{DB_PATH}")
EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def query_sql(query: str):
    try:
        with SQL_ENGINE.connect() as conn:
            # Clean query
            query = query.strip().replace("`", "").replace("sql", "").replace(";", "")
            
            # --- DATE SAFETY ---
            if "2026" in query:
                query = query.replace("2026", "2025")
            if "date('now')" in query:
                query = query.replace("date('now')", "'2024-03-01'")

            result = conn.execute(text(query))
            rows = [dict(row) for row in result.mappings()]
            return rows
    except Exception as e:
        logger.error(f"SQL Error: {e}")
        return []

def query_pdf(query: str):
    try:
        vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=EMBEDDINGS)
        docs = vector_db.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        return "No report data found."

class RobustAgent:
    def __init__(self, model="qwen2.5:0.5b"):
        self.llm = ChatOllama(model=model, temperature=0, num_ctx=4096)
        self.system_prompt = """You are a restricted Tool-Access Agent. 
        DATABASE SCHEMA:
        - movies (movie_id, title, genre, release_year, budget, revenue)
        - marketing_spend (movie_id, campaign_name, spend, channel)
        - viewers (viewer_id, name, city, country)
        - watch_activity (activity_id, viewer_id, movie_id, watch_date, duration_minutes)
        - reviews (review_id, movie_id, rating, comment)
        - regional_performance (region_name, active_users, total_revenue)

        Instructions:
        1. Metrics/Stats: {"action": "sql", "input": "SELECT ..."}
        2. Descriptions/Roadmap: {"action": "pdf", "input": "topic"}

        Examples:
        - "best titles 2025" -> {"action": "sql", "input": "SELECT title, revenue FROM movies WHERE release_year = 2025 ORDER BY revenue DESC LIMIT 5"}
        - "why trending" -> {"action": "pdf", "input": "Stellar Run"}

        STRICT RULES:
        - ONLY use the table names above.
        - FINAL ANSWER MUST BE PLAIN TEXT. NO JSON.
        """

    def _extract_json(self, text):
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return None
        except:
            return None

    def invoke(self, query: str):
        logger.info(f"Agent Logic -> {query}")
        
        # 1. Routing
        res = self.llm.invoke(f"{self.system_prompt}\nUser: {query}\nJSON:")
        parsed = self._extract_json(res.content)

        if not parsed:
            return {"answer": res.content, "data": None, "type": "text", "thought": "Direct Answer"}

        action = parsed.get("action")
        tool_input = parsed.get("input")

        # 2. Tool Execution
        if action == "sql":
            data = query_sql(tool_input)
            if not data:
                return {"answer": "I found no matching records in the database.", "data": None, "type": "text", "thought": f"SQL: {tool_input}"}
            
            # FORCE PLAIN TEXT HERE
            answer = self.llm.invoke(f"System: Use this data: {data}. Answer the user question: '{query}' in PLAIN TEXT. NO JSON.")
            return {"answer": answer.content, "data": data, "type": "table", "thought": f"SQL: {tool_input}"}
        
        elif action == "pdf":
            context = query_pdf(tool_input)
            # FORCE PLAIN TEXT HERE
            answer = self.llm.invoke(f"System: Use this context: {context}. Answer the user question: '{query}' in PLAIN TEXT. NO JSON.")
            return {"answer": answer.content, "data": None, "type": "text", "thought": "RAG Search (PDF)"}

        return {"answer": res.content, "data": None, "type": "text", "thought": "Decision Made."}

def get_agent_executor():
    return RobustAgent()
