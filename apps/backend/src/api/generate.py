from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..db.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router for generate endpoints
router = APIRouter(prefix="/generate", tags=["image-generation"])


class ImageGenerationResponse(BaseModel):
    id: str
    message: str
    prompt: str
    status: str
    generated_image_url: Optional[str] = None
    reference_image_url: Optional[str] = None
    created_at: str
    estimated_completion_time: Optional[int] = None


@router.post("/", response_model=ImageGenerationResponse)
async def generate_image(
    prompt: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Generate image from text prompt with reference image
    
    This endpoint requires both a text prompt and a reference image
    to generate new images. The reference image is mandatory.
    
    In a real implementation, this would integrate with AI services like 
    OpenAI DALL-E, Stability AI, etc.
    """
    logger.info(f"Starting image generation request - prompt_length: {len(prompt)}, image_filename: {image.filename if image else 'None'}, image_content_type: {image.content_type if image else 'None'}")
    
    try:
        # Validate prompt
        logger.debug(f"Validating prompt - prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
        if not prompt.strip():
            logger.warning("Empty prompt received")
            raise HTTPException(
                status_code=400, 
                detail="Prompt cannot be empty"
            )
        
        if len(prompt) > 1000:
            logger.warning(f"Prompt too long - length: {len(prompt)}, max: 1000")
            raise HTTPException(
                status_code=400, 
                detail="Prompt too long (max 1000 characters)"
            )
        
        logger.info(f"Prompt validation passed - length: {len(prompt)}")
        
        # Validate that image is provided
        logger.debug(f"Validating image file - filename: {image.filename if image else 'None'}")
        if not image or not image.filename:
            logger.warning("No image file provided")
            raise HTTPException(
                status_code=400,
                detail="Reference image is required"
            )
        
        logger.info(f"Image file validation passed - filename: {image.filename}")
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        logger.info(f"Generated request ID: {image_id}")
        
        # Handle reference image (now mandatory)
        # Validate image file
        logger.debug(f"Validating image content type - received: {image.content_type}, allowed: {settings.allowed_image_types}")
        if image.content_type not in settings.allowed_image_types:
            logger.warning(f"Invalid file type - received: {image.content_type}, allowed: {settings.allowed_image_types}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Check file size
        logger.debug("Reading image content to check file size")
        content = await image.read()
        file_size = len(content)
        max_size_mb = settings.max_file_size // (1024*1024)
        logger.info(f"Image file size: {file_size} bytes ({file_size / (1024*1024):.2f} MB), max: {settings.max_file_size} bytes ({max_size_mb} MB)")
        
        if file_size > settings.max_file_size:
            logger.warning(f"File too large - size: {file_size} bytes, max: {settings.max_file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"Reference image too large. Maximum size is {max_size_mb}MB"
            )
        
        logger.info("Image file validation passed")
        
        # Reset file pointer for service
        await image.seek(0)
        logger.debug("Reset image file pointer for service call")
        
        # Generate image using service
        logger.info("Starting image generation via service")
        # Reset file pointer for generation
        await image.seek(0)
        logger.debug("Reset image file pointer for generation")
        
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_image_from_prompt(
            prompt=prompt,
            reference_image=image
        )
        
        logger.info(f"Image generation completed - generated_size: {len(generated_image_data)} bytes, content_type: {content_type}")
        
        # Convert image data to base64 for JSON response
        logger.debug("Converting generated image to base64")
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        logger.info(f"Base64 conversion completed - data_url_length: {len(generated_image_data_url)}")
        
        response = ImageGenerationResponse(
            id=image_id,
            message="Image generated successfully",
            prompt=prompt,
            status="completed",
            generated_image_url=generated_image_data_url,
            reference_image_url=reference_image_url,
            created_at=current_time,
            estimated_completion_time=None
        )
        
        logger.info(f"Image generation request completed successfully - id: {image_id}")
        
        return response
        
    except HTTPException as e:
        logger.error(f"HTTP error during image generation - status: {e.status_code}, detail: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during image generation - error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

