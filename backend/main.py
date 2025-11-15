from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
from typing import Optional, List, Dict
import time

# Import custom modules
from search import verify_with_sources
from utils import extract_keywords, calculate_similarity, summarize_text, extract_key_sentences
from summarize import get_summarizer
import ai_tasks

app = FastAPI(
    title="Fake News Verification API",
    description="Real-time fake news detection with multi-source verification + AI assistant",
    version="2.0.0"
)

# Include AI tasks router
app.include_router(ai_tasks.router)

# CORS middleware for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML model
MODEL_PATH = os.path.join("model", "model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    model = None


# Request/Response Models
class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    label: int

class VerifyRequest(BaseModel):
    text: str
    headline: Optional[str] = None

class VerifyResponse(BaseModel):
    verification_status: str
    matching_sources: List[str]
    similarity_scores: Dict[str, float]
    keywords: List[str]
    timestamp: float

class FullCheckResponse(BaseModel):
    model_prediction: str
    model_confidence: float
    verification_status: str
    matching_sources: List[str]
    similarity_scores: Dict[str, float]
    keywords: List[str]
    summary: str
    key_sentences: List[str]
    timestamp: float


@app.get("/")
async def root():
    return {
        "service": "Fake News Verification API + AI Assistant",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "core": ["/predict", "/verify", "/full-check", "/sources", "/summarize"],
            "ai_assistant": [
                "/ai/ask", "/ai/extract-claims", "/ai/rag-query",
                "/ai/draft", "/ai/explain", "/ai/feedback",
                "/ai/admin/health", "/ai/admin/stats"
            ]
        }
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    ML-based fake news prediction using trained model
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short")
    
    try:
        # Predict
        prediction = model.predict([request.text])[0]
        probabilities = model.predict_proba([request.text])[0]
        confidence = float(max(probabilities))
        
        # 0 = Fake, 1 = Real
        label_text = "REAL" if prediction == 1 else "FAKE"
        
        return PredictResponse(
            prediction=label_text,
            confidence=confidence,
            label=int(prediction)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest):
    """
    Multi-source verification using real-time news scraping
    """
    text = request.headline if request.headline else request.text
    
    if not text or len(text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text/headline required")
    
    try:
        # Extract keywords
        keywords = extract_keywords(text)
        
        # Verify with multiple sources
        verification_result = await verify_with_sources(text, keywords)
        
        return VerifyResponse(
            verification_status=verification_result["status"],
            matching_sources=verification_result["sources"],
            similarity_scores=verification_result["scores"],
            keywords=keywords,
            timestamp=time.time()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@app.post("/full-check", response_model=FullCheckResponse)
async def full_check(request: VerifyRequest):
    """
    Complete analysis: ML prediction + multi-source verification + summarization
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short")
    
    try:
        # Step 1: ML Prediction
        if model:
            prediction = model.predict([request.text])[0]
            probabilities = model.predict_proba([request.text])[0]
            confidence = float(max(probabilities))
            label_text = "REAL" if prediction == 1 else "FAKE"
        else:
            prediction = 0
            confidence = 0.0
            label_text = "UNKNOWN"
        
        # Step 2: Text Summarization
        summary = summarize_text(request.text, num_sentences=3)
        key_sentences = extract_key_sentences(request.text, num_sentences=5)
        
        # Step 3: Multi-source verification
        text = request.headline if request.headline else request.text
        keywords = extract_keywords(text)
        verification_result = await verify_with_sources(text, keywords)
        
        return FullCheckResponse(
            model_prediction=label_text,
            model_confidence=confidence,
            verification_status=verification_result["status"],
            matching_sources=verification_result["sources"],
            similarity_scores=verification_result["scores"],
            keywords=keywords,
            summary=summary,
            key_sentences=key_sentences,
            timestamp=time.time()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full check error: {str(e)}")


@app.get("/sources")
async def get_sources():
    """
    Return list of trusted sources used for verification
    """
    return {
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com", "region": "Global"},
            {"name": "AP News", "url": "https://apnews.com", "region": "Global"},
            {"name": "BBC", "url": "https://www.bbc.com/news", "region": "Global"},
            {"name": "The Hindu", "url": "https://www.thehindu.com", "region": "India"},
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com", "region": "India"},
            {"name": "NDTV", "url": "https://www.ndtv.com", "region": "India"},
            {"name": "Government Sources", "url": ".gov domains", "region": "Various"}
        ],
        "verification_method": "Real-time scraping + cosine similarity",
        "threshold": 0.6
    }


@app.post("/summarize")
async def summarize_endpoint(text: str, num_sentences: int = 3):
    """
    Standalone summarization endpoint
    """
    if not text or len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text too short")
    
    try:
        summary = summarize_text(text, num_sentences)
        key_sentences = extract_key_sentences(text, num_sentences=5)
        
        return {
            "summary": summary,
            "key_sentences": key_sentences,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round((1 - len(summary) / len(text)) * 100, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
