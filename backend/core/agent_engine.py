import os
import json
import re
from langchain_ollama import ChatOllama
from sqlalchemy import create_engine, text
import chromadb
from chromadb.utils import embedding_functions

# --- Global Initialization ---
EMB_FN = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
CHROMA_CLIENT = chromadb.PersistentClient(path="data/chroma_db")
SQL_ENGINE = create_engine("sqlite:///data/insights_assistant.db")

# 1. Specialized Data Tools
def query_sql(query: str):
    try:
        with SQL_ENGINE.connect() as conn:
            query = query.strip().replace("`", "").replace("sql", "").replace(";", "")
            result = conn.execute(text(query))
            rows = [dict(row) for row in result.mappings()]
            
            # AUTO-ALIASING FOR CHARTS (Fixes the "no graph" issue)
            for row in rows:
                if 'revenue' in row and 'value' not in row: row['value'] = row['revenue']
                if 'spend' in row and 'value' not in row: row['value'] = row['spend']
                if 'count' in row and 'value' not in row: row['value'] = row['count']
                if 'title' in row and 'name' not in row: row['name'] = row['title']
            return rows
    except Exception as e:
        return f"SQL Error: {str(e)}"

def retrieve_docs(query: str) -> str:
    try:
        collection = CHROMA_CLIENT.get_collection(name="internal_reports", embedding_function=EMB_FN)
        results = collection.query(query_texts=[query], n_results=2)
        return "\n".join(results['documents'][0])
    except Exception as e:
        return f"RAG Error: {str(e)}"

# 2. Ultra-Robust Agent
class RobustAgent:
    def __init__(self, model="qwen2.5:0.5b"):
        self.llm = ChatOllama(model=model, temperature=0, num_ctx=4096)
        self.system_prompt = """You are a Data API. You MUST return ONLY JSON.
        Tables: movies (id, title, revenue, release_year), marketing_spend (region, spend), watch_activity (movie_id, watch_date).
        
        If SQL is needed, return: {"action": "sql", "input": "SELECT ..."}
        If PDF is needed, return: {"action": "pdf", "input": "search text"}
        If answering directly, return: {"action": "answer", "input": "your text"}
        
        Use strftime('%Y', watch_date) for years in SQLite.
        """

    def _extract_json(self, text):
        try:
            # Look for ANY json-like block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None
        except:
            return None

    def invoke(self, user_input):
        print(f"DEBUG: Processing -> {user_input}")
        prompt = f"{self.system_prompt}\nUser: {user_input}\nJSON:"
        
        try:
            response = self.llm.invoke(prompt)
            res_json = self._extract_json(response.content)

            if not res_json:
                return {"output": response.content, "data": None, "thought": "Direct response."}

            action = res_json.get("action", "").lower()
            val = res_json.get("input", "")

            if action == "sql":
                obs = query_sql(val)
                final_prompt = f"Data: {obs}\nQuestion: {user_input}\nSummarize:"
                final_res = self.llm.invoke(final_prompt)
                return {"output": final_res.content, "data": obs if isinstance(obs, list) else None, "thought": f"SQL Executed: {val}"}
            
            elif action == "pdf":
                obs = retrieve_docs(val)
                final_prompt = f"Context: {obs}\nQuestion: {user_input}\nAnswer:"
                final_res = self.llm.invoke(final_prompt)
                return {"output": final_res.content, "data": None, "thought": f"PDF Search: {val}"}
            
            return {"output": val, "data": None, "thought": "Direct Answer."}
        
        except Exception as e:
            return {"output": f"Error: {str(e)}", "data": None, "thought": "Error handler."}

def get_agent_executor():
    return RobustAgent(model=os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b"))
