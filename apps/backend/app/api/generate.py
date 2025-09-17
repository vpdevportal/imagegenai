from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import base64
import logging

from ..services.image_generator import image_generator
from ..config import settings

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
    try:
        # Validate prompt
        if not prompt.strip():
            raise HTTPException(
                status_code=400, 
                detail="Prompt cannot be empty"
            )
        
        if len(prompt) > 1000:
            raise HTTPException(
                status_code=400, 
                detail="Prompt too long (max 1000 characters)"
            )
        
        # Validate that image is provided
        if not image or not image.filename:
            raise HTTPException(
                status_code=400,
                detail="Reference image is required"
            )
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        # Handle reference image (now mandatory)
        # Validate image file
        if image.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Check file size
        content = await image.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Reference image too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Reset file pointer for service
        await image.seek(0)
        
        # Process reference image and get data URL
        reference_image_url = image_generator.process_reference_image(image)
        
        # Generate the actual image using AI
        try:
            # Reset file pointer for generation
            await image.seek(0)
            generated_image_data, content_type = image_generator.generate_from_image_and_text(image, prompt)
            
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
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

