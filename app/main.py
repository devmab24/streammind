"""
StreamMind - Real-Time AI Content Discovery Engine
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from app.services.redis_client import RedisService
from app.services.embedding_service import EmbeddingService
from app.services.vector_search import VectorSearchEngine
from app.services.personalization import PersonalizationEngine
from app.services.performance_monitor import PerformanceMonitor
from app.api.search import router as search_router
from app.api.recommendations import router as recommendations_router
from app.api.analytics import router as analytics_router
from app.utils.sample_data import load_sample_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
redis_service = None
embedding_service = None
vector_search = None
personalization_engine = None
performance_monitor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global redis_service, embedding_service, vector_search, personalization_engine, performance_monitor
    
    try:
        logger.info("🚀 Starting StreamMind services...")
        
        # Initialize Redis service
        redis_service = RedisService()
        await redis_service.initialize()
        
        # Initialize embedding service
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        # Initialize vector search
        vector_search = VectorSearchEngine(redis_service.client, embedding_service)
        await vector_search.initialize_indices()
        
        # Initialize personalization engine
        personalization_engine = PersonalizationEngine(
            redis_service.client, 
            embedding_service, 
            vector_search
        )
        await personalization_engine.initialize()
        
        # Initialize performance monitoring
        performance_monitor = PerformanceMonitor(redis_service.client)
        await performance_monitor.start_monitoring()
        
        # Load sample data if in demo mode
        if os.getenv("DEMO_MODE", "true").lower() == "true":
            await load_sample_data(redis_service.client, vector_search)
        
        logger.info("✅ All services initialized successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("🛑 Shutting down StreamMind services...")
        if performance_monitor:
            await performance_monitor.stop_monitoring()
        if redis_service:
            await redis_service.close()

# Create FastAPI app
app = FastAPI(
    title="StreamMind",
    description="Real-Time AI Content Discovery Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main demo page"""
    try:
        with open("app/static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>StreamMind</title></head>
            <body>
                <h1>StreamMind - Real-Time AI Content Discovery</h1>
                <p>Welcome to StreamMind! The demo interface is loading...</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        await redis_service.client.ping()
        
        return {
            "status": "healthy",
            "services": {
                "redis": "connected",
                "embedding": "ready" if embedding_service and embedding_service.model else "loading",
                "vector_search": "ready" if vector_search else "initializing"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/api/status")
async def get_status():
    """Get detailed system status"""
    try:
        metrics = await performance_monitor.get_current_metrics() if performance_monitor else {}
        
        return {
            "status": "running",
            "metrics": {
                "requests_processed": getattr(metrics, 'total_requests', 0),
                "cache_hit_rate": getattr(metrics, 'cache_hit_rate', {}),
                "response_time_ms": getattr(metrics, 'average_response_time_ms', 0),
                "vectors_indexed": "1.2M+",  # Mock data for demo
                "events_per_second": getattr(metrics, 'events_per_second', 0)
            },
            "services": {
                "redis": "connected",
                "vector_search": "ready",
                "personalization": "ready",
                "monitoring": "active"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )