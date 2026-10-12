import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from rag import rag_engine
from ingest import ingest_documents

app = FastAPI(
    title="Healthcare Insurance Policy AI Engine",
    description="Microservice providing LangChain RAG & citation retrieval over insurance policies",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4

class Citation(BaseModel):
    source: str
    page: int
    content_preview: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    requires_human_review: bool

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "healthcare-ai-rag"}

@app.post("/ingest")
def trigger_ingest():
    try:
        ingest_documents()
        return {"status": "success", "message": "Policy documents re-indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def execute_query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        result = rag_engine.query(req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
