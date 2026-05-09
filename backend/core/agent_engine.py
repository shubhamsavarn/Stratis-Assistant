import os
import json
import re
from langchain_ollama import ChatOllama
from sqlalchemy import create_engine, text
import chromadb
from chromadb.utils import embedding_functions

# 1. Specialized Data Tools
def query_sql(query: str):
    engine = create_engine("sqlite:///data/insights_assistant.db")
    try:
        with engine.connect() as conn:
            # Clean common model-generated SQL issues
            query = query.strip().replace("`", "").replace("sql", "").replace(";", "")
            result = conn.execute(text(query))
            return [dict(row) for row in result.mappings()]
    except Exception as e:
        return f"SQL Error: {str(e)}"

def retrieve_docs(query: str) -> str:
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_collection(name="internal_reports", embedding_function=emb_fn)
        results = collection.query(query_texts=[query], n_results=2)
        return "\n".join(results['documents'][0])
    except Exception as e:
        return f"RAG Error: {str(e)}"

# 2. Ultra-Robust Agent
class RobustAgent:
    def __init__(self, model="phi3"):
        self.llm = ChatOllama(model=model, temperature=0)
        self.system_prompt = """You are a Secure Insights Assistant. Tables: movies, marketing_spend, viewers, watch_activity, reviews.
        Return ONLY valid JSON in this format:
        {
            "thought": "your reasoning",
            "action": "SQL_Query" or "PDF_Retrieval" or "FinalAnswer",
            "action_input": "query or text"
        }
        """

    def _extract_json(self, text):
        try:
            # Try finding the first '{' and last '}'
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None
        except:
            return None

    def invoke(self, user_input):
        print(f"DEBUG: Processing question -> {user_input}")
        prompt = f"{self.system_prompt}\n\nUser Question: {user_input}"
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            res_json = self._extract_json(content)

            if not res_json:
                # If no JSON, treat as FinalAnswer
                return {"output": content, "data": None, "thought": "Direct heuristic response."}

            if res_json.get("action") == "SQL_Query":
                sql = res_json["action_input"]
                # Fix common table name hallucinations
                sql = sql.replace("MovieData", "movies").replace("MarketingData", "marketing_spend")
                obs = query_sql(sql)
                
                final_prompt = f"Data Analysis Mode.\nQuestion: {user_input}\nResults: {obs}\nProvide final answer."
                final_res = self.llm.invoke(final_prompt)
                return {"output": final_res.content, "data": obs if isinstance(obs, list) else None, "thought": f"SQL Analysis: {sql}"}
            
            elif res_json.get("action") == "PDF_Retrieval":
                obs = retrieve_docs(res_json["action_input"])
                final_prompt = f"Document Synthesis Mode.\nQuestion: {user_input}\nContext: {obs}\nProvide final answer."
                final_res = self.llm.invoke(final_prompt)
                return {"output": final_res.content, "data": None, "thought": f"Vector Search: {res_json['action_input']}"}
            
            return {"output": res_json.get("action_input", content), "data": None, "thought": "Logic reasoning."}
        
        except Exception as e:
            return {"output": f"Error: {str(e)}", "data": None, "thought": "Exception occurred."}

def get_agent_executor():
    return RobustAgent(model=os.getenv("OLLAMA_MODEL", "phi3"))
