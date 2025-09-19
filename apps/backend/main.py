from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from src.api.routes import api_router
from src.db.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('imagegenai.log')
    ]
)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

logger = logging.getLogger(__name__)
logger.info("Starting ImageGenAI FastAPI application")

# Configure CORS
cors_origins = settings.allowed_origins + [settings.frontend_url]
logger.info(f"CORS allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "ImageGenAI API is running"}

# No longer mounting static files since we use in-memory image processing

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_dirs=["src"],
        log_level="info"
    )
