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

from ..ai.image_to_prompt_generator import image_to_prompt_generator
from ..utils.thumbnail import ThumbnailGenerator
from .prompt_service import prompt_service
from ..db.config import settings

logger = logging.getLogger(__name__)


class ImageToPromptService:
    """Service for handling image to prompt generation business logic"""
    
    def __init__(self):
        self.generator = image_to_prompt_generator
        self.prompt_service = prompt_service
    
    async def generate_prompt_from_image(
        self,
        file: UploadFile,
        style: str = "artistic"
    ) -> dict:
        """
        Generate a prompt from an uploaded image
        
        Args:
            file: Uploaded image file
            style: Style for prompt generation
            
        Returns:
            dict: Response containing prompt, thumbnail, and metadata
            
        Raises:
            HTTPException: If generation fails
        """
        logger.info(f"Starting prompt generation - filename: {file.filename}, style: {style}")
        
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read and validate image
            contents = await file.read()
            try:
                image = Image.open(io.BytesIO(contents))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
            
            # Generate prompt from image using AI
            prompt = await self.generator.generate_prompt_from_image(
                image=image,
                style=style
            )
            
            # Validate prompt length
            if len(prompt) > 1000:
                prompt = prompt[:1000].rsplit(' ', 1)[0]
            
            # Generate thumbnail
            thumbnail_data = ThumbnailGenerator.generate_thumbnail_from_pil_image(image)
            
            # Save the prompt to the database
            try:
                if self.prompt_service.exists_by_text(prompt):
                    return {
                        "success": False,
                        "message": "Prompt already exists in database",
                        "prompt": prompt,
                        "style": style,
                        "thumbnail": f"data:image/webp;base64,{base64.b64encode(thumbnail_data).decode('utf-8')}",
                        "original_filename": file.filename,
                        "prompt_id": None,
                        "saved_to_database": False
                    }
                else:
                    saved_prompt = self.prompt_service.create_prompt(
                        prompt_text=prompt,
                        model=settings.gemini_model,
                        image_data=thumbnail_data
                    )
                    prompt_id = saved_prompt.id
            except Exception as e:
                logger.error(f"Failed to save prompt to database: {str(e)}")
                prompt_id = None
            
            result = {
                "success": True,
                "prompt": prompt,
                "style": style,
                "thumbnail": f"data:image/webp;base64,{base64.b64encode(thumbnail_data).decode('utf-8')}",
                "original_filename": file.filename,
                "prompt_id": prompt_id,
                "saved_to_database": prompt_id is not None
            }
            
            logger.info(f"Prompt generation completed - prompt_id: {prompt_id}, saved: {prompt_id is not None}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")


# Global service instance
image_to_prompt_service = ImageToPromptService()
