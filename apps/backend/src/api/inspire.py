from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging

from ..services.image_to_prompt_service import image_to_prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspire", tags=["inspire"])

# Service is already initialized globally

@router.post("/generate-prompt")
async def generate_prompt_from_image(
    file: UploadFile = File(...)
):
    """
    Generate a prompt from an uploaded image (uses photorealistic style)
    """
    try:
        result = await image_to_prompt_service.generate_prompt_from_image(
            file=file
        )
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "image-to-prompt"}
