"""
Stability AI Image Generator using Stable Diffusion 3 img2img
"""

import os
from typing import Optional, Tuple
from io import BytesIO
import base64
import logging
import requests

from PIL import Image
from fastapi import HTTPException, UploadFile

from ...base.base_image_generator import BaseImageGenerator
from ....db.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class StabilityImageGenerator(BaseImageGenerator):
    """Image generator using Stability AI API with Stable Diffusion 3"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Stability AI Image Generator
        
        Args:
            api_key: Stability AI API key. If not provided, will look for STABILITY_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('STABILITY_AI_API_KEY') or getattr(settings, 'STABILITY_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set STABILITY_AI_API_KEY environment variable")
        
        self.base_url = "https://api.stability.ai/v2beta/stable-image"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
    
    def generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using a reference image and text prompt (img2img)
        
        Args:
            image_file: Uploaded image file (mandatory)
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Read image content
            image_content = image_file.file.read()
            image_file.file.seek(0)
            
            logger.info(f"Generating image with Stability AI SD3, prompt: {prompt[:100]}...")
            
            # Use Stability AI img2img endpoint
            files = {
                "image": (image_file.filename or "image.png", image_content, "image/png")
            }
            data = {
                "prompt": prompt,
                "mode": "image-to-image",
                "strength": 0.7,
                "seed": 0,
            }
            
            response = requests.post(
                f"{self.base_url}/edit",
                headers=self.headers,
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                image_data = response.content
                content_type = response.headers.get("Content-Type", "image/png")
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                error_detail = response.text or f"HTTP {response.status_code}"
                logger.error(f"Stability AI API error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Stability AI API error: {error_detail}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate image with Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Stability AI: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to generate image with Stability AI: {str(e)}", exc_info=True)
            error_message = "Image generation failed. Please try again later."
            
            if "401" in str(e) or "authentication" in str(e).lower():
                error_message = "Authentication failed. Please check your API key."
            elif "429" in str(e) or "rate limit" in str(e).lower():
                error_message = "Rate limit exceeded. Please try again later."
            
            raise HTTPException(
                status_code=500,
                detail=error_message
            )
    
    def generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using only text prompt (text-to-image)
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            logger.info(f"Generating image from text with Stability AI SD3, prompt: {prompt[:100]}...")
            
            data = {
                "prompt": prompt,
                "output_format": "png",
            }
            
            response = requests.post(
                f"{self.base_url}/generate/stable-diffusion-xl-1024-v1-0",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                image_data = response.content
                content_type = "image/png"
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                error_detail = response.text or f"HTTP {response.status_code}"
                logger.error(f"Stability AI API error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Stability AI API error: {error_detail}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate image from text with Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Stability AI: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to generate image from text with Stability AI: {str(e)}", exc_info=True)
            error_message = "Image generation failed. Please try again later."
            
            if "401" in str(e) or "authentication" in str(e).lower():
                error_message = "Authentication failed. Please check your API key."
            elif "429" in str(e) or "rate limit" in str(e).lower():
                error_message = "Rate limit exceeded. Please try again later."
            
            raise HTTPException(
                status_code=500,
                detail=error_message
            )
    
    def generate_from_multiple_images_and_text(self, image_files: list, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using multiple reference images and text prompt
        Note: Stability AI may not support multiple images directly, so we'll use the first image
        
        Args:
            image_files: List of uploaded image files (mandatory)
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        if not image_files or len(image_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one image file is required"
            )
        
        # Use the first image for now
        logger.info(f"Using first image from {len(image_files)} images for Stability AI generation")
        return self.generate_from_image_and_text(image_files[0], prompt)

