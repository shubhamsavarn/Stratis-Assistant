import os
import traceback
import logging
import uuid
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Security, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load configurations
load_dotenv()

# Import core engine
from backend.core.agent_engine import get_agent_executor
from scripts.ingest import ingest_csvs, ingest_pdfs

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("InsightFlow.API")

app = FastAPI(
    title="InsightFlow AI API",
    description="Production-grade AI Analytics Assistant Backend",
    version="2.0.0"
)

# --- Security Configuration ---
API_KEY = os.getenv("API_KEY", "sk-insight-flow-2025")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validates the X-API-KEY header against environment configuration."""
    if api_key != API_KEY:
        logger.warning(f"Unauthorized access attempt blocked.")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    data: Optional[List] = None
    type: str = "text"
    thought_trace: str = ""
    request_id: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """System health and heartbeat check."""
    return {
        "status": "operational",
        "version": "2.0.0",
        "engine": "qwen2.5:0.5b"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """
    Main processing endpoint for AI queries.
    Uses RobustAgent to route and execute data tools.
    """
    req_id = str(uuid.uuid4())[:8]
    try:
        logger.info(f"[{req_id}] Processing Query: {request.query}")
        
        executor = get_agent_executor()
        result = executor.invoke(request.query)
        
        return ChatResponse(
            answer=result["answer"],
            data=result.get("data"),
            type=result.get("type", "text"),
            thought_trace=result.get("thought", ""),
            request_id=req_id
        )
    except Exception as e:
        logger.error(f"[{req_id}] Critical Error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error (ID: {req_id})")

@app.post("/ingest")
async def trigger_ingestion(background_tasks: BackgroundTasks, api_key: str = Depends(verify_api_key)):
    """
    Asynchronously triggers the data ingestion pipeline.
    This processes raw CSVs and PDFs into SQLite and ChromaDB.
    """
    logger.info("Manual ingestion triggered via API.")
    
    def run_pipeline():
        try:
            ingest_csvs()
            ingest_pdfs()
            logger.info("Background ingestion completed successfully.")
        except Exception as e:
            logger.error(f"Background ingestion failed: {e}")

    background_tasks.add_task(run_pipeline)
    return {"message": "Ingestion pipeline started in background."}

if __name__ == "__main__":
    # Host and Port from .env
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
