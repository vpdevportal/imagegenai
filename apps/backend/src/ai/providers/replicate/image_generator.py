"""
Replicate Image Generator using FLUX.1-dev model
"""

import asyncio
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
        # Allow model name to be configured via environment variable
        # Default fallback models will be tried if the configured one fails
        self.model = os.getenv('REPLICATE_MODEL_NAME', 'black-forest-labs/flux-dev')
    
    async def generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        """Async wrapper: runs sync Replicate API in thread pool to avoid blocking the event loop."""
        return await asyncio.to_thread(self._sync_generate_from_image_and_text, image_file, prompt)

    def _sync_generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        try:
            # Read and process the uploaded image
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Replicate accepts images as file-like objects (BytesIO)
            # Reset the file pointer and use BytesIO
            image_file.file.seek(0)
            image_bytes_io = BytesIO(image_content)
            
            logger.info(f"Generating image with Replicate model {self.model}, prompt: {prompt[:100]}...")
            
            # Use Replicate API for image-to-image generation
            # Try different model names if one fails
            # Start with configured model, then try common alternatives
            model_names = [
                self.model,  # Try configured model first
                "black-forest-labs/flux-dev",
                "black-forest-labs/flux-1-dev", 
                "black-forest-labs/flux-1",
                "stability-ai/flux-dev"  # Alternative naming
            ]
            # Remove duplicates while preserving order
            model_names = list(dict.fromkeys(model_names))
            
            output = None
            last_error = None
            
            for model_name in model_names:
                try:
                    logger.info(f"Trying model: {model_name}")
                    # Replicate Python SDK accepts file-like objects
                    output = replicate.run(
                        model_name,
                        input={
                            "prompt": prompt,
                            "image": image_bytes_io,
                            "num_outputs": 1,
                            "guidance_scale": 7.5,
                            "num_inference_steps": 28,
                        }
                    )
                    # If successful, update self.model for future use
                    self.model = model_name
                    logger.info(f"Successfully used model: {model_name}")
                    break
                except Exception as model_error:
                    last_error = model_error
                    error_str = str(model_error)
                    logger.warning(f"Model {model_name} failed: {error_str}")
                    if "404" not in error_str and "not found" not in error_str.lower():
                        # If it's not a 404/not found, don't try other models
                        raise
                    continue
            
            if output is None:
                error_msg = f"All model names failed. Last error: {str(last_error)}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=500,
                    detail=f"Replicate model not found. Please check the model name. Error: {str(last_error)}"
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
    
    async def generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        """Async wrapper: runs sync Replicate API in thread pool to avoid blocking the event loop."""
        return await asyncio.to_thread(self._sync_generate_from_text, prompt)

    def _sync_generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
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
    
    async def generate_from_multiple_images_and_text(self, image_files: list, prompt: str) -> Tuple[bytes, str]:
        """Async wrapper. Replicate FLUX uses first image only."""
        if not image_files or len(image_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one image file is required"
            )
        return await self.generate_from_image_and_text(image_files[0], prompt)

