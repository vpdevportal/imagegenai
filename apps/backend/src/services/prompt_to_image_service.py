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

from ..ai.prompt_to_image_generator import get_prompt_to_image_generator
from .prompt_service import prompt_service

logger = logging.getLogger(__name__)


class PromptToImageService:
    """Service for handling prompt to image generation business logic"""
    
    def __init__(self):
        self.generator = get_prompt_to_image_generator()
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
        try:
            # Process reference image and get data URL
            reference_image_url = self.generator.process_reference_image(reference_image)
            
            # Generate the actual image using AI
            generated_image_data, content_type = self.generator.generate_from_image_and_text(
                reference_image, prompt
            )
            
            # Save prompt to database with thumbnail
            try:
                # Create temporary file for the generated image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(generated_image_data)
                    temp_file_path = temp_file.name
                
                # Save to database
                prompt_record = self.prompt_service.create_or_update_prompt(
                    prompt_text=prompt,
                    model="gemini-2.5-flash-image-preview",
                    image_path=temp_file_path
                )
                
                logger.info(f"Saved prompt to database: ID={prompt_record.id}, uses={prompt_record.total_uses}")
                
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
            except Exception as db_error:
                logger.error(f"Failed to save prompt to database: {db_error}")
                # Continue with response even if database save fails
            
            return generated_image_data, content_type, reference_image_url
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )


# Global service instance
prompt_to_image_service = PromptToImageService()
