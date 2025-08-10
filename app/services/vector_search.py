"""
Vector Search Engine - Simplified version for deployment
"""

import asyncio
import json
import numpy as np
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result item"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    author: str
    score: float
    distance: float
    created_at: datetime

@dataclass
class SearchQuery:
    """Search query parameters"""
    text: str
    vector: Optional[List[float]] = None
    k: int = 10
    category_filter: Optional[str] = None

class VectorSearchEngine:
    """Simplified vector search engine"""
    
    def __init__(self, redis_client, embedding_service):
        self.redis = redis_client
        self.embedding_service = embedding_service
        self.content_index = "content_vectors"
        
    async def initialize_indices(self):
        """Initialize search indices"""
        try:
            # Try to create index - will fail if already exists (which is fine)
            try:
                # Create a simple hash-based index for demo
                logger.info("Initializing vector search indices...")
                # In a real implementation, this would create Redis Search indices
                # For now, we'll use a simplified approach
                logger.info("✅ Vector search indices ready")
            except Exception as e:
                logger.info(f"Index already exists or creation failed: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize indices: {e}")
    
    async def index_content(self, content_id: str, content_data: Dict[str, Any]) -> bool:
        """Index content for search"""
        try:
            # Generate embedding if not provided
            if "embedding" not in content_data:
                text_to_embed = f"{content_data.get('title', '')} {content_data.get('content', '')}"
                embedding = await self.embedding_service.generate_embedding(text_to_embed)
                content_data["embedding"] = embedding
            
            # Store in Redis
            key = f"content:{content_id}"
            
            # Prepare data for storage
            redis_data = {
                "id": content_id,
                "title": content_data.get("title", ""),
                "content": content_data.get("content", ""),
                "category": content_data.get("category", ""),
                "tags": ",".join(content_data.get("tags", [])),
                "author": content_data.get("author", ""),
                "created_at": int(content_data.get("created_at", datetime.utcnow()).timestamp()),
                "embedding": json.dumps(content_data["embedding"]),
                "metadata": json.dumps(content_data.get("metadata", {}))
            }
            
            # Store in Redis hash
            await self.redis.hset(key, mapping=redis_data)
            
            # Add to content list for search
            await self.redis.sadd("content_ids", content_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index content {content_id}: {e}")
            return False
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform search (simplified implementation)"""
        start_time = time.time()
        
        try:
            # Generate query vector if not provided
            if query.vector is None:
                query.vector = await self.embedding_service.generate_embedding(query.text)
            
            # Get all content IDs
            content_ids = await self.redis.smembers("content_ids")
            
            if not content_ids:
                return []
            
            # Calculate similarities for all content
            results = []
            for content_id_bytes in content_ids:
                content_id = content_id_bytes.decode() if isinstance(content_id_bytes, bytes) else content_id_bytes
                
                try:
                    # Get content data
                    content_data = await self.redis.hgetall(f"content:{content_id}")
                    
                    if not content_data:
                        continue
                    
                    # Decode data
                    content_info = {}
                    for k, v in content_data.items():
                        key = k.decode() if isinstance(k, bytes) else k
                        value = v.decode() if isinstance(v, bytes) else v
                        content_info[key] = value
                    
                    # Parse embedding
                    try:
                        content_embedding = json.loads(content_info.get("embedding", "[]"))
                        if not content_embedding:
                            continue
                    except:
                        continue
                    
                    # Calculate similarity
                    similarity = self.embedding_service.cosine_similarity(query.vector, content_embedding)
                    distance = 1 - similarity
                    
                    # Apply category filter
                    if query.category_filter and content_info.get("category") != query.category_filter:
                        continue
                    
                    # Create result
                    result = SearchResult(
                        id=content_id,
                        title=content_info.get("title", ""),
                        content=content_info.get("content", ""),
                        category=content_info.get("category", ""),
                        tags=content_info.get("tags", "").split(",") if content_info.get("tags") else [],
                        author=content_info.get("author", ""),
                        score=similarity,
                        distance=distance,
                        created_at=datetime.fromtimestamp(int(content_info.get("created_at", 0)))
                    )
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Error processing content {content_id}: {e}")
                    continue
            
            # Sort by similarity score
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Return top k results
            return results[:query.k]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_content_count(self) -> int:
        """Get total number of indexed content items"""
        try:
            return await self.redis.scard("content_ids")
        except:
            return 0