"""
Configuration settings for the ImageGenAI application
"""

import os
from typing import Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

from ..constants import (
    DEFAULT_GEMINI_MODEL,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_DEBUG,
    DEFAULT_FRONTEND_URL,
    DEFAULT_ALLOWED_ORIGINS,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_ALLOWED_IMAGE_TYPES
)


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = API_TITLE
    api_description: str = API_DESCRIPTION
    api_version: str = API_VERSION
    
    # Server Configuration
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    debug: bool = DEFAULT_DEBUG
    
    # CORS Configuration
    frontend_url: str = DEFAULT_FRONTEND_URL
    allowed_origins: Union[list, str] = DEFAULT_ALLOWED_ORIGINS
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # AI Configuration
    google_ai_api_key: Optional[str] = None
    gemini_model: str = DEFAULT_GEMINI_MODEL
    
    # File Upload Configuration
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    allowed_image_types: Union[list, str] = DEFAULT_ALLOWED_IMAGE_TYPES
    
    @field_validator('allowed_image_types', mode='before')
    @classmethod
    def parse_allowed_image_types(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
