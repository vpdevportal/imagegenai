from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..ai.prompt_generator import prompt_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teleport", tags=["teleport"])


@router.post("/generate")
async def generate_teleport(
    background_image: UploadFile = File(...),
    person_image: UploadFile = File(...)
):
    """
    Generate an image by teleporting a person into a new background
    
    Args:
        background_image: The new background image (first image)
        person_image: The image containing the person (second image)
    """
    logger.info(f"Starting teleport request - background: {background_image.filename}, person: {person_image.filename}")
    
    try:
        # Validate both files
        if not background_image or not background_image.filename:
            raise HTTPException(status_code=400, detail="Background image file is required")
        
        if not person_image or not person_image.filename:
            raise HTTPException(status_code=400, detail="Person image file is required")
        
        if not background_image.content_type or not background_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="First file must be an image")
        
        if not person_image.content_type or not person_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Second file must be an image")
        
        # Get prompt
        teleport_prompt = prompt_generator.teleport_prompt()
        logger.info(f"Teleport prompt: {teleport_prompt}")
        
        # Generate using service
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_teleport(
            background_image=background_image,
            person_image=person_image
        )
        
        # Convert image data to base64 for JSON response
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        response_data = {
            "id": request_id,
            "message": "Teleport generated successfully",
            "prompt": teleport_prompt,
            "status": "completed",
            "generated_image_url": generated_image_data_url,
            "reference_image_url": reference_image_url,
            "created_at": current_time
        }
        
        logger.info(f"Teleport completed successfully - id: {request_id}")
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating teleport: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate teleport: {str(e)}"
        )
