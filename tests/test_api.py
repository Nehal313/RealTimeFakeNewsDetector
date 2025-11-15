"""
Unit Tests for Fake News Detection System
Run with: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_endpoint(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data
        assert "timestamp" in data
    
    def test_sources_endpoint(self):
        """Test /sources endpoint"""
        response = client.get("/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) >= 6  # At least 6 sources


class TestPredictionEndpoint:
    """Test ML prediction endpoint"""
    
    def test_predict_fake_news(self):
        """Test prediction with likely fake news"""
        payload = {
            "text": "BREAKING: Aliens landed in New York City today and met with the President"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert data["prediction"] in ["FAKE", "REAL"]
        assert 0 <= data["confidence"] <= 1
    
    def test_predict_real_news(self):
        """Test prediction with likely real news"""
        payload = {
            "text": "The Supreme Court announced a new ruling on constitutional matters after careful deliberation"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
    
    def test_predict_empty_text(self):
        """Test prediction with empty text"""
        payload = {"text": ""}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error


class TestAIEndpoints:
    """Test AI assistant endpoints"""
    
    def test_ai_health(self):
        """Test AI admin health endpoint"""
        response = client.get("/ai/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "vector_store" in data
    
    def test_extract_claims(self):
        """Test claim extraction endpoint"""
        payload = {
            "text": "The President announced a new climate policy. Scientists say temperatures rose 1.5 degrees."
        }
        response = client.post("/ai/extract-claims", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "claims" in data
        assert isinstance(data["claims"], list)
    
    def test_ai_explain(self):
        """Test explanation endpoint"""
        payload = {
            "text": "Sample article text",
            "prediction": "FAKE",
            "confidence": 0.85
        }
        response = client.post("/ai/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data


class TestVerificationEndpoint:
    """Test multi-source verification (requires network)"""
    
    @pytest.mark.skip(reason="Requires network access and may be slow")
    def test_verify_endpoint(self):
        """Test verification endpoint"""
        payload = {
            "text": "Breaking news about climate change",
            "headline": "Climate Update"
        }
        response = client.post("/verify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "verification_status" in data
        assert "keywords" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
