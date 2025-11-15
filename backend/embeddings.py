"""
Embeddings module - Generate vector embeddings for text
Supports OpenAI embeddings (if API key) or local SentenceTransformer
"""

import os
from typing import List, Union
import numpy as np

# Try OpenAI first
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Fallback to SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False


class EmbeddingGenerator:
    """
    Unified embedding generator
    """
    
    def __init__(self, method: str = "auto"):
        """
        Args:
            method: "openai", "sentence-transformer", or "auto"
        """
        self.method = method
        self.model = None
        
        if method == "auto":
            # Try OpenAI first
            if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
                self.method = "openai"
                openai.api_key = os.getenv("OPENAI_API_KEY")
            elif SENTENCE_TRANSFORMER_AVAILABLE:
                self.method = "sentence-transformer"
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            else:
                raise RuntimeError("No embedding model available")
        
        elif method == "openai":
            if not OPENAI_AVAILABLE:
                raise RuntimeError("OpenAI not installed")
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_API_KEY not set")
            openai.api_key = os.getenv("OPENAI_API_KEY")
        
        elif method == "sentence-transformer":
            if not SENTENCE_TRANSFORMER_AVAILABLE:
                raise RuntimeError("sentence-transformers not installed")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"✓ Embeddings initialized with method: {self.method}")
    
    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text
        
        Args:
            text: Single string or list of strings
        
        Returns:
            numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        if self.method == "openai":
            return self._embed_openai(text)
        else:
            return self._embed_sentence_transformer(text)
    
    def _embed_openai(self, texts: List[str]) -> np.ndarray:
        """OpenAI embeddings"""
        try:
            response = openai.Embedding.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            embeddings = [item['embedding'] for item in response['data']]
            return np.array(embeddings)
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            raise
    
    def _embed_sentence_transformer(self, texts: List[str]) -> np.ndarray:
        """Local SentenceTransformer embeddings"""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"SentenceTransformer error: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.method == "openai":
            return 1536  # ada-002 dimension
        else:
            return 384  # MiniLM dimension


# Global instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create global embedding generator"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator(method="auto")
    return _embedding_generator


def embed_text(text: Union[str, List[str]]) -> np.ndarray:
    """Convenience function to embed text"""
    generator = get_embedding_generator()
    return generator.embed(text)
