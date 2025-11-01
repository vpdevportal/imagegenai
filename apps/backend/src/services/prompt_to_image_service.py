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
from .prompt_service import prompt_service
from ..db.config import settings

logger = logging.getLogger(__name__)


class PromptToImageService:
    """Service for handling prompt to image generation business logic"""
    
    def __init__(self):
        self.generator = prompt_to_image_generator
        self.prompt_service = prompt_service
        logger.info("Prompt to image service initialized")
    
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
        logger.info(f"Starting prompt to image generation - prompt_length: {len(prompt)}, reference_image_filename: {reference_image.filename}, reference_image_size: {reference_image.size if hasattr(reference_image, 'size') else 'unknown'}")
        
        try:
            # Process reference image and get data URL
            logger.debug("Processing reference image")
            reference_image_url = self.generator.process_reference_image(reference_image)
            logger.info(f"Reference image processed successfully - url_length: {len(reference_image_url) if reference_image_url else 0}")
            
            # Generate the actual image using AI
            logger.info("Starting AI image generation")
            generated_image_data, content_type = self.generator.generate_from_image_and_text(
                reference_image, prompt
            )
            logger.info(f"AI image generation completed - generated_size: {len(generated_image_data)} bytes, content_type: {content_type}")
            
            logger.info("Prompt to image generation completed successfully")
            return generated_image_data, content_type, reference_image_url
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            
            # Track failure for the prompt
            logger.info(f"Tracking failure for prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
            self.prompt_service.track_failure(prompt)
            
            raise e


# Global service instance
prompt_to_image_service = PromptToImageService()
