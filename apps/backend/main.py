from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="ImageGenAI API",
    description="AI-powered image generation and processing API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ImageGenAI API is running"}

# API routes
@app.get("/api/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ImageGenAI API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Image generation endpoints (placeholder)
from pydantic import BaseModel

class ImageGenerationRequest(BaseModel):
    prompt: str

@app.post("/api/generate")
async def generate_image(request: ImageGenerationRequest):
    """Generate image from text prompt"""
    # TODO: Implement AI image generation
    return {
        "message": "Image generation endpoint",
        "prompt": request.prompt,
        "status": "pending",
        "generated_image_url": None
    }

@app.get("/api/images")
async def list_images():
    """List all generated images"""
    # TODO: Implement image listing
    return {
        "images": [],
        "total": 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
