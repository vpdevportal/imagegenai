"""
Configuration settings for the ImageGenAI application
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "ImageGenAI API"
    api_description: str = "AI-powered image generation and processing API"
    api_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    frontend_url: str = "http://localhost:3000"
    allowed_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # AI Configuration
    google_ai_api_key: Optional[str] = None
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: list = [
        "image/jpeg",
        "image/jpg", 
        "image/png",
        "image/webp"
    ]
    
    # Generated Images Configuration
    generated_images_dir: str = "generated_images"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
