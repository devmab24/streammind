"""
Sample data loader for demo purposes
"""

import asyncio
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

SAMPLE_CONTENT = [
    {
        "id": "content_1",
        "title": "Advanced Vector Search with Redis",
        "content": "Learn how to implement high-performance vector search using Redis Stack with real-time indexing and semantic similarity matching. This comprehensive guide covers HNSW algorithms, optimization techniques, and best practices for production deployments.",
        "category": "technology",
        "tags": ["redis", "vector-search", "database", "performance"],
        "author": "Redis Labs",
        "created_at": datetime.utcnow() - timedelta(hours=2)
    },
    {
        "id": "content_2", 
        "title": "Building Real-time AI Applications",
        "content": "A comprehensive guide to creating responsive AI applications with streaming data processing and instant user feedback. Covers architecture patterns, performance optimization, and scalability considerations.",
        "category": "tutorial",
        "tags": ["ai", "real-time", "streaming", "architecture"],
        "author": "AI Weekly",
        "created_at": datetime.utcnow() - timedelta(hours=5)
    },
    {
        "id": "content_3",
        "title": "Machine Learning in Production: Redis Integration",
        "content": "Best practices for deploying ML models with Redis as a feature store and real-time inference cache. Learn about model serving, feature engineering, and monitoring strategies.",
        "category": "research",
        "tags": ["machine-learning", "production", "redis", "feature-store"],
        "author": "MLOps Community",
        "created_at": datetime.utcnow() - timedelta(days=1)
    },
    {
        "id": "content_4",
        "title": "Semantic Caching for LLM Optimization",
        "content": "Revolutionary approach to reducing LLM API costs through intelligent semantic caching. Achieve 90% cost reduction while maintaining response quality through vector similarity matching.",
        "category": "technology",
        "tags": ["llm", "caching", "optimization", "cost-reduction"],
        "author": "OpenAI Research",
        "created_at": datetime.utcnow() - timedelta(hours=8)
    },
    {
        "id": "content_5",
        "title": "Real-time Feature Streaming Architecture",
        "content": "Design patterns for processing user interactions in real-time to update ML features instantly. Covers Redis Streams, event sourcing, and feature pipeline optimization.",
        "category": "tutorial",
        "tags": ["streaming", "features", "real-time", "architecture"],
        "author": "Data Engineering Weekly",
        "created_at": datetime.utcnow() - timedelta(hours=12)
    },
    {
        "id": "content_6",
        "title": "Personalization at Scale: Multi-Strategy Recommendations",
        "content": "Advanced personalization techniques combining collaborative filtering, content-based filtering, and contextual awareness for superior user experience.",
        "category": "research",
        "tags": ["personalization", "recommendations", "ml", "user-experience"],
        "author": "Netflix Tech Blog",
        "created_at": datetime.utcnow() - timedelta(hours=18)
    },
    {
        "id": "content_7",
        "title": "Redis Streams for Event-Driven Architecture",
        "content": "Comprehensive guide to using Redis Streams for building robust event-driven systems. Covers consumer groups, message processing, and fault tolerance patterns.",
        "category": "technology",
        "tags": ["redis", "streams", "event-driven", "architecture"],
        "author": "Redis University",
        "created_at": datetime.utcnow() - timedelta(days=2)
    },
    {
        "id": "content_8",
        "title": "Performance Optimization for AI Applications",
        "content": "Deep dive into performance optimization techniques for AI-powered applications. Covers caching strategies, request batching, and system monitoring.",
        "category": "tutorial",
        "tags": ["performance", "optimization", "ai", "monitoring"],
        "author": "Performance Weekly",
        "created_at": datetime.utcnow() - timedelta(hours=6)
    },
    {
        "id": "content_9",
        "title": "Contextual AI: Beyond Simple Recommendations",
        "content": "Explore how contextual awareness transforms AI recommendations. Learn about time-based preferences, location awareness, and behavioral adaptation.",
        "category": "research",
        "tags": ["contextual-ai", "recommendations", "behavior", "adaptation"],
        "author": "AI Research Institute",
        "created_at": datetime.utcnow() - timedelta(hours=14)
    },
    {
        "id": "content_10",
        "title": "Building Scalable Vector Databases",
        "content": "Architecture patterns and best practices for building vector databases that scale to billions of embeddings while maintaining sub-millisecond query performance.",
        "category": "technology",
        "tags": ["vector-database", "scaling", "performance", "embeddings"],
        "author": "Database Weekly",
        "created_at": datetime.utcnow() - timedelta(hours=20)
    }
]

async def load_sample_data(redis_client, vector_search_engine):
    """Load sample content data for demo"""
    try:
        logger.info("Loading sample data...")
        
        # Check if data already exists
        content_count = await vector_search_engine.get_content_count()
        if content_count > 0:
            logger.info(f"Sample data already loaded ({content_count} items)")
            return
        
        # Load content items
        successful_loads = 0
        
        for content_item in SAMPLE_CONTENT:
            try:
                success = await vector_search_engine.index_content(
                    content_item["id"], 
                    content_item
                )
                if success:
                    successful_loads += 1
                    
            except Exception as e:
                logger.error(f"Failed to load content {content_item['id']}: {e}")
        
        logger.info(f"✅ Loaded {successful_loads}/{len(SAMPLE_CONTENT)} sample content items")
        
        # Add some additional mock data for demo metrics
        await _add_demo_metrics(redis_client)
        
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")

async def _add_demo_metrics(redis_client):
    """Add demo metrics for dashboard"""
    try:
        # Add some performance metrics
        metrics_data = {
            "total_requests": "1250000",
            "cache_hit_rate": "0.942",
            "avg_response_time": "4.3",
            "vectors_indexed": "1200000",
            "active_users": "8439"
        }
        
        await redis_client.hset("demo:metrics", mapping=metrics_data)
        
        # Add some user interaction data
        for i in range(100):
            interaction_data = {
                "user_id": f"user_{i % 10}",
                "content_id": f"content_{i % len(SAMPLE_CONTENT) + 1}",
                "event_type": ["view", "like", "share"][i % 3],
                "timestamp": str(int((datetime.utcnow() - timedelta(minutes=i)).timestamp() * 1000))
            }
            
            await redis_client.xadd("demo:interactions", interaction_data, maxlen=1000)
        
        logger.info("✅ Demo metrics loaded")
        
    except Exception as e:
        logger.error(f"Failed to load demo metrics: {e}")

async def get_sample_content_by_category(category: str = None):
    """Get sample content filtered by category"""
    if category:
        return [item for item in SAMPLE_CONTENT if item["category"] == category]
    return SAMPLE_CONTENT