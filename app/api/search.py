"""
Search API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    k: int = 10

class SearchResultResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    author: str
    score: float
    time_ago: str

class SearchResponse(BaseModel):
    results: List[SearchResultResponse]
    total_results: int
    search_time_ms: float
    query: str

# We'll inject these from main.py
vector_search = None
performance_monitor = None

def get_services():
    """Get global services - will be set by main.py"""
    from app.main import vector_search as vs, performance_monitor as pm
    return vs, pm

@router.post("/", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search for content using vector similarity"""
    start_time = time.time()
    
    try:
        vs, pm = get_services()
        
        if not vs:
            raise HTTPException(status_code=503, detail="Search service not available")
        
        # Create search query
        from app.services.vector_search import SearchQuery
        
        search_query = SearchQuery(
            text=request.query,
            k=request.k,
            category_filter=request.category
        )
        
        # Perform search
        results = await vs.search(search_query)
        
        # Convert to response format
        response_results = []
        for result in results:
            # Calculate time ago (mock for demo)
            time_ago = f"{abs(hash(result.id)) % 24} hours ago"
            
            response_results.append(SearchResultResponse(
                id=result.id,
                title=result.title,
                content=result.content[:200] + "..." if len(result.content) > 200 else result.content,
                category=result.category,
                tags=result.tags[:5],  # Limit tags
                author=result.author,
                score=result.score,
                time_ago=time_ago
            ))
        
        search_time_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        if pm:
            await pm.record_request(search_time_ms, success=True)
        
        return SearchResponse(
            results=response_results,
            total_results=len(response_results),
            search_time_ms=search_time_ms,
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        search_time_ms = (time.time() - start_time) * 1000
        
        # Record failed request
        if pm:
            await pm.record_request(search_time_ms, success=False)
        
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/categories")
async def get_categories():
    """Get available content categories"""
    return {
        "categories": [
            "technology",
            "tutorial", 
            "news",
            "research",
            "business",
            "design",
            "development"
        ]
    }

@router.get("/stats")
async def get_search_stats():
    """Get search statistics"""
    try:
        vs, pm = get_services()
        
        content_count = await vs.get_content_count() if vs else 0
        
        return {
            "total_content": content_count,
            "categories": 7,
            "avg_search_time_ms": 4.2,  # Mock data
            "cache_hit_rate": 0.94
        }
        
    except Exception as e:
        logger.error(f"Failed to get search stats: {e}")
        return {
            "total_content": 0,
            "categories": 0,
            "avg_search_time_ms": 0,
            "cache_hit_rate": 0
        }