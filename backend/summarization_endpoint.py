from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class SummarizeRequest(BaseModel):
    text: str
    num_sentences: int = 3

class SummarizeResponse(BaseModel):
    summary: str
    key_sentences: List[str]
    original_length: int
    summary_length: int
    compression_ratio: float

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(request: SummarizeRequest):
    """
    Standalone text summarization endpoint
    """
    from utils import summarize_text, extract_key_sentences
    
    if not request.text or len(request.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text too short for summarization")
    
    try:
        summary = summarize_text(request.text, request.num_sentences)
        key_sentences = extract_key_sentences(request.text, num_sentences=5)
        
        original_len = len(request.text)
        summary_len = len(summary)
        compression = round((1 - summary_len / original_len) * 100, 2)
        
        return SummarizeResponse(
            summary=summary,
            key_sentences=key_sentences,
            original_length=original_len,
            summary_length=summary_len,
            compression_ratio=compression
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
