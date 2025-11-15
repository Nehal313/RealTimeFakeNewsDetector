"""
Advanced summarization using HuggingFace transformers
Supports multiple models with fallback
"""

from typing import Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available. Using TF-IDF fallback.")

from utils import summarize_text as tfidf_summarize


class AdvancedSummarizer:
    """
    Multi-model summarizer with fallback
    """
    
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        """
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.summarizer = None
        self.method = "tfidf"  # Default fallback
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print(f"Loading summarization model: {model_name}...")
                self.summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    device=-1  # CPU
                )
                self.method = "transformers"
                print(f"✓ Summarizer loaded: {model_name}")
            except Exception as e:
                print(f"Failed to load transformers model: {e}")
                print("Falling back to TF-IDF summarization")
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 40,
        num_sentences: int = 3
    ) -> str:
        """
        Generate summary
        
        Args:
            text: Input text
            max_length: Maximum summary length (for transformers)
            min_length: Minimum summary length (for transformers)
            num_sentences: Number of sentences (for TF-IDF)
        
        Returns:
            Summary text
        """
        if not text or len(text.strip()) < 100:
            return text
        
        if self.method == "transformers" and self.summarizer:
            try:
                # Truncate if too long (BART has 1024 token limit)
                max_input_length = 1024
                if len(text.split()) > max_input_length:
                    text = ' '.join(text.split()[:max_input_length])
                
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                return result[0]['summary_text']
            
            except Exception as e:
                print(f"Transformer summarization failed: {e}")
                # Fallback to TF-IDF
                return tfidf_summarize(text, num_sentences)
        
        else:
            # TF-IDF fallback
            return tfidf_summarize(text, num_sentences)
    
    def batch_summarize(self, texts: list, **kwargs) -> list:
        """Summarize multiple texts"""
        return [self.summarize(text, **kwargs) for text in texts]


# Global instance
_summarizer = None

def get_summarizer() -> AdvancedSummarizer:
    """Get or create global summarizer"""
    global _summarizer
    if _summarizer is None:
        _summarizer = AdvancedSummarizer()
    return _summarizer


def summarize_advanced(
    text: str,
    max_length: int = 150,
    min_length: int = 40
) -> str:
    """Convenience function for advanced summarization"""
    summarizer = get_summarizer()
    return summarizer.summarize(text, max_length, min_length)
