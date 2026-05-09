from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.core.agent_engine import get_agent_executor
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn
import traceback
import logging
from fastapi.security import APIKeyHeader
from fastapi import Security, Depends

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("InsightFlow")

app = FastAPI(title="Secure AI Insights Assistant")

# --- Security: API Key Mock ---
API_KEY = "sk-insight-flow-2025"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        logger.warning(f"Unauthorized access attempt with key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    data: Optional[List] = None
    type: str = "text"
    thought_trace: str = ""

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    try:
        logger.info(f"Processing query: {request.query}")
        executor = get_agent_executor()
        result = executor.invoke(request.query)
        return ChatResponse(
            answer=result["answer"],
            data=result.get("data"),
            type=result.get("type", "text"),
            thought_trace=result.get("thought", "")
        )
    except Exception as e:
        logger.error(f"Error in /chat: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
