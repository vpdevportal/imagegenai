from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..services.prompt_service import prompt_service
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
    image: UploadFile = File(...),
    provider: Optional[str] = Form(None)
):
    """
    Generate image from text prompt with reference image
    
    This endpoint requires both a text prompt and a reference image
    to generate new images. The reference image is mandatory.
    
    Args:
        prompt: Text prompt for image generation
        image: Reference image file
        provider: AI provider to use (gemini, replicate, stability, huggingface). Defaults to gemini.
    """
    logger.info(f"Starting image generation - prompt_length: {len(prompt)}, filename: {image.filename}, provider: {provider or 'gemini'}")
    
    try:
        # Validate prompt
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt too long (max 1000 characters)")
        
        # Validate that image is provided
        if not image or not image.filename:
            raise HTTPException(status_code=400, detail="Reference image is required")
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Validate image file
        if image.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Check file size
        content = await image.read()
        file_size = len(content)
        max_size_mb = settings.max_file_size // (1024*1024)
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Reference image too large. Maximum size is {max_size_mb}MB"
            )
        
        # Reset file pointer for service
        await image.seek(0)
        
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_image_from_prompt(
            prompt=prompt,
            reference_image=image,
            provider=provider
        )
        
        # Track usage for the original prompt if it exists in database (only on successful generation)
        try:
            if prompt_service.exists_by_text(prompt):
                model_name = provider or getattr(settings, 'gemini_model', 'gemini-2.5-flash-image')
                prompt_service.update_prompt(prompt, model_name)
        except Exception as usage_error:
            logger.warning(f"Failed to track prompt usage: {usage_error}")
        
        # Convert image data to base64 for JSON response
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        
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
        
        logger.info(f"Image generation completed successfully - id: {image_id}")
        
        return response
        
    except HTTPException as e:
        # Track failure for the original prompt if it exists in database
        try:
            if prompt_service.exists_by_text(prompt):
                prompt_service.track_failure(prompt)
        except Exception:
            pass
        
        raise e
    except Exception as e:
        logger.error(f"Error during image generation: {str(e)}", exc_info=True)
        
        # Track failure for the original prompt if it exists in database
        try:
            if prompt_service.exists_by_text(prompt):
                prompt_service.track_failure(prompt)
        except Exception:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

