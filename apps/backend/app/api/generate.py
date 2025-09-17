from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from typing import Optional
import uuid
from datetime import datetime
import base64
import io
import os
import logging

from ..services.image_generator import image_generator
from ..config import settings

# Configure logging
logger = logging.getLogger(__name__)

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
    image: UploadFile = File(...)
):
    """
    Generate image from text prompt with reference image
    
    This endpoint requires both a text prompt and a reference image
    to generate new images. The reference image is mandatory.
    
    In a real implementation, this would integrate with AI services like 
    OpenAI DALL-E, Stability AI, etc.
    """
    logger.info(f"Starting image generation request - Prompt: '{prompt[:50]}...', Image: {image.filename}")
    
    try:
        # Validate prompt
        if not prompt.strip():
            logger.warning("Empty prompt provided")
            raise HTTPException(
                status_code=400, 
                detail="Prompt cannot be empty"
            )
        
        if len(prompt) > 1000:
            logger.warning(f"Prompt too long: {len(prompt)} characters")
            raise HTTPException(
                status_code=400, 
                detail="Prompt too long (max 1000 characters)"
            )
        
        # Validate that image is provided
        if not image or not image.filename:
            logger.warning("No image provided")
            raise HTTPException(
                status_code=400,
                detail="Reference image is required"
            )
        
        # Generate unique ID for this request
        image_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        logger.info(f"Generated request ID: {image_id}")
        
        # Handle reference image (now mandatory)
        logger.info(f"Processing reference image: {image.filename}, type: {image.content_type}")
        
        # Validate image file
        if image.content_type not in settings.allowed_image_types:
            logger.warning(f"Invalid file type: {image.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Check file size
        content = await image.read()
        logger.info(f"Reference image size: {len(content)} bytes")
        if len(content) > settings.max_file_size:
            logger.warning(f"Image too large: {len(content)} bytes (max: {settings.max_file_size})")
            raise HTTPException(
                status_code=400,
                detail=f"Reference image too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Reset file pointer for service
        await image.seek(0)
        
        # Save reference image and get URL
        logger.info("Saving reference image...")
        reference_image_url = image_generator.save_reference_image(image)
        logger.info(f"Reference image saved: {reference_image_url}")
        
        # Create image generation record
        image_data = {
            "id": image_id,
            "prompt": prompt,
            "status": "pending",
            "generated_image_url": None,
            "reference_image_url": reference_image_url,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Generate the actual image using AI
        logger.info("Starting image generation...")
        try:
            # Generate image with reference image (now mandatory)
            logger.info("Generating image with reference image...")
            # Reset file pointer for generation
            await image.seek(0)
            generated_image_data, content_type = image_generator.generate_from_image_and_text(image, prompt)
            logger.info(f"Generated image data received: {len(generated_image_data)} bytes")
            
            # Convert image data to base64 for JSON response
            generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
            generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
            
            # Update image data with generated image data URL
            image_data.update({
                "status": "completed",
                "generated_image_url": generated_image_data_url,
                "updated_at": datetime.now().isoformat()
            })
            
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
        logger.info(f"Image generation completed successfully for ID: {image_id}")
        
        return response
        
    except HTTPException:
        logger.warning("HTTP exception occurred during image generation")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{image_id}", response_model=ImageGenerationResponse)
async def get_generation_status(image_id: str):
    """
    Get the status of an image generation request
    """
    logger.info(f"Getting generation status for ID: {image_id}")
    
    if image_id not in generated_images:
        logger.warning(f"Generation request not found: {image_id}")
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
    logger.info(f"Listing generation requests - Total: {len(generated_images)}")
    return {
        "requests": list(generated_images.values()),
        "total": len(generated_images)
    }

@router.delete("/{image_id}")
async def delete_generation_request(image_id: str):
    """
    Delete an image generation request
    """
    logger.info(f"Deleting generation request: {image_id}")
    
    if image_id not in generated_images:
        logger.warning(f"Generation request not found for deletion: {image_id}")
        raise HTTPException(
            status_code=404,
            detail="Image generation request not found"
        )
    
    del generated_images[image_id]
    logger.info(f"Generation request deleted successfully: {image_id}")
    
    return {"message": "Image generation request deleted successfully"}
