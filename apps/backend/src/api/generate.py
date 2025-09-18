from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import base64

from ..services.prompt_to_image_service import prompt_to_image_service
from ..db.config import settings

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
    """Generate image from text prompt with reference image"""
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
        
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        if image.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        content = await image.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"Reference image too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
            )
        
        await image.seek(0)
        
        try:
            await image.seek(0)
            generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_image_from_prompt(
                prompt=prompt,
                reference_image=image
            )
            
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
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

