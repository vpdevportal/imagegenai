"""
Image to Prompt Service

Service layer that handles business logic for generating prompts from images.
Uses the AI generator classes for the actual AI operations.
"""

import logging
import base64
from typing import Tuple, Optional
from fastapi import HTTPException, UploadFile
from PIL import Image
import io

from ..ai.factory import PromptGeneratorFactory
from ..utils.thumbnail import ThumbnailGenerator
from .prompt_service import prompt_service
from ..db.config import settings

logger = logging.getLogger(__name__)


class ImageToPromptService:
    """Service for handling image to prompt generation business logic"""
    
    def __init__(self):
        self.prompt_service = prompt_service
    
    def _get_generator(self, provider: Optional[str] = None):
        """
        Get the appropriate prompt generator instance based on provider
        
        Args:
            provider: Provider name (defaults to gemini if not specified)
            
        Returns:
            BasePromptGenerator: Generator instance
        """
        provider = provider or getattr(settings, 'default_ai_provider', 'gemini')
        return PromptGeneratorFactory.create(provider)
    
    async def generate_prompt_from_image(
        self,
        file: UploadFile,
        provider: Optional[str] = None
    ) -> dict:
        """
        Generate a prompt from an uploaded image
        
        Args:
            file: Uploaded image file
            provider: AI provider to use (defaults to gemini)
            
        Returns:
            dict: Response containing prompt, thumbnail, and metadata
            
        Raises:
            HTTPException: If generation fails
        """
        logger.info(f"Starting prompt generation - filename: {file.filename}, provider: {provider or 'gemini'}")
        
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
            
            # Get generator and generate prompt from image using AI
            generator = self._get_generator(provider)
            prompt = await generator.generate_prompt_from_image(
                image=image
            )
            
            # Validate prompt length
            if len(prompt) > 2000:
                prompt = prompt[:2000].rsplit(' ', 1)[0]
            
            # Generate thumbnail
            thumbnail_data = ThumbnailGenerator.generate_thumbnail_from_pil_image(image)
            
            # Save the prompt to the database
            try:
                if self.prompt_service.exists_by_text(prompt):
                    return {
                        "success": False,
                        "message": "Prompt already exists in database",
                        "prompt": prompt,
                        "style": "photorealistic",
                        "thumbnail": f"data:image/webp;base64,{base64.b64encode(thumbnail_data).decode('utf-8')}",
                        "original_filename": file.filename,
                        "prompt_id": None,
                        "saved_to_database": False
                    }
                else:
                    # Use provider name or default model name for database
                    model_name = provider or getattr(settings, 'gemini_model', 'gemini-2.5-flash-image')
                    saved_prompt = self.prompt_service.create_prompt(
                        prompt_text=prompt,
                        model=model_name,
                        image_data=thumbnail_data
                    )
                    prompt_id = saved_prompt.id
            except Exception as e:
                logger.error(f"Failed to save prompt to database: {str(e)}")
                prompt_id = None
            
            result = {
                "success": True,
                "prompt": prompt,
                "style": "photorealistic",
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
