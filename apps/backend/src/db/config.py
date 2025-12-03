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
    default_ai_provider: str = "gemini"  # Default provider: gemini, replicate, stability, huggingface
    
    # Additional AI Provider API Keys
    replicate_api_key: Optional[str] = None
    stability_ai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
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
        # Look for .env in root directory (../../../../.env from apps/backend/src/db/)
        # Falls back to local .env if root .env not found
        env_file=["../../../../.env", "../../../.env", "../../.env", "../.env", ".env"],
        case_sensitive=False,
        extra='ignore'  # Ignore extra fields from .env that aren't in Settings class
    )


# Global settings instance
settings = Settings()
