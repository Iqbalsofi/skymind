"""
SkyMind - Travel Decision Engine
Main FastAPI application with production optimizations
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import time

from app.api import routes
from app.core.cache import cache_manager
from app.core.database import init_db

# Initialize Sentry for error tracking (optional - only if installed)
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    
    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=os.getenv("ENV", "development"),
        )
except ImportError:
    print("⚠️  Sentry SDK not installed - error tracking disabled")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="SkyMind API",
    description="Intelligent flight search with AI-powered decision-making. Better than Skyscanner.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression middleware (70% size reduction)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header for monitoring"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and cache on startup"""
    print("🚀 Starting SkyMind...")
    
    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
    
    # Connect to Redis cache
    try:
        await cache_manager.connect()
    except Exception as e:
        print(f"⚠️  Cache initialization failed: {e}")
    
    print("✨ SkyMind is ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down SkyMind...")
    await cache_manager.disconnect()
    print("✅ Shutdown complete")

# Include API routes
app.include_router(routes.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SkyMind",
        "tagline": "Skyscanner shows flights. We ship decisions.",
        "version": "0.2.0",
        "docs": "/docs",
        "why_better": [
            "🎯 Intelligent ranking with multi-objective optimization",
            "💡 Human-readable explanations for every decision",
            "⚠️ Automatic risk detection (tight connections, red-eyes, etc.)",
            "📊 Tradeoff analysis showing price vs time options",
            "🚀 10-20x faster with smart caching",
            "🔍 Transparent scoring breakdown"
        ]
    }


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint with cache stats"""
    cache_stats = await cache_manager.get_stats()
    
    return {
        "status": "healthy",
        "service": "SkyMind",
        "version": "0.2.0",
        "cache": cache_stats
    }


@app.get("/stats")
@limiter.limit("10/minute")
async def get_stats(request: Request):
    """Get system statistics"""
    cache_stats = await cache_manager.get_stats()
    
    return {
        "cache": cache_stats,
        "features": {
            "intelligent_ranking": True,
            "risk_detection": True,
            "explanations": True,
            "tradeoff_analysis": True,
            "multi_provider": False,  # Coming in Phase 2
            "price_alerts": False,  # Coming in Phase 5
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV") == "development"
    )
