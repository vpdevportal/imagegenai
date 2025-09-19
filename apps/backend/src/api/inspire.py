from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging

from ..services.image_to_prompt_service import image_to_prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspire", tags=["inspire"])

# Service is already initialized globally

@router.post("/generate-prompt")
async def generate_prompt_from_image(
    file: UploadFile = File(...),
    style: str = "photorealistic",
    detail_level: str = "detailed"
):
    """
    Generate a prompt from an uploaded image
    """
    logger.info(f"Starting prompt generation request - filename: {file.filename}, content_type: {file.content_type}, style: {style}, detail_level: {detail_level}")
    
    try:
        # Use the service to handle all the business logic
        result = await image_to_prompt_service.generate_prompt_from_image(
            file=file,
            style=style,
            detail_level=detail_level
        )
        
        logger.info(f"Prompt generation completed successfully - prompt_id: {result.get('prompt_id', 'N/A')}, saved_to_database: {result.get('saved_to_database', False)}")
        return JSONResponse(content=result)
        
    except HTTPException as e:
        logger.error(f"HTTP error during prompt generation - status: {e.status_code}, detail: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during prompt generation - error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

@router.get("/styles")
async def get_available_styles():
    """
    Get available prompt styles
    """
    return {
        "styles": [
            {"value": "photorealistic", "label": "Photorealistic"},
            {"value": "artistic", "label": "Artistic"},
            {"value": "minimalist", "label": "Minimalist"},
            {"value": "vintage", "label": "Vintage"},
            {"value": "modern", "label": "Modern"},
            {"value": "abstract", "label": "Abstract"}
        ],
        "detail_levels": [
            {"value": "simple", "label": "Simple"},
            {"value": "detailed", "label": "Detailed"},
            {"value": "comprehensive", "label": "Comprehensive"}
        ]
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "image-to-prompt"}
