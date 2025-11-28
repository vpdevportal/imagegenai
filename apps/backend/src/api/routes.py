from fastapi import APIRouter
from .generate import router as generate_router
from .prompts import router as prompts_router
from .inspire import router as inspire_router
from .variations import router as variations_router
from .fusion import router as fusion_router
from .teleport import router as teleport_router

# Create main API router
api_router = APIRouter(prefix="/api", tags=["api"])

# Include all sub-routers
api_router.include_router(generate_router)
api_router.include_router(prompts_router)
api_router.include_router(inspire_router)
api_router.include_router(variations_router)
api_router.include_router(fusion_router)
api_router.include_router(teleport_router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "ImageGenAI API is running",
        "version": "1.0.0"
    }

# Root API endpoint
@api_router.get("/")
async def root():
    """Root API endpoint"""
    return {
        "message": "Welcome to ImageGenAI API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "health": "/api/health",
            "generate": "/api/generate",
            "prompts": "/api/prompts",
            "inspire": "/api/inspire",
            "variations": "/api/variations",
            "fusion": "/api/fusion",
            "teleport": "/api/teleport",
            "docs": "/api/docs"
        }
    }
