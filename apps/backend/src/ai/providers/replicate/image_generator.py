"""
Replicate Image Generator using FLUX.1-dev model
"""

import os
from typing import Optional, Tuple
from io import BytesIO
import base64
import logging

import replicate
from PIL import Image
from fastapi import HTTPException, UploadFile

from ...base.base_image_generator import BaseImageGenerator
from ....db.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class ReplicateImageGenerator(BaseImageGenerator):
    """Image generator using Replicate API with FLUX.1-dev model"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Replicate Image Generator
        
        Args:
            api_key: Replicate API key. If not provided, will look for REPLICATE_API_KEY env var
        """
        self.api_key = api_key or os.getenv('REPLICATE_API_KEY') or getattr(settings, 'REPLICATE_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set REPLICATE_API_KEY environment variable")
        
        # Set the API token for replicate client
        os.environ['REPLICATE_API_TOKEN'] = self.api_key
        self.model = "black-forest-labs/flux-1-dev"  # FLUX.1-dev for image-to-image
    
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
            # Read and process the uploaded image
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Convert image to base64 for Replicate API
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            image_data_url = f"data:image/png;base64,{image_base64}"
            
            logger.info(f"Generating image with Replicate FLUX.1-dev, prompt: {prompt[:100]}...")
            
            # Use Replicate API for image-to-image generation
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "image": image_data_url,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 28,
                }
            )
            
            # Replicate returns a list of URLs or file paths
            if isinstance(output, list) and len(output) > 0:
                image_url = output[0]
                
                # Download the image from URL
                import requests
                response = requests.get(image_url)
                response.raise_for_status()
                
                image_data = response.content
                content_type = "image/png"  # Replicate typically returns PNG
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Replicate API returned no image output"
                )
                
        except Exception as e:
            logger.error(f"Failed to generate image with Replicate: {str(e)}", exc_info=True)
            error_message = "Image generation failed. Please try again later."
            
            if "401" in str(e) or "authentication" in str(e).lower():
                error_message = "Authentication failed. Please check your API key."
            elif "429" in str(e) or "rate limit" in str(e).lower():
                error_message = "Rate limit exceeded. Please try again later."
            elif "400" in str(e):
                error_message = "Invalid request. Please check your input."
            
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
            logger.info(f"Generating image from text with Replicate FLUX.1-dev, prompt: {prompt[:100]}...")
            
            # Use Replicate API for text-to-image generation
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 28,
                }
            )
            
            # Replicate returns a list of URLs or file paths
            if isinstance(output, list) and len(output) > 0:
                image_url = output[0]
                
                # Download the image from URL
                import requests
                response = requests.get(image_url)
                response.raise_for_status()
                
                image_data = response.content
                content_type = "image/png"
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Replicate API returned no image output"
                )
                
        except Exception as e:
            logger.error(f"Failed to generate image from text with Replicate: {str(e)}", exc_info=True)
            error_message = "Image generation failed. Please try again later."
            
            if "401" in str(e) or "authentication" in str(e).lower():
                error_message = "Authentication failed. Please check your API key."
            elif "429" in str(e) or "rate limit" in str(e).lower():
                error_message = "Rate limit exceeded. Please try again later."
            elif "400" in str(e):
                error_message = "Invalid request. Please check your input."
            
            raise HTTPException(
                status_code=500,
                detail=error_message
            )
    
    def generate_from_multiple_images_and_text(self, image_files: list, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using multiple reference images and text prompt
        Note: Replicate FLUX may not support multiple images directly, so we'll use the first image
        
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
        
        # Use the first image for now (Replicate FLUX may not support multiple images)
        logger.info(f"Using first image from {len(image_files)} images for Replicate generation")
        return self.generate_from_image_and_text(image_files[0], prompt)

