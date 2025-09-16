from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import json
from typing import Optional
import uuid
from datetime import datetime
import base64
import io
import os

from ..services.image_generator import image_generator
from ..config import settings

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
            
            # Save reference image and get URL
            reference_image_url = image_generator.save_reference_image(image)
            
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
        
        # Generate the actual image using AI
        try:
            if reference_image_url:
                # Reset file pointer for generation
                await image.seek(0)
                generated_image_url, _ = image_generator.generate_from_image_and_text(image, prompt)
            else:
                generated_image_url, _ = image_generator.generate_from_text(prompt)
            
            # Update image data with generated image URL
            image_data.update({
                "status": "completed",
                "generated_image_url": generated_image_url,
                "updated_at": datetime.now().isoformat()
            })
            
            response = ImageGenerationResponse(
                id=image_id,
                message="Image generated successfully",
                prompt=prompt,
                status="completed",
                generated_image_url=generated_image_url,
                reference_image_url=reference_image_url,
                created_at=current_time,
                estimated_completion_time=None
            )
            
        except Exception as e:
            # Update image data with error status
            image_data.update({
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.now().isoformat()
            })
            
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
        
        # Store in memory (replace with database in production)
        generated_images[image_id] = image_data
        
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
