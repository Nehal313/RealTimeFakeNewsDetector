"""
AI Special Tasks Module
Advanced AI assistant capabilities using RAG, embeddings, and LLM reasoning
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import json
import os

from vectorstore import get_vector_store
from embeddings import embed_text
from claims import extract_claims, rank_claims_by_importance
from summarize import get_summarizer
from utils import extract_keywords, extract_key_sentences
from search import verify_with_sources

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# Request/Response Models
class AskRequest(BaseModel):
    question: str
    context: Optional[str] = None

class ExtractClaimsRequest(BaseModel):
    text: str

class RAGQueryRequest(BaseModel):
    query: str
    k: int = 5

class DraftRequest(BaseModel):
    text: str
    draft_type: str  # rebuttal, press_release, tweet, summary, bullets

class ExplainRequest(BaseModel):
    text: str
    prediction: str
    confidence: float

class FeedbackRequest(BaseModel):
    article_text: str
    model_prediction: str
    user_verdict: str
    user_comment: Optional[str] = None


# In-memory stats (in production, use Redis/DB)
stats = {
    "total_queries": 0,
    "total_claims_extracted": 0,
    "total_rag_queries": 0,
    "total_drafts": 0,
    "total_feedback": 0,
    "start_time": time.time()
}


@router.post("/ask")
async def ai_ask(request: AskRequest):
    """
    Natural language Q&A about an article using RAG
    """
    try:
        stats["total_queries"] += 1
        
        vector_store = get_vector_store()
        
        # If context provided, add to vector store temporarily
        if request.context:
            vector_store.add(
                [request.context],
                [{"source": "user_context", "timestamp": time.time()}]
            )
        
        # Retrieve relevant evidence
        results = vector_store.search(request.question, k=3)
        
        # Build answer from evidence
        if results:
            evidence_texts = [r.get('text', '') for r in results]
            answer = f"Based on available evidence:\n\n"
            
            for i, text in enumerate(evidence_texts[:2], 1):
                answer += f"{i}. {text[:200]}...\n\n"
            
            answer += f"\nConfidence: {results[0]['similarity']:.2%}"
        else:
            answer = "No relevant information found in the knowledge base."
        
        return {
            "question": request.question,
            "answer": answer,
            "evidence_count": len(results),
            "top_evidence": results[:3] if results else []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-claims")
async def extract_claims_endpoint(request: ExtractClaimsRequest):
    """
    Extract all major verifiable claims from article
    """
    try:
        stats["total_claims_extracted"] += 1
        
        claims = extract_claims(request.text)
        ranked_claims = rank_claims_by_importance(claims)
        
        return {
            "claims": ranked_claims,
            "total_claims": len(ranked_claims),
            "high_priority": [c for c in ranked_claims if c['priority'] >= 4]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag-query")
async def rag_query(request: RAGQueryRequest):
    """
    Retrieve evidence using RAG (vector similarity search)
    """
    try:
        stats["total_rag_queries"] += 1
        
        vector_store = get_vector_store()
        results = vector_store.search(request.query, k=request.k)
        
        return {
            "query": request.query,
            "results": results,
            "total_results": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft")
async def generate_draft(request: DraftRequest):
    """
    Generate various text drafts: rebuttal, press release, tweets, etc.
    """
    try:
        stats["total_drafts"] += 1
        
        summarizer = get_summarizer()
        draft_type = request.draft_type.lower()
        
        if draft_type == "summary":
            draft = summarizer.summarize(request.text, max_length=150)
        
        elif draft_type == "bullets":
            key_sentences = extract_key_sentences(request.text, num_sentences=5)
            draft = "\n".join([f"• {s}" for s in key_sentences])
        
        elif draft_type == "tweet":
            summary = summarizer.summarize(request.text, max_length=60)
            keywords = extract_keywords(request.text, top_n=3)
            hashtags = ' '.join([f'#{kw}' for kw in keywords])
            draft = f"{summary}\n\n{hashtags}"
        
        elif draft_type == "rebuttal":
            draft = f"""FACT-CHECK REBUTTAL

Original Claim:
{request.text[:200]}...

Our Analysis:
This claim requires verification across multiple trusted sources. 
We recommend cross-referencing with Reuters, AP News, and official government sources.

Key Concerns:
• Lack of primary source attribution
• Unverified statistics or quotes
• Absence of corroborating evidence

Recommendation: Treat as UNVERIFIED until confirmed by established news outlets.
"""
        
        elif draft_type == "press_release":
            keywords = extract_keywords(request.text, top_n=5)
            draft = f"""PRESS RELEASE - FACT VERIFICATION ALERT

FOR IMMEDIATE RELEASE

SUBJECT: Verification Status Update

Our fact-checking team has analyzed recent claims regarding: {', '.join(keywords)}

Key Findings:
[Automated analysis complete - human review recommended]

For more information, contact our verification team.
"""
        
        else:
            raise HTTPException(status_code=400, detail="Invalid draft_type")
        
        return {
            "draft_type": draft_type,
            "draft": draft,
            "timestamp": time.time()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_prediction(request: ExplainRequest):
    """
    Explain model reasoning and confidence factors
    """
    try:
        keywords = extract_keywords(request.text, top_n=10)
        
        # Analyze confidence
        confidence_level = "High" if request.confidence > 0.8 else "Medium" if request.confidence > 0.6 else "Low"
        
        explanation = {
            "prediction": request.prediction,
            "confidence": request.confidence,
            "confidence_level": confidence_level,
            "key_factors": {
                "top_keywords": keywords[:5],
                "text_length": len(request.text.split()),
                "analysis": f"Model is {confidence_level.lower()} confidence ({request.confidence:.1%}) "
                           f"that this content is {request.prediction}."
            },
            "interpretation": generate_interpretation(request.prediction, request.confidence),
            "recommendation": generate_recommendation(request.prediction, request.confidence)
        }
        
        return explanation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def log_feedback(request: FeedbackRequest):
    """
    Log user feedback and verdict corrections
    """
    try:
        stats["total_feedback"] += 1
        
        # In production, save to database
        feedback_entry = {
            "timestamp": time.time(),
            "model_prediction": request.model_prediction,
            "user_verdict": request.user_verdict,
            "comment": request.user_comment,
            "text_snippet": request.article_text[:200]
        }
        
        # Log to file
        log_file = "logs/feedback.jsonl"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(feedback_entry) + '\n')
        
        return {
            "status": "feedback_recorded",
            "message": "Thank you for your feedback. This helps improve our system.",
            "timestamp": feedback_entry["timestamp"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/health")
async def health_check():
    """
    System health check
    """
    try:
        vector_store = get_vector_store()
        vs_stats = vector_store.stats()
        
        return {
            "status": "healthy",
            "uptime_seconds": time.time() - stats["start_time"],
            "vector_store": vs_stats,
            "stats": stats
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/admin/stats")
async def get_stats():
    """
    Get usage statistics
    """
    return {
        "stats": stats,
        "uptime_hours": (time.time() - stats["start_time"]) / 3600
    }


# Helper functions
def generate_interpretation(prediction: str, confidence: float) -> str:
    """Generate human-readable interpretation"""
    if prediction == "FAKE":
        if confidence > 0.9:
            return "Strong indicators of misinformation detected."
        elif confidence > 0.7:
            return "Multiple red flags suggest this may be fake news."
        else:
            return "Some suspicious patterns detected, but further verification needed."
    else:
        if confidence > 0.9:
            return "Content appears legitimate with high confidence."
        elif confidence > 0.7:
            return "Likely authentic, but cross-verification recommended."
        else:
            return "Uncertain classification - verify with trusted sources."


def generate_recommendation(prediction: str, confidence: float) -> str:
    """Generate actionable recommendation"""
    if prediction == "FAKE" and confidence > 0.7:
        return "⚠️ DO NOT SHARE. Verify with trusted news sources before acting on this information."
    elif prediction == "FAKE":
        return "⚠️ Approach with caution. Cross-check with multiple sources."
    elif confidence < 0.7:
        return "✓ Verify independently before fully trusting this content."
    else:
        return "✓ Appears credible, but always good to verify important claims."
