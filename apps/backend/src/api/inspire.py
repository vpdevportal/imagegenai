from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from fastapi.responses import JSONResponse
import logging

from ..services.image_to_prompt_service import image_to_prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspire", tags=["inspire"])

# Service is already initialized globally

@router.post("/generate-prompt")
async def generate_prompt_from_image(
    file: UploadFile = File(...),
    provider: Optional[str] = Form(None)
):
    """
    Generate a prompt from an uploaded image (uses photorealistic style)
    
    Args:
        file: Uploaded image file
        provider: AI provider to use (currently only gemini is supported). Defaults to gemini.
    """
    try:
        result = await image_to_prompt_service.generate_prompt_from_image(
            file=file,
            provider=provider
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
