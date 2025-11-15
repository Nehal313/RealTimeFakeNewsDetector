import re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOP_WORDS = set(stopwords.words('english'))


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    """
    # Remove special characters, URLs, extra spaces
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^A-Za-z0-9\s]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract top keywords from text using TF-IDF and frequency
    """
    cleaned = clean_text(text)
    
    # Tokenize
    tokens = word_tokenize(cleaned)
    
    # Remove stopwords and short words
    keywords = [
        word for word in tokens 
        if word not in STOP_WORDS and len(word) > 3
    ]
    
    # Get most frequent keywords
    word_freq = Counter(keywords)
    top_keywords = [word for word, _ in word_freq.most_common(top_n)]
    
    return top_keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two texts using TF-IDF
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    
    except Exception as e:
        print(f"Similarity calculation error: {e}")
        return 0.0


def detect_claim_type(text: str) -> str:
    """
    Detect type of claim (death, policy, law, etc.)
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['died', 'death', 'dead', 'passed away', 'killed']):
        return 'death'
    
    if any(word in text_lower for word in ['law', 'legislation', 'bill', 'act', 'regulation']):
        return 'law'
    
    if any(word in text_lower for word in ['policy', 'government', 'minister', 'president', 'prime minister']):
        return 'policy'
    
    if any(word in text_lower for word in ['celebrity', 'actor', 'actress', 'star', 'famous']):
        return 'celebrity'
    
    return 'general'


def build_search_query(text: str, keywords: List[str]) -> str:
    """
    Build optimized search query from text and keywords
    """
    # Use top 5 keywords
    query_keywords = keywords[:5]
    
    # Add claim type context
    claim_type = detect_claim_type(text)
    
    if claim_type == 'death':
        query_keywords.append('news')
    elif claim_type in ['law', 'policy']:
        query_keywords.append('official')
    
    return ' '.join(query_keywords)


def determine_verification_status(
    similarity_scores: Dict[str, float],
    threshold: float = 0.6
) -> str:
    """
    Determine verification status based on similarity scores
    
    Returns:
        - "Verified" if multiple sources confirm (similarity > threshold)
        - "Contradictory" if sources have conflicting info
        - "Unverified" if no strong matches
        - "Breaking News - Low Confirmation" if some matches but not enough
    """
    if not similarity_scores:
        return "Unverified"
    
    high_scores = [score for score in similarity_scores.values() if score >= threshold]
    medium_scores = [score for score in similarity_scores.values() if 0.4 <= score < threshold]
    
    if len(high_scores) >= 2:
        return "Verified"
    elif len(high_scores) == 1 and len(medium_scores) >= 2:
        return "Likely Verified"
    elif len(medium_scores) >= 1:
        return "Breaking News - Low Confirmation"
    else:
        return "Unverified"


def summarize_text(text: str, num_sentences: int = 3) -> str:
    """
    Extractive text summarization using TF-IDF sentence scoring
    
    Args:
        text: Input text to summarize
        num_sentences: Number of sentences in summary
    
    Returns:
        Summarized text
    """
    if not text or len(text.strip()) < 100:
        return text
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= num_sentences:
        return text
    
    try:
        # Create TF-IDF matrix for sentences
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100,
            lowercase=True
        )
        
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Calculate sentence scores (sum of TF-IDF values)
        sentence_scores = tfidf_matrix.sum(axis=1).A1
        
        # Get top N sentence indices
        top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
        
        # Sort indices to maintain original order
        top_indices_sorted = sorted(top_indices)
        
        # Build summary
        summary_sentences = [sentences[i] for i in top_indices_sorted]
        summary = ' '.join(summary_sentences)
        
        return summary
    
    except Exception as e:
        print(f"Summarization error: {e}")
        # Fallback: return first N sentences
        return ' '.join(sentences[:num_sentences])


def extract_key_sentences(text: str, num_sentences: int = 5) -> List[str]:
    """
    Extract most important sentences from text using TF-IDF
    
    Returns:
        List of key sentences
    """
    if not text:
        return []
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= num_sentences:
        return sentences
    
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100
        )
        
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = tfidf_matrix.sum(axis=1).A1
        
        top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
        top_indices_sorted = sorted(top_indices)
        
        return [sentences[i] for i in top_indices_sorted]
    
    except Exception as e:
        print(f"Key sentence extraction error: {e}")
        return sentences[:num_sentences]
