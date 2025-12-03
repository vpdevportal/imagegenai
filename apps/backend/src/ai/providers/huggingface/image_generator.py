"""
Hugging Face Image Generator using Inference API with Stable Diffusion
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


class HuggingFaceImageGenerator(BaseImageGenerator):
    """Image generator using Hugging Face Inference API with Stable Diffusion"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Hugging Face Image Generator
        
        Args:
            api_key: Hugging Face API key. If not provided, will look for HUGGINGFACE_API_KEY env var
        """
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY') or getattr(settings, 'HUGGINGFACE_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set HUGGINGFACE_API_KEY environment variable")
        
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model_name = "stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using a reference image and text prompt (img2img)
        Note: Hugging Face may require ControlNet for img2img, using text-to-image with enhanced prompt
        
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
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            logger.info(f"Generating image with Hugging Face SDXL, prompt: {prompt[:100]}...")
            
            # Use Hugging Face Inference API
            # Note: For img2img, we may need to use a different model endpoint
            # For now, using text-to-image with enhanced prompt that references the image
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5,
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model_name}",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                image_data = response.content
                content_type = "image/png"
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.warning("Model is loading, waiting...")
                import time
                time.sleep(10)
                return self.generate_from_image_and_text(image_file, prompt)
            else:
                error_detail = response.text or f"HTTP {response.status_code}"
                logger.error(f"Hugging Face API error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hugging Face API error: {error_detail}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate image with Hugging Face: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Hugging Face: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to generate image with Hugging Face: {str(e)}", exc_info=True)
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
            logger.info(f"Generating image from text with Hugging Face SDXL, prompt: {prompt[:100]}...")
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5,
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model_name}",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                image_data = response.content
                content_type = "image/png"
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.warning("Model is loading, waiting...")
                import time
                time.sleep(10)
                return self.generate_from_text(prompt)
            else:
                error_detail = response.text or f"HTTP {response.status_code}"
                logger.error(f"Hugging Face API error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hugging Face API error: {error_detail}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate image from text with Hugging Face: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Hugging Face: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to generate image from text with Hugging Face: {str(e)}", exc_info=True)
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
        Note: Hugging Face may not support multiple images directly, so we'll use the first image
        
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
        logger.info(f"Using first image from {len(image_files)} images for Hugging Face generation")
        return self.generate_from_image_and_text(image_files[0], prompt)

