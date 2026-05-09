from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.core.agent_engine import get_agent_executor
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn
import traceback

app = FastAPI(title="Secure AI Insights Assistant")

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
    thought_trace: str = ""
    data: Optional[List] = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        executor = get_agent_executor()
        result = executor.invoke(request.query)
        return ChatResponse(
            answer=result["output"],
            thought_trace=str(result.get("thought", "")),
            data=result.get("data")
        )
    except Exception as e:
        print(f"ERROR in /chat: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
