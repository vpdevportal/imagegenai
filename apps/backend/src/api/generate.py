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
    provider: Optional[str] = Form(None),
    prompt_id: Optional[int] = Form(None)
):
    """
    Generate image from text prompt with reference image
    
    This endpoint requires both a text prompt and a reference image
    to generate new images. The reference image is mandatory.
    
    Args:
        prompt: Text prompt for image generation (required)
        image: Reference image file
        provider: AI provider to use (gemini, replicate, stability). Defaults to gemini.
        prompt_id: Optional prompt ID. If provided, will increment usage count for that prompt ID.
    """
    logger.info(f"Starting image generation - prompt_id: {prompt_id}, prompt_length: {len(prompt) if prompt else 0}, filename: {image.filename if image else 'None'}, content_type: {image.content_type if image else 'None'}, provider: {provider or 'gemini'}")
    
    try:
        # Validate prompt (always required)
        if not prompt or not prompt.strip():
            logger.warning(f"Validation failed: Empty prompt")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(prompt) > 2000:
            logger.warning(f"Validation failed: Prompt too long ({len(prompt)} characters)")
            raise HTTPException(status_code=400, detail="Prompt too long (max 2000 characters)")
        
        # Validate that image is provided
        if not image or not image.filename:
            logger.warning(f"Validation failed: No image file provided")
            raise HTTPException(status_code=400, detail="Reference image is required")
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Validate image file
        # Use content_type if available, otherwise try to infer from filename
        content_type_to_validate = image.content_type
        if not content_type_to_validate and image.filename:
            # Try to infer from filename extension
            filename_lower = image.filename.lower()
            if filename_lower.endswith(('.jpg', '.jpeg')):
                content_type_to_validate = 'image/jpeg'
                logger.info(f"Inferred content_type: {content_type_to_validate} from filename: {image.filename}")
            elif filename_lower.endswith('.png'):
                content_type_to_validate = 'image/png'
                logger.info(f"Inferred content_type: {content_type_to_validate} from filename: {image.filename}")
            elif filename_lower.endswith('.webp'):
                content_type_to_validate = 'image/webp'
                logger.info(f"Inferred content_type: {content_type_to_validate} from filename: {image.filename}")
        
        if not content_type_to_validate:
            logger.warning(f"Image file has no content_type and could not infer from filename: {image.filename}")
            # Allow to proceed - the service layer will handle actual image validation
            # This is more lenient than before to avoid breaking existing functionality
        else:
            # Normalize content_type (handle case and variations)
            content_type_lower = content_type_to_validate.lower()
            # Map common variations
            content_type_map = {
                'image/jpg': 'image/jpeg',
                'image/jpeg': 'image/jpeg',
                'image/png': 'image/png',
                'image/webp': 'image/webp'
            }
            normalized_content_type = content_type_map.get(content_type_lower, content_type_lower)
            
            # Check if normalized type is allowed
            allowed_types_lower = [t.lower() for t in settings.allowed_image_types]
            if normalized_content_type not in allowed_types_lower and content_type_lower not in allowed_types_lower:
                logger.warning(f"Invalid file type: {content_type_to_validate} (normalized: {normalized_content_type}) - filename: {image.filename}")
            raise HTTPException(
                status_code=400,
                    detail=f"Invalid file type: {content_type_to_validate}. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Check file size
        content = await image.read()
        file_size = len(content)
        max_size_mb = settings.max_file_size // (1024*1024)
        
        if file_size > settings.max_file_size:
            logger.warning(f"Validation failed: File too large ({file_size / (1024*1024):.2f}MB, max: {max_size_mb}MB)")
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
        
        # Track usage for the prompt (only on successful generation)
        try:
            if prompt_id:
                # Increment usage by ID
                prompt_service.increment_usage_by_id(prompt_id)
                logger.info(f"Successfully incremented usage count for prompt ID {prompt_id}")
            elif prompt_service.exists_by_text(prompt):
                # Fallback to text-based tracking if no prompt_id provided
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
        # Track failure for the prompt
        try:
            if prompt_id:
                prompt_service.track_failure_by_id(prompt_id)
            elif prompt and prompt_service.exists_by_text(prompt):
                prompt_service.track_failure(prompt)
        except Exception:
            pass
        
        raise e
    except Exception as e:
        logger.error(f"Error during image generation: {str(e)}", exc_info=True)
        
        # Track failure for the prompt
        try:
            if prompt_id:
                prompt_service.track_failure_by_id(prompt_id)
            elif prompt and prompt_service.exists_by_text(prompt):
                prompt_service.track_failure(prompt)
        except Exception:
            pass
        
        # Only log full traceback, but return user-friendly message
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image. Please try again later."
        )

