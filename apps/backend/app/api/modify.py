from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import json
from typing import Optional
import uuid
from datetime import datetime
import base64
import io

# Create router for image modification endpoints
router = APIRouter(prefix="/modify", tags=["image-modification"])

class ImageModificationRequest(BaseModel):
    prompt: str
    user_id: Optional[int] = None
    metadata: Optional[dict] = None

class ImageModificationResponse(BaseModel):
    id: str
    message: str
    prompt: str
    status: str
    modified_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    created_at: str
    estimated_completion_time: Optional[int] = None

# In-memory storage for demo (replace with database in production)
modified_images = {}

@router.post("/", response_model=ImageModificationResponse)
async def modify_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    metadata: Optional[str] = Form(None)
):
    """
    Modify an uploaded image based on text prompt
    
    This endpoint accepts an image file and a text prompt to modify the image.
    In a real implementation, this would integrate with AI services like 
    OpenAI DALL-E, Stability AI, or similar image editing services.
    """
    try:
        # Validate inputs
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
        
        # Validate image file
        if not image.filename:
            raise HTTPException(
                status_code=400,
                detail="No image file provided"
            )
        
        # Check file type
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
                detail="File too large. Maximum size is 10MB"
            )
        
        # Generate unique ID for this request
        modification_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"custom_metadata": metadata}
        
        # Create image modification record
        modification_data = {
            "id": modification_id,
            "prompt": prompt,
            "user_id": user_id,
            "metadata": parsed_metadata,
            "status": "pending",
            "original_image_url": f"/uploads/original_{modification_id}_{image.filename}",
            "modified_image_url": None,
            "created_at": current_time,
            "updated_at": current_time,
            "file_size": len(content),
            "file_type": image.content_type
        }
        
        # Store in memory (replace with database in production)
        modified_images[modification_id] = modification_data
        
        # TODO: In a real implementation, you would:
        # 1. Save the uploaded image to storage (local filesystem, S3, etc.)
        # 2. Add the request to a task queue (Celery, RQ, etc.)
        # 3. Call AI service for image modification
        # 4. Store the result and update status
        
        response = ImageModificationResponse(
            id=modification_id,
            message="Image modification request received",
            prompt=prompt,
            status="pending",
            modified_image_url=None,
            original_image_url=modification_data["original_image_url"],
            created_at=current_time,
            estimated_completion_time=45  # seconds for modification
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/paste", response_model=ImageModificationResponse)
async def modify_pasted_image(request: dict):
    """
    Modify a pasted/copied image based on text prompt
    
    This endpoint accepts a base64-encoded image and a text prompt.
    """
    try:
        prompt = request.get("prompt", "")
        image_data = request.get("image", "")
        user_id = request.get("user_id")
        metadata = request.get("metadata", {})
        
        # Validate inputs
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
        
        if not image_data:
            raise HTTPException(
                status_code=400,
                detail="No image data provided"
            )
        
        # Validate base64 image data
        try:
            # Remove data URL prefix if present
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]
            
            decoded_image = base64.b64decode(image_data)
            
            # Check file size (max 10MB)
            if len(decoded_image) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=400,
                    detail="Image too large. Maximum size is 10MB"
                )
                
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid image data format"
            )
        
        # Generate unique ID for this request
        modification_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Create image modification record
        modification_data = {
            "id": modification_id,
            "prompt": prompt,
            "user_id": user_id,
            "metadata": metadata,
            "status": "pending",
            "original_image_url": f"/uploads/pasted_{modification_id}.png",
            "modified_image_url": None,
            "created_at": current_time,
            "updated_at": current_time,
            "file_size": len(decoded_image),
            "file_type": "image/png"
        }
        
        # Store in memory (replace with database in production)
        modified_images[modification_id] = modification_data
        
        response = ImageModificationResponse(
            id=modification_id,
            message="Pasted image modification request received",
            prompt=prompt,
            status="pending",
            modified_image_url=None,
            original_image_url=modification_data["original_image_url"],
            created_at=current_time,
            estimated_completion_time=45  # seconds for modification
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{modification_id}", response_model=ImageModificationResponse)
async def get_modification_status(modification_id: str):
    """
    Get the status of an image modification request
    """
    if modification_id not in modified_images:
        raise HTTPException(
            status_code=404,
            detail="Image modification request not found"
        )
    
    modification_data = modified_images[modification_id]
    
    return ImageModificationResponse(
        id=modification_data["id"],
        message="Image modification status",
        prompt=modification_data["prompt"],
        status=modification_data["status"],
        modified_image_url=modification_data["modified_image_url"],
        original_image_url=modification_data["original_image_url"],
        created_at=modification_data["created_at"],
        estimated_completion_time=None
    )

@router.get("/", response_model=dict)
async def list_modification_requests():
    """
    List all image modification requests (for demo purposes)
    """
    return {
        "requests": list(modified_images.values()),
        "total": len(modified_images)
    }

@router.delete("/{modification_id}")
async def delete_modification_request(modification_id: str):
    """
    Delete an image modification request
    """
    if modification_id not in modified_images:
        raise HTTPException(
            status_code=404,
            detail="Image modification request not found"
        )
    
    del modified_images[modification_id]
    
    return {"message": "Image modification request deleted successfully"}
