"""
Recommendations API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class RecommendationRequest(BaseModel):
    user_id: str
    diversity: float = 0.7
    k: int = 5

class RecommendationResponse(BaseModel):
    content_id: str
    title: str
    explanation: str
    confidence: float
    tags: List[str]

class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    user_id: str
    generation_time_ms: float
    strategy: str

# Sample recommendations data for demo
SAMPLE_RECOMMENDATIONS = {
    "user1": [
        {
            "content_id": "rec_1",
            "title": "Advanced Redis Caching Strategies",
            "explanation": "Based on your interest in performance optimization",
            "confidence": 0.92,
            "tags": ["redis", "caching", "performance"]
        },
        {
            "content_id": "rec_2", 
            "title": "Building Scalable Vector Databases",
            "explanation": "Similar users also viewed this content",
            "confidence": 0.88,
            "tags": ["vectors", "databases", "scaling"]
        },
        {
            "content_id": "rec_3",
            "title": "Real-time Data Processing with Streams",
            "explanation": "Trending in your technology interests",
            "confidence": 0.85,
            "tags": ["streaming", "real-time", "data"]
        }
    ],
    "user2": [
        {
            "content_id": "rec_4",
            "title": "ML Feature Stores with Redis",
            "explanation": "Matches your data science background",
            "confidence": 0.95,
            "tags": ["ml", "features", "data-science"]
        },
        {
            "content_id": "rec_5",
            "title": "Real-time Model Inference Patterns",
            "explanation": "Trending in your field this week",
            "confidence": 0.87,
            "tags": ["inference", "real-time", "models"]
        }
    ],
    "user3": [
        {
            "content_id": "rec_6",
            "title": "UI/UX Design for AI Applications",
            "explanation": "Based on your design preferences",
            "confidence": 0.90,
            "tags": ["design", "ui", "ai"]
        },
        {
            "content_id": "rec_7",
            "title": "Interactive Data Visualization",
            "explanation": "Similar designers found this valuable",
            "confidence": 0.83,
            "tags": ["visualization", "design", "data"]
        }
    ],
    "user4": [
        {
            "content_id": "rec_8",
            "title": "Startup Guide: Building AI Products",
            "explanation": "Relevant for startup founders",
            "confidence": 0.89,
            "tags": ["startup", "ai", "product"]
        },
        {
            "content_id": "rec_9",
            "title": "Scaling Technical Teams",
            "explanation": "Based on your leadership interests",
            "confidence": 0.86,
            "tags": ["leadership", "scaling", "teams"]
        }
    ]
}

@router.post("/", response_model=RecommendationsResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get personalized recommendations for a user"""
    start_time = time.time()
    
    try:
        # Simulate processing time
        await asyncio.sleep(0.5)  # Mock processing delay
        
        # Get recommendations for user (using sample data for demo)
        user_recs = SAMPLE_RECOMMENDATIONS.get(request.user_id, SAMPLE_RECOMMENDATIONS["user1"])
        
        # Apply diversity filter (mock implementation)
        selected_recs = user_recs[:request.k]
        
        # Apply diversity adjustment to scores
        for i, rec in enumerate(selected_recs):
            diversity_penalty = i * (1 - request.diversity) * 0.1
            rec["confidence"] = max(rec["confidence"] - diversity_penalty, 0.5)
        
        recommendations = [
            RecommendationResponse(**rec) for rec in selected_recs
        ]
        
        generation_time_ms = (time.time() - start_time) * 1000
        
        return RecommendationsResponse(
            recommendations=recommendations,
            user_id=request.user_id,
            generation_time_ms=generation_time_ms,
            strategy="hybrid_contextual"
        )
        
    except Exception as e:
        logger.error(f"Recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@router.get("/users")
async def get_available_users():
    """Get available demo users"""
    return {
        "users": [
            {"id": "user1", "name": "Sarah (Tech Enthusiast)", "description": "Frontend developer learning AI"},
            {"id": "user2", "name": "Mike (Data Scientist)", "description": "ML engineer with 5+ years experience"},
            {"id": "user3", "name": "Emma (Designer)", "description": "UX designer exploring AI tools"},
            {"id": "user4", "name": "Alex (Startup Founder)", "description": "Building AI-powered products"}
        ]
    }

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    return {
        "user_id": user_id,
        "total_interactions": abs(hash(user_id)) % 1000 + 100,
        "favorite_categories": ["technology", "tutorial", "research"],
        "engagement_score": 0.75 + (abs(hash(user_id)) % 25) / 100,
        "diversity_preference": 0.7
    }

import asyncio