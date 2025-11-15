"""
Unit Tests for Utility Functions
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils import extract_keywords, calculate_similarity, extractive_summary


class TestUtilityFunctions:
    """Test utility helper functions"""
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "Breaking news about climate change and global warming"
        keywords = extract_keywords(text, top_n=5)
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert all(isinstance(k, str) for k in keywords)
    
    def test_calculate_similarity(self):
        """Test text similarity calculation"""
        text1 = "Climate change is affecting global temperatures"
        text2 = "Global warming impacts climate worldwide"
        similarity = calculate_similarity(text1, text2)
        assert 0 <= similarity <= 1
        assert similarity > 0.3  # Should have some similarity
    
    def test_extractive_summary(self):
        """Test extractive summarization"""
        text = """
        Climate change is a serious issue. Scientists warn of rising temperatures.
        Global warming affects ecosystems. Immediate action is needed.
        """
        summary = extractive_summary(text, num_sentences=2)
        assert isinstance(summary, str)
        assert len(summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
