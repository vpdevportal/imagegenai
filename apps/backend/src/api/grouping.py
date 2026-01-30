from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..db.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grouping", tags=["grouping"])


@router.post("/generate")
async def generate_grouping(
    prompt: str = Form(...),
    images: List[UploadFile] = File(...),
    provider: Optional[str] = Form(None),
    prompt_id: Optional[int] = Form(None)
):
    """
    Generate an image using multiple person images and a text prompt
    
    Args:
        prompt: Text prompt for image generation (required)
        images: List of uploaded person image files (required, at least 1)
        provider: AI provider to use (gemini, replicate, stability). Defaults to gemini.
        prompt_id: Optional prompt ID. If provided, will increment usage count for that prompt ID.
    """
    logger.info(f"Starting image grouping request - prompt_id: {prompt_id}, prompt_length: {len(prompt) if prompt else 0}, num_images: {len(images) if images else 0}, provider: {provider or 'gemini'}")
    
    try:
        # Validate prompt
        if not prompt or not prompt.strip():
            logger.warning(f"Validation failed: Empty prompt")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(prompt) > 5000:
            logger.warning(f"Validation failed: Prompt too long ({len(prompt)} characters)")
            raise HTTPException(status_code=400, detail="Prompt too long (max 5000 characters)")
        
        # Validate images
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one person image is required")
        
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
        
        # Validate each image
        for idx, image in enumerate(images):
            if not image or not image.filename:
                raise HTTPException(status_code=400, detail=f"Image {idx + 1} is invalid or missing filename")
            
            # Validate content type
            content_type_to_validate = image.content_type
            if not content_type_to_validate and image.filename:
                # Try to infer from filename extension
                filename_lower = image.filename.lower()
                if filename_lower.endswith(('.jpg', '.jpeg')):
                    content_type_to_validate = 'image/jpeg'
                elif filename_lower.endswith('.png'):
                    content_type_to_validate = 'image/png'
                elif filename_lower.endswith('.webp'):
                    content_type_to_validate = 'image/webp'
            
            if not content_type_to_validate:
                logger.warning(f"Image {idx + 1} has no content_type and could not infer from filename: {image.filename}")
            else:
                # Normalize content_type
                content_type_lower = content_type_to_validate.lower()
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
                    logger.warning(f"Invalid file type for image {idx + 1}: {content_type_to_validate} - filename: {image.filename}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image {idx + 1} has invalid file type: {content_type_to_validate}. Allowed types: {', '.join(settings.allowed_image_types)}"
                    )
            
            # Check file size
            content = await image.read()
            file_size = len(content)
            max_size_mb = settings.max_file_size // (1024*1024)
            
            if file_size > settings.max_file_size:
                logger.warning(f"Validation failed: Image {idx + 1} too large ({file_size / (1024*1024):.2f}MB, max: {max_size_mb}MB)")
                raise HTTPException(
                    status_code=400,
                    detail=f"Image {idx + 1} too large. Maximum size is {max_size_mb}MB"
                )
            
            # Reset file pointer for service
            await image.seek(0)
        
        # Generate grouping using service
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_grouping_from_images(
            prompt=prompt,
            images=images,
            provider=provider
        )
        
        # Track usage for the prompt (only on successful generation)
        try:
            if prompt_id:
                # Increment usage by ID
                from ..services.prompt_service import prompt_service
                prompt_service.increment_usage_by_id(prompt_id)
                logger.info(f"Successfully incremented usage count for prompt ID {prompt_id}")
        except Exception as usage_error:
            logger.warning(f"Failed to track prompt usage: {usage_error}")
        
        # Convert image data to base64 for JSON response
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        
        # Generate unique ID for this request
        grouping_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        response_data = {
            "id": grouping_id,
            "message": "Image grouping generated successfully",
            "prompt": prompt,
            "status": "completed",
            "generated_image_url": generated_image_data_url,
            "reference_image_url": reference_image_url,
            "created_at": current_time
        }
        
        logger.info(f"Image grouping completed successfully - id: {grouping_id}")
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Track failure for the prompt
        try:
            if prompt_id:
                from ..services.prompt_service import prompt_service
                prompt_service.track_failure_by_id(prompt_id)
        except Exception:
            pass
        # Re-raise HTTPExceptions as-is - they already have proper status codes and user-friendly messages
        raise
    except Exception as e:
        logger.error(f"Error generating image grouping: {str(e)}", exc_info=True)
        
        # Track failure for the prompt
        try:
            if prompt_id:
                from ..services.prompt_service import prompt_service
                prompt_service.track_failure_by_id(prompt_id)
        except Exception:
            pass
        
        # Only log full traceback, but return user-friendly message
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image grouping. Please try again later."
        )

