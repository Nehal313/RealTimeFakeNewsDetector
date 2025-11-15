"""
Claims extraction module - Extract verifiable claims from articles
"""

import re
from typing import List, Dict
from utils import clean_text
import nltk


def extract_claims(text: str) -> List[Dict]:
    """
    Extract major claims from article text
    
    Returns:
        List of claim dicts with:
        - claim: The extracted claim text
        - type: claim type (factual, opinion, prediction, etc.)
        - entities: Named entities mentioned
        - verification_query: Suggested search query
    """
    if not text or len(text.strip()) < 50:
        return []
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    claims = []
    claim_indicators = [
        'announced', 'stated', 'confirmed', 'revealed', 'reported',
        'said', 'according to', 'claims that', 'alleges', 'died',
        'killed', 'arrested', 'passed away', 'discovered', 'found',
        'launched', 'signed', 'approved', 'rejected', 'banned'
    ]
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        
        # Check if sentence contains claim indicators
        has_indicator = any(indicator in sentence_lower for indicator in claim_indicators)
        
        # Check for quotes (often claims)
        has_quote = '"' in sentence or '"' in sentence or "'" in sentence
        
        # Check for numbers/stats (factual claims)
        has_number = bool(re.search(r'\d+', sentence))
        
        # Heuristic: sentence is likely a claim
        is_claim = has_indicator or has_quote or (has_number and len(sentence.split()) > 5)
        
        if is_claim and len(sentence.split()) >= 5:
            claim_type = determine_claim_type(sentence)
            entities = extract_entities_simple(sentence)
            
            claims.append({
                "claim": sentence.strip(),
                "type": claim_type,
                "entities": entities,
                "verification_query": build_verification_query(sentence, entities),
                "sentence_index": i
            })
    
    # Limit to top 10 claims
    return claims[:10]


def determine_claim_type(sentence: str) -> str:
    """Classify claim type"""
    sentence_lower = sentence.lower()
    
    if any(word in sentence_lower for word in ['will', 'would', 'expect', 'predict', 'likely']):
        return 'prediction'
    
    if any(word in sentence_lower for word in ['should', 'must', 'need to', 'ought']):
        return 'opinion'
    
    if any(word in sentence_lower for word in ['died', 'killed', 'death', 'passed away']):
        return 'death'
    
    if any(word in sentence_lower for word in ['law', 'policy', 'bill', 'signed', 'approved']):
        return 'policy'
    
    if re.search(r'\d+', sentence):
        return 'statistical'
    
    return 'factual'


def extract_entities_simple(text: str) -> List[str]:
    """
    Simple entity extraction using patterns
    (In production, use spaCy or NER model)
    """
    entities = []
    
    # Capitalized sequences (likely names/places)
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    entities.extend(capitalized[:5])
    
    # Organizations (contains Corp, Inc, Ltd, etc.)
    orgs = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Corp|Inc|Ltd|LLC|Organization|Agency)\b', text)
    entities.extend(orgs)
    
    # Remove duplicates
    entities = list(set(entities))
    
    return entities[:5]


def build_verification_query(claim: str, entities: List[str]) -> str:
    """Build search query for claim verification"""
    # Use entities if available
    if entities:
        query = ' '.join(entities[:3])
    else:
        # Use first 5-7 words
        words = claim.split()[:7]
        query = ' '.join(words)
    
    # Clean
    query = re.sub(r'[^\w\s]', '', query)
    
    return query.strip()


def rank_claims_by_importance(claims: List[Dict]) -> List[Dict]:
    """
    Rank claims by verification priority
    
    Priority factors:
    - Death/disaster claims: highest
    - Policy/law claims: high
    - Statistical claims: medium
    - Predictions/opinions: lower
    """
    priority_map = {
        'death': 5,
        'policy': 4,
        'statistical': 3,
        'factual': 2,
        'prediction': 1,
        'opinion': 0
    }
    
    for claim in claims:
        claim['priority'] = priority_map.get(claim['type'], 1)
    
    # Sort by priority
    sorted_claims = sorted(claims, key=lambda x: x['priority'], reverse=True)
    
    return sorted_claims
