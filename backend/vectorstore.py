"""
Vector store using FAISS for similarity search
"""

import os
import pickle
from typing import List, Tuple, Dict
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available. Install with: pip install faiss-cpu")

from embeddings import get_embedding_generator


class VectorStore:
    """
    FAISS-based vector store for evidence retrieval
    """
    
    def __init__(self, index_path: str = ".vectordb"):
        """
        Args:
            index_path: Directory to store FAISS index
        """
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available")
        
        self.index_path = index_path
        os.makedirs(index_path, exist_ok=True)
        
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")
        
        self.embedding_gen = get_embedding_generator()
        self.dimension = self.embedding_gen.get_dimension()
        
        # Initialize or load index
        if os.path.exists(self.index_file):
            self.load()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
        
        print(f"✓ VectorStore initialized with {self.index.ntotal} vectors")
    
    def add(self, texts: List[str], metadata: List[Dict] = None):
        """
        Add texts to vector store
        
        Args:
            texts: List of text documents
            metadata: List of metadata dicts (one per text)
        """
        if not texts:
            return
        
        # Generate embeddings
        embeddings = self.embedding_gen.embed(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        if metadata is None:
            metadata = [{"text": text} for text in texts]
        
        self.metadata.extend(metadata)
        
        print(f"✓ Added {len(texts)} vectors. Total: {self.index.ntotal}")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Query text
            k: Number of results
        
        Returns:
            List of results with scores and metadata
        """
        if self.index.ntotal == 0:
            return []
        
        # Embed query
        query_embedding = self.embedding_gen.embed(query)
        
        # Search
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            min(k, self.index.ntotal)
        )
        
        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(dist)
                result['similarity'] = 1 / (1 + float(dist))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, self.index_file)
        
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"✓ VectorStore saved to {self.index_path}")
    
    def load(self):
        """Load index and metadata from disk"""
        if not os.path.exists(self.index_file):
            raise FileNotFoundError(f"Index not found: {self.index_file}")
        
        self.index = faiss.read_index(self.index_file)
        
        with open(self.metadata_file, 'rb') as f:
            self.metadata = pickle.load(f)
        
        print(f"✓ VectorStore loaded from {self.index_path}")
    
    def clear(self):
        """Clear all vectors"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("✓ VectorStore cleared")
    
    def stats(self) -> Dict:
        """Get store statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": self.index_path,
            "method": self.embedding_gen.method
        }


# Global instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create global vector store"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
