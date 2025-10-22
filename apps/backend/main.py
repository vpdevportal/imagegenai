from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from src.api.routes import api_router
from src.db.config import settings

# Custom formatter to shorten logger names to last 10 characters
class ShortNameFormatter(logging.Formatter):
    def format(self, record):
        # Truncate or pad logger name to exactly 20 characters
        if hasattr(record, 'name') and record.name:
            if len(record.name) > 20:
                record.name = record.name[-20:]  # Take last 20 characters
            else:
                record.name = record.name.ljust(20)  # Pad with spaces to 20 characters
        return super().format(record)

# Configure logging
formatter = ShortNameFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create handlers
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler('imagegenai.log')
file_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[stream_handler, file_handler]
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + [settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
