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
        logger.info("Image to prompt service initialized")
    
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
        logger.info(f"Starting image to prompt generation - filename: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}, style: {style}")
        
        try:
            # Validate file type
            logger.debug(f"Validating file type - content_type: {file.content_type}")
            if not file.content_type or not file.content_type.startswith('image/'):
                logger.warning(f"Invalid file type received - content_type: {file.content_type}")
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Read the uploaded file
            logger.debug("Reading uploaded file contents")
            contents = await file.read()
            logger.info(f"File read successfully - size: {len(contents)} bytes")
            
            # Validate image
            logger.debug("Validating and processing image")
            try:
                image = Image.open(io.BytesIO(contents))
                logger.info(f"Image opened successfully - mode: {image.mode}, size: {image.size}")
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    logger.debug(f"Converting image from {image.mode} to RGB")
                    image = image.convert('RGB')
                    logger.info("Image converted to RGB successfully")
            except Exception as e:
                logger.error(f"Failed to process image - error: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
            
            # Generate prompt from image using AI
            logger.info("Starting AI prompt generation")
            prompt = await self.generator.generate_prompt_from_image(
                image=image,
                style=style
            )
            logger.info(f"AI prompt generation completed - prompt length: {len(prompt)} characters")
            
            # Validate prompt length
            if len(prompt) > 1000:
                logger.warning(f"Generated prompt exceeds 1000 characters ({len(prompt)}), truncating")
                prompt = prompt[:1000].rsplit(' ', 1)[0]  # Truncate at last complete word
                logger.info(f"Final prompt length after truncation: {len(prompt)} characters")
            
            # Generate a thumbnail for the uploaded image
            logger.debug("Generating thumbnail for uploaded image")
            thumbnail_data = ThumbnailGenerator.generate_thumbnail_from_pil_image(image)
            logger.info(f"Thumbnail generated successfully - size: {len(thumbnail_data)} bytes")
            
            # Save the prompt to the database
            logger.debug("Attempting to save prompt to database")
            try:

                if self.prompt_service.exists_by_text(prompt):
                    logger.info("Prompt already exists in database")
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
                    logger.info("Prompt does not exist in database")
                    saved_prompt = self.prompt_service.create_prompt(
                        prompt_text=prompt,
                        model=settings.gemini_model,
                        image_data=thumbnail_data
                    )
                    prompt_id = saved_prompt.id
                    logger.info(f"Prompt saved to database successfully - prompt_id: {prompt_id}, total_uses: {saved_prompt.total_uses}")
            except Exception as e:
                logger.error(f"Failed to save prompt to database - error: {str(e)}")
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
            
            logger.info(f"Image to prompt generation completed successfully - saved_to_database: {prompt_id is not None}")
            return result
            
        except HTTPException as e:
            logger.error(f"HTTP error in image to prompt generation - status: {e.status_code}, detail: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in image to prompt generation - error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")


# Global service instance
image_to_prompt_service = ImageToPromptService()
