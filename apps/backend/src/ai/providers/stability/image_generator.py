"""
Stability AI Image Generator using Stable Diffusion img2img
"""

import asyncio
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
    """Image generator using Stability AI API with Stable Diffusion"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Stability AI Image Generator
        
        Args:
            api_key: Stability AI API key. If not provided, will look for STABILITY_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('STABILITY_AI_API_KEY') or getattr(settings, 'STABILITY_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set STABILITY_AI_API_KEY environment variable")
        
        # Stability AI v1 API base URL
        self.base_url = "https://api.stability.ai/v1/generation"
        # Default engine for image-to-image
        self.engine = os.getenv('STABILITY_AI_ENGINE', 'stable-diffusion-xl-1024-v1-0')
        
        # Headers for v1 API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/png"  # v1 API requires specific Accept header
        }
    
    def _resize_image_to_allowed_dimensions(self, image_content: bytes) -> bytes:
        """
        Resize image to one of the allowed dimensions for SDXL v1 models.
        Allowed dimensions: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 
                           640x1536, 768x1344, 832x1216, 896x1152
        
        Args:
            image_content: Original image bytes
            
        Returns:
            bytes: Resized image bytes
        """
        from io import BytesIO
        
        # Allowed dimensions for SDXL v1 models
        ALLOWED_DIMENSIONS = [
            (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640),
            (640, 1536), (768, 1344), (832, 1216), (896, 1152)
        ]
        
        try:
            # Open image
            img = Image.open(BytesIO(image_content))
            original_width, original_height = img.size
            original_aspect = original_width / original_height
            
            logger.info(f"Original image dimensions: {original_width}x{original_height}")
            
            # Find the closest allowed dimension that maintains aspect ratio
            best_dimension = None
            min_aspect_diff = float('inf')
            
            for width, height in ALLOWED_DIMENSIONS:
                aspect = width / height
                aspect_diff = abs(aspect - original_aspect)
                
                if aspect_diff < min_aspect_diff:
                    min_aspect_diff = aspect_diff
                    best_dimension = (width, height)
            
            target_width, target_height = best_dimension
            
            # Resize image maintaining aspect ratio, then crop/pad to exact dimensions
            # First, resize to fit within target dimensions
            if original_aspect > target_width / target_height:
                # Image is wider - fit to width
                new_width = target_width
                new_height = int(target_width / original_aspect)
            else:
                # Image is taller - fit to height
                new_height = target_height
                new_width = int(target_height * original_aspect)
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with target dimensions and paste resized image
            final_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # Center the resized image
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            final_img.paste(resized_img, (paste_x, paste_y))
            
            # Convert to bytes
            output = BytesIO()
            final_img.save(output, format='PNG')
            output.seek(0)
            
            logger.info(f"Resized image to {target_width}x{target_height} (closest match to {original_width}x{original_height})")
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Failed to resize image, using original: {str(e)}")
            return image_content
    
    async def generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        """Async wrapper: runs sync Stability API in thread pool to avoid blocking the event loop."""
        return await asyncio.to_thread(self._sync_generate_from_image_and_text, image_file, prompt)

    def _sync_generate_from_image_and_text(self, image_file: UploadFile, prompt: str) -> Tuple[bytes, str]:
        try:
            # Read image content
            image_content = image_file.file.read()
            image_file.file.seek(0)
            
            # Resize image to allowed dimensions for SDXL v1 models
            image_content = self._resize_image_to_allowed_dimensions(image_content)
            
            logger.info(f"Generating image with Stability AI {self.engine}, prompt: {prompt[:100]}...")
            
            # Stability AI v1 API endpoint for image-to-image
            endpoint = f"{self.base_url}/{self.engine}/image-to-image"
            
            # Prepare multipart/form-data request
            files = {
                "init_image": (image_file.filename or "image.png", image_content, "image/png")
            }
            
            # Form data parameters for v1 API
            data = {
                "text_prompts[0][text]": prompt,
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": 0.7,  # How much the init_image influences the result (0.0 to 1.0)
                "cfg_scale": 7,  # How strictly the AI adheres to the prompt (0 to 35)
                "samples": 1,  # Number of images to generate
                "steps": 30  # Number of diffusion steps
            }
            
            logger.info(f"Calling Stability AI endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                headers=self.headers,
                files=files,
                data=data,
                timeout=120  # Image generation can take time
            )
            
            if response.status_code == 200:
                # v1 API returns image bytes directly when Accept: image/png
                image_data = response.content
                content_type = response.headers.get("Content-Type", "image/png")
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                # Handle errors
                error_detail = response.text[:1000] if response.text else f"HTTP {response.status_code}"
                logger.error(f"Stability AI API error ({response.status_code}): {error_detail}")
                
                # Provide helpful error messages
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication failed. Please check your Stability AI API key."
                    )
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Engine '{self.engine}' not found. Available engines may have changed. Error: {error_detail}"
                    )
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid request parameters. Error: {error_detail}"
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Stability AI API error: {error_detail}"
                    )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Stability AI: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPExceptions as-is (they already have proper status codes and messages)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to Stability AI. Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to generate image with Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Image generation failed. Please try again later."
            )
    
    async def generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        """Async wrapper: runs sync Stability API in thread pool to avoid blocking the event loop."""
        return await asyncio.to_thread(self._sync_generate_from_text, prompt)

    def _sync_generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        try:
            logger.info(f"Generating image from text with Stability AI {self.engine}, prompt: {prompt[:100]}...")
            
            # Stability AI v1 API endpoint for text-to-image
            endpoint = f"{self.base_url}/{self.engine}/text-to-image"
            
            # Form data parameters for v1 API
            data = {
                "text_prompts[0][text]": prompt,
                "cfg_scale": 7,
                "samples": 1,
                "steps": 30,
                "width": 1024,
                "height": 1024
            }
            
            logger.info(f"Calling Stability AI endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                # v1 API returns image bytes directly when Accept: image/png
                image_data = response.content
                content_type = response.headers.get("Content-Type", "image/png")
                
                logger.info(f"Image generated successfully: {len(image_data)} bytes")
                return image_data, content_type
            else:
                error_detail = response.text[:1000] if response.text else f"HTTP {response.status_code}"
                logger.error(f"Stability AI API error ({response.status_code}): {error_detail}")
                
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication failed. Please check your Stability AI API key."
                    )
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Engine '{self.engine}' not found. Error: {error_detail}"
                    )
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid request parameters. Error: {error_detail}"
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Stability AI API error: {error_detail}"
                    )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Stability AI: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate image from text with Stability AI: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
    
    async def generate_from_multiple_images_and_text(self, image_files: list, prompt: str) -> Tuple[bytes, str]:
        """Stability AI v1 uses first image only."""
        if not image_files or len(image_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one image file is required"
            )
        return await self.generate_from_image_and_text(image_files[0], prompt)
