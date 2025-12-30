"""
Prompt to Image Service

Service layer that handles business logic for image generation from prompts.
Uses the AI generator classes for the actual AI operations.
"""

import logging
import tempfile
import os
from typing import Tuple, Optional, List
from fastapi import HTTPException, UploadFile

from ..ai.factory import ImageGeneratorFactory
from ..ai.prompt_generator import prompt_generator
from .prompt_service import prompt_service
from ..db.config import settings

logger = logging.getLogger(__name__)


class PromptToImageService:
    """Service for handling prompt to image generation business logic"""
    
    def __init__(self):
        self.prompt_service = prompt_service
    
    def _get_generator(self, provider: Optional[str] = None):
        """
        Get the appropriate generator instance based on provider
        
        Args:
            provider: Provider name (defaults to gemini if not specified)
            
        Returns:
            BaseImageGenerator: Generator instance
        """
        provider = provider or getattr(settings, 'default_ai_provider', 'gemini')
        return ImageGeneratorFactory.create(provider)
    
    async def generate_image_from_prompt(
        self, 
        prompt: str, 
        reference_image: UploadFile,
        provider: Optional[str] = None
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image from a text prompt and reference image
        
        Args:
            prompt: Text prompt for image generation
            reference_image: Uploaded reference image file
            provider: AI provider to use (defaults to gemini)
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            generator = self._get_generator(provider)
            reference_image_url = generator.process_reference_image(reference_image)
            generated_image_data, content_type = generator.generate_from_image_and_text(
                reference_image, prompt
            )
            return generated_image_data, content_type, reference_image_url
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is (they already have proper status codes and messages)
            raise
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            # Convert unexpected exceptions to HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
    
    async def generate_fusion_from_images(
        self, 
        image1: UploadFile,
        image2: UploadFile,
        provider: Optional[str] = None
    ) -> Tuple[bytes, str, str]:
        """
        Generate a fusion image from two reference images
        
        Args:
            image1: First uploaded image file
            image2: Second uploaded image file
            provider: AI provider to use (defaults to gemini)
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            generator = self._get_generator(provider)
            # Process first image as reference image URL (for response)
            reference_image_url = generator.process_reference_image(image1)
            
            # Reset file pointers
            image1.file.seek(0)
            image2.file.seek(0)
            
            # Generate fusion using multiple images
            generated_image_data, content_type = generator.generate_from_multiple_images_and_text(
                [image1, image2], 
                prompt_generator.fusion_prompt()
            )
            return generated_image_data, content_type, reference_image_url
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is (they already have proper status codes and messages)
            raise
        except Exception as e:
            logger.error(f"Fusion generation failed: {str(e)}", exc_info=True)
            # Convert unexpected exceptions to HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Fusion generation failed: {str(e)}"
            )
    
    async def generate_teleport(
        self,
        background_image: UploadFile,
        person_image: UploadFile,
        provider: Optional[str] = None
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image by teleporting a person into a new background
        
        Args:
            background_image: Image to use as background (second image)
            person_image: Image containing the person (first image - primary)
            provider: AI provider to use (defaults to gemini)
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            generator = self._get_generator(provider)
            # Process background image as reference image URL (for response)
            reference_image_url = generator.process_reference_image(background_image)
            
            # Reset file pointers
            background_image.file.seek(0)
            person_image.file.seek(0)
            
            # Generate using multiple images
            # Note: The order matters - person image is first (primary), background is second
            # This tells the AI to modify the person's background with the new background
            generated_image_data, content_type = generator.generate_from_multiple_images_and_text(
                [person_image, background_image], 
                prompt_generator.teleport_prompt()
            )
            return generated_image_data, content_type, reference_image_url
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is (they already have proper status codes and messages)
            raise
        except Exception as e:
            logger.error(f"Teleport generation failed: {str(e)}", exc_info=True)
            # Convert unexpected exceptions to HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Teleport generation failed: {str(e)}"
            )
    
    async def generate_grouping_from_images(
        self,
        prompt: str,
        images: List[UploadFile],
        provider: Optional[str] = None
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image using multiple person images and a text prompt
        
        Args:
            prompt: Text prompt for image generation
            images: List of uploaded person image files
            provider: AI provider to use (defaults to gemini)
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            generator = self._get_generator(provider)
            # Process first image as reference image URL (for response)
            reference_image_url = generator.process_reference_image(images[0])
            
            # Reset file pointers for all images
            for image in images:
                image.file.seek(0)
            
            # Generate grouping using multiple images with the provided prompt
            generated_image_data, content_type = generator.generate_from_multiple_images_and_text(
                images, 
                prompt
            )
            return generated_image_data, content_type, reference_image_url
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is (they already have proper status codes and messages)
            raise
        except Exception as e:
            logger.error(f"Grouping generation failed: {str(e)}", exc_info=True)
            # Convert unexpected exceptions to HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Grouping generation failed: {str(e)}"
            )


# Global service instance
prompt_to_image_service = PromptToImageService()
