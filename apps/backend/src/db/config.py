"""
Configuration settings for the ImageGenAI application
"""

import os
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


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
    allowed_origins: Union[list, str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:6001",
        "http://127.0.0.1:6001"
    ]
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
