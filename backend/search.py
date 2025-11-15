import asyncio
import aiohttp
from typing import List, Dict
from bs4 import BeautifulSoup
import re
from utils import calculate_similarity, build_search_query, determine_verification_status


# Trusted news sources
TRUSTED_SOURCES = {
    "reuters": "https://www.reuters.com/search/news?blob=",
    "apnews": "https://apnews.com/search?q=",
    "bbc": "https://www.bbc.com/search?q=",
    "thehindu": "https://www.thehindu.com/search/?q=",
    "timesofindia": "https://timesofindia.indiatimes.com/topic/",
    "ndtv": "https://www.ndtv.com/search?searchtext=",
}

# User agent to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


async def fetch_url(session: aiohttp.ClientSession, url: str, timeout: int = 5) -> str:
    """
    Fetch URL content asynchronously
    """
    try:
        async with session.get(url, headers=HEADERS, timeout=timeout, ssl=False) as response:
            if response.status == 200:
                return await response.text()
            return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def extract_headlines(html: str, source: str) -> List[str]:
    """
    Extract headlines from HTML based on source
    """
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    headlines = []
    
    try:
        if source == "reuters":
            articles = soup.find_all('h3', class_='search-result-title')
            headlines = [article.get_text().strip() for article in articles[:5]]
        
        elif source == "apnews":
            articles = soup.find_all('h2', class_='Component-headline')
            headlines = [article.get_text().strip() for article in articles[:5]]
        
        elif source == "bbc":
            articles = soup.find_all(['h3', 'h2'], class_=re.compile('.*headline.*|.*title.*'))
            headlines = [article.get_text().strip() for article in articles[:5]]
        
        elif source == "thehindu":
            articles = soup.find_all('a', class_='story-card-img')
            headlines = [article.get('title', '').strip() for article in articles[:5]]
        
        elif source == "timesofindia":
            articles = soup.find_all('span', class_='w_tle')
            headlines = [article.get_text().strip() for article in articles[:5]]
        
        elif source == "ndtv":
            articles = soup.find_all('h2', class_='newsHdng')
            headlines = [article.get_text().strip() for article in articles[:5]]
        
        # Fallback: generic extraction
        if not headlines:
            articles = soup.find_all(['h1', 'h2', 'h3'])
            headlines = [article.get_text().strip() for article in articles[:10]]
    
    except Exception as e:
        print(f"Error extracting headlines from {source}: {e}")
    
    # Clean and filter
    headlines = [h for h in headlines if len(h) > 20 and len(h) < 300]
    return headlines[:5]


async def search_source(
    session: aiohttp.ClientSession,
    source_name: str,
    query: str,
    user_text: str
) -> Dict:
    """
    Search a single source and return similarity scores
    """
    if source_name not in TRUSTED_SOURCES:
        return {"source": source_name, "headlines": [], "max_similarity": 0.0}
    
    # Build search URL
    base_url = TRUSTED_SOURCES[source_name]
    search_url = f"{base_url}{query.replace(' ', '+')}"
    
    # Fetch content
    html = await fetch_url(session, search_url, timeout=8)
    
    # Extract headlines
    headlines = extract_headlines(html, source_name)
    
    # Calculate similarity scores
    similarities = []
    for headline in headlines:
        score = calculate_similarity(user_text, headline)
        similarities.append(score)
    
    max_similarity = max(similarities) if similarities else 0.0
    
    return {
        "source": source_name,
        "headlines": headlines,
        "max_similarity": max_similarity
    }


async def verify_with_sources(text: str, keywords: List[str]) -> Dict:
    """
    Verify text across multiple trusted sources
    
    Returns:
        {
            "status": "Verified | Unverified | Contradictory | Breaking News",
            "sources": [list of sources that confirmed],
            "scores": {source: similarity_score}
        }
    """
    # Build search query
    search_query = build_search_query(text, keywords)
    
    # Search all sources concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [
            search_source(session, source, search_query, text)
            for source in TRUSTED_SOURCES.keys()
        ]
        
        results = await asyncio.gather(*tasks)
    
    # Aggregate results
    similarity_scores = {}
    matching_sources = []
    
    for result in results:
        source = result["source"]
        max_sim = result["max_similarity"]
        
        similarity_scores[source] = max_sim
        
        if max_sim >= 0.6:  # High confidence threshold
            matching_sources.append(source)
    
    # Determine verification status
    status = determine_verification_status(similarity_scores, threshold=0.6)
    
    return {
        "status": status,
        "sources": matching_sources,
        "scores": similarity_scores
    }


async def verify_government_source(claim: str, country: str = "US") -> bool:
    """
    Verify against official government sources (.gov domains)
    """
    # Placeholder for .gov verification
    # In production, implement specific .gov API or scraping
    
    gov_domains = {
        "US": "https://www.usa.gov",
        "India": "https://www.india.gov.in",
        "UK": "https://www.gov.uk"
    }
    
    # This would need actual implementation
    return False
