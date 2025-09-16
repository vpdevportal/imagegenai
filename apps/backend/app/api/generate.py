from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import json
from typing import Optional
import uuid
from datetime import datetime
import base64
import io

# Create router for generate endpoints
router = APIRouter(prefix="/generate", tags=["image-generation"])

class ImageGenerationRequest(BaseModel):
    prompt: str
    user_id: Optional[int] = None
    metadata: Optional[dict] = None

class ImageGenerationResponse(BaseModel):
    id: str
    message: str
    prompt: str
    status: str
    generated_image_url: Optional[str] = None
    reference_image_url: Optional[str] = None
    created_at: str
    estimated_completion_time: Optional[int] = None

# In-memory storage for demo (replace with database in production)
generated_images = {}

@router.post("/", response_model=ImageGenerationResponse)
async def generate_image(
    prompt: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user_id: Optional[int] = Form(None),
    metadata: Optional[str] = Form(None)
):
    """
    Generate image from text prompt with optional reference image
    
    This endpoint accepts a text prompt and optionally a reference image
    to generate new images. It can work in two modes:
    1. Text-only generation: Just provide a prompt
    2. Image + prompt generation: Provide both an image and a prompt
    
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
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"custom_metadata": metadata}
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        reference_image_url = None
        
        # Handle reference image if provided
        if image and image.filename:
            # Validate image file
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            if image.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Check file size (max 10MB)
            content = await image.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=400,
                    detail="Reference image too large. Maximum size is 10MB"
                )
            
            reference_image_url = f"/uploads/reference_{image_id}_{image.filename}"
            parsed_metadata.update({
                "has_reference_image": True,
                "reference_filename": image.filename,
                "reference_size": len(content),
                "reference_type": image.content_type
            })
        else:
            parsed_metadata.update({
                "has_reference_image": False
            })
        
        # Create image generation record
        image_data = {
            "id": image_id,
            "prompt": prompt,
            "user_id": user_id,
            "metadata": parsed_metadata,
            "status": "pending",
            "generated_image_url": None,
            "reference_image_url": reference_image_url,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Store in memory (replace with database in production)
        generated_images[image_id] = image_data
        
        # TODO: In a real implementation, you would:
        # 1. Save the reference image to storage if provided
        # 2. Add the request to a task queue (Celery, RQ, etc.)
        # 3. Call AI service with prompt and optional reference image
        # 4. Store the result in database
        # 5. Update status to "completed" or "failed"
        
        # Determine completion time based on whether reference image is provided
        completion_time = 45 if reference_image_url else 30
        
        response = ImageGenerationResponse(
            id=image_id,
            message="Image generation request received",
            prompt=prompt,
            status="pending",
            generated_image_url=None,
            reference_image_url=reference_image_url,
            created_at=current_time,
            estimated_completion_time=completion_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{image_id}", response_model=ImageGenerationResponse)
async def get_generation_status(image_id: str):
    """
    Get the status of an image generation request
    """
    if image_id not in generated_images:
        raise HTTPException(
            status_code=404,
            detail="Image generation request not found"
        )
    
    image_data = generated_images[image_id]
    
    return ImageGenerationResponse(
        id=image_data["id"],
        message="Image generation status",
        prompt=image_data["prompt"],
        status=image_data["status"],
        generated_image_url=image_data["generated_image_url"],
        reference_image_url=image_data.get("reference_image_url"),
        created_at=image_data["created_at"],
        estimated_completion_time=None
    )

@router.get("/", response_model=dict)
async def list_generation_requests():
    """
    List all image generation requests (for demo purposes)
    """
    return {
        "requests": list(generated_images.values()),
        "total": len(generated_images)
    }

@router.delete("/{image_id}")
async def delete_generation_request(image_id: str):
    """
    Delete an image generation request
    """
    if image_id not in generated_images:
        raise HTTPException(
            status_code=404,
            detail="Image generation request not found"
        )
    
    del generated_images[image_id]
    
    return {"message": "Image generation request deleted successfully"}
