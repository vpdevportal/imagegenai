"""
Prompt to Image Service

Service layer that handles business logic for image generation from prompts.
Uses the AI generator classes for the actual AI operations.
"""

import logging
import tempfile
import os
from typing import Tuple
from fastapi import HTTPException, UploadFile

from ..ai.prompt_to_image_generator import prompt_to_image_generator
from ..ai.prompt_generator import prompt_generator
from .prompt_service import prompt_service
from ..db.config import settings

logger = logging.getLogger(__name__)


class PromptToImageService:
    """Service for handling prompt to image generation business logic"""
    
    def __init__(self):
        self.generator = prompt_to_image_generator
        self.prompt_service = prompt_service
    
    async def generate_image_from_prompt(
        self, 
        prompt: str, 
        reference_image: UploadFile
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image from a text prompt and reference image
        
        Args:
            prompt: Text prompt for image generation
            reference_image: Uploaded reference image file
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            reference_image_url = self.generator.process_reference_image(reference_image)
            generated_image_data, content_type = self.generator.generate_from_image_and_text(
                reference_image, prompt
            )
            return generated_image_data, content_type, reference_image_url
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise e
    
    async def generate_fusion_from_images(
        self, 
        image1: UploadFile,
        image2: UploadFile
    ) -> Tuple[bytes, str, str]:
        """
        Generate a fusion image from two reference images
        
        Args:
            image1: First uploaded image file
            image2: Second uploaded image file
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Process first image as reference image URL (for response)
            reference_image_url = self.generator.process_reference_image(image1)
            
            # Reset file pointers
            image1.file.seek(0)
            image2.file.seek(0)
            
            # Generate fusion using multiple images
            generated_image_data, content_type = self.generator.generate_from_multiple_images_and_text(
                [image1, image2], 
                prompt_generator.fusion_prompt()
            )
            return generated_image_data, content_type, reference_image_url
            
        except Exception as e:
            logger.error(f"Fusion generation failed: {str(e)}", exc_info=True)
            raise e


# Global service instance
prompt_to_image_service = PromptToImageService()
