from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..ai.prompt_generator import prompt_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/variations", tags=["variations"])


@router.post("/generate")
async def generate_variation(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    """
    Generate a variation of an uploaded image using Gemini image editing
    
    Args:
        file: Uploaded image file (required)
        prompt: Optional text prompt describing the desired variation
                If not provided, generates an automatic variation
    """
    has_prompt = prompt is not None and prompt.strip() != '' if prompt else False
    logger.info(f"Starting image variation request - filename: {file.filename}, has_prompt: {has_prompt}")
    
    try:
        # Validate file
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Image file is required")
        
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Use provided prompt or default prompt for automatic variation
        variation_prompt = prompt_generator.variation_prompt(prompt)
        logger.info(f"Variation prompt: {variation_prompt}")
        
        # Generate variation using existing service
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_image_from_prompt(
            prompt=variation_prompt,
            reference_image=file
        )
        
        # Convert image data to base64 for JSON response
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        
        # Generate unique ID for this request
        variation_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        response_data = {
            "id": variation_id,
            "message": "Image variation generated successfully",
            "prompt": variation_prompt,
            "original_prompt": prompt if prompt else None,
            "status": "completed",
            "generated_image_url": generated_image_data_url,
            "reference_image_url": reference_image_url,
            "created_at": current_time
        }
        
        logger.info(f"Image variation completed successfully - id: {variation_id}")
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image variation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image variation: {str(e)}"
        )

