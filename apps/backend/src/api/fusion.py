from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
import base64
import logging

from ..services.prompt_to_image_service import prompt_to_image_service
from ..ai.prompt_generator import prompt_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fusion", tags=["fusion"])


@router.post("/generate")
async def generate_fusion(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    provider: Optional[str] = Form(None)
):
    """
    Generate a fusion image by merging two people from separate images
    
    Args:
        image1: First uploaded image file (required)
        image2: Second uploaded image file (required)
        provider: AI provider to use (gemini, replicate, stability, huggingface). Defaults to gemini.
    """
    logger.info(f"Starting image fusion request - image1: {image1.filename}, image2: {image2.filename}, provider: {provider or 'gemini'}")
    
    try:
        # Validate both files
        if not image1 or not image1.filename:
            raise HTTPException(status_code=400, detail="First image file is required")
        
        if not image2 or not image2.filename:
            raise HTTPException(status_code=400, detail="Second image file is required")
        
        if not image1.content_type or not image1.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="First file must be an image")
        
        if not image2.content_type or not image2.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Second file must be an image")
        
        # Get fusion prompt
        fusion_prompt = prompt_generator.fusion_prompt()
        logger.info(f"Fusion prompt: {fusion_prompt}")
        
        # Generate fusion using service
        generated_image_data, content_type, reference_image_url = await prompt_to_image_service.generate_fusion_from_images(
            image1=image1,
            image2=image2,
            provider=provider
        )
        
        # Convert image data to base64 for JSON response
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        generated_image_data_url = f"data:{content_type};base64,{generated_image_base64}"
        
        # Generate unique ID for this request
        fusion_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        response_data = {
            "id": fusion_id,
            "message": "Image fusion generated successfully",
            "prompt": fusion_prompt,
            "status": "completed",
            "generated_image_url": generated_image_data_url,
            "reference_image_url": reference_image_url,
            "created_at": current_time
        }
        
        logger.info(f"Image fusion completed successfully - id: {fusion_id}")
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image fusion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image fusion: {str(e)}"
        )

