"""
Configuration settings for the ImageGenAI application
"""

import os
import json
from typing import Optional, Union, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, field_serializer

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
    def parse_allowed_image_types(cls, v: Any) -> Any:
        """Parse allowed_image_types from various formats"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Strip whitespace first
            v = v.strip()
            # Remove surrounding brackets if present but malformed
            if v.startswith('[') and v.endswith(']'):
                # Try to parse as JSON
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, ValueError) as e:
                    # If JSON parsing fails, try to extract values manually
                    # Remove brackets and split by comma
                    content = v[1:-1].strip()
                    if content:
                        items = [item.strip().strip('"').strip("'") for item in content.split(',') if item.strip()]
                        if items:
                            return items
            # Try comma-separated format
            if ',' in v:
                return [item.strip().strip('"').strip("'") for item in v.split(',') if item.strip()]
            # If single value, return as list
            if v:
                return [v.strip().strip('"').strip("'")]
        return v or DEFAULT_ALLOWED_IMAGE_TYPES
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
