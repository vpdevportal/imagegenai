"""
Application Constants

This module contains all application-wide constants to avoid repetition
and make maintenance easier.
"""

# AI Model Configuration
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-image-preview"

# Application Configuration
APP_NAME = "ImageGenAI"
API_TITLE = "ImageGenAI API"
API_DESCRIPTION = "AI-powered image generation and processing API"
API_VERSION = "1.0.0"

# File Upload Configuration
DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/webp"
]

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_DEBUG = True

# CORS Configuration
DEFAULT_FRONTEND_URL = "http://localhost:5001"
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5001",
    "http://127.0.0.1:5001",
    "http://localhost:6001",
    "http://127.0.0.1:6001"
]
