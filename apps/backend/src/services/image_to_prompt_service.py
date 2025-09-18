"""
Image to Prompt Service

Service layer that handles business logic for generating prompts from images.
Uses the AI generator classes for the actual AI operations.
"""

import logging
import base64
from typing import Tuple
from fastapi import HTTPException, UploadFile
from PIL import Image
import io

from ..ai.image_to_prompt_generator import get_image_to_prompt_generator
from ..utils.thumbnail import ThumbnailGenerator
from .prompt_service import prompt_service

logger = logging.getLogger(__name__)


class ImageToPromptService:
    """Service for handling image to prompt generation business logic"""
    
    def __init__(self):
        self.generator = get_image_to_prompt_generator()
        self.prompt_service = prompt_service
        logger.info("Image to prompt service initialized")
    
    async def generate_prompt_from_image(
        self,
        file: UploadFile,
        style: str = "photorealistic",
        detail_level: str = "detailed"
    ) -> dict:
        """
        Generate a prompt from an uploaded image
        
        Args:
            file: Uploaded image file
            style: Style for prompt generation
            detail_level: Detail level for prompt generation
            
        Returns:
            dict: Response containing prompt, thumbnail, and metadata
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read the uploaded file
            contents = await file.read()
            
            # Validate image
            try:
                image = Image.open(io.BytesIO(contents))
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
            
            # Generate prompt from image using AI
            prompt = await self.generator.generate_prompt_from_image(
                image=image,
                style=style,
                detail_level=detail_level
            )
            
            # Generate a thumbnail for the uploaded image
            thumbnail_data = ThumbnailGenerator.generate_thumbnail_from_pil_image(image)
            
            # Save the prompt to the database
            try:
                saved_prompt = await self.prompt_service.create_prompt(
                    prompt_text=prompt,
                    model="gemini-2.5-flash",  # The model used for generation
                    thumbnail_data=thumbnail_data,
                    source="inspire_tab"  # Mark as generated from inspire tab
                )
                prompt_id = saved_prompt.id
            except Exception as e:
                logger.error(f"Error saving prompt to database: {e}")
                # Continue even if database save fails
                prompt_id = None
            
            return {
                "success": True,
                "prompt": prompt,
                "style": style,
                "detail_level": detail_level,
                "thumbnail": base64.b64encode(thumbnail_data).decode('utf-8'),
                "original_filename": file.filename,
                "prompt_id": prompt_id,
                "saved_to_database": prompt_id is not None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")


# Global service instance
image_to_prompt_service = ImageToPromptService()
