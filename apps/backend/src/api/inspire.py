from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.image_to_prompt_service import image_to_prompt_service

router = APIRouter(prefix="/inspire", tags=["inspire"])

@router.post("/generate-prompt")
async def generate_prompt_from_image(
    file: UploadFile = File(...),
    style: str = "photorealistic",
    detail_level: str = "detailed"
):
    """Generate a prompt from an uploaded image"""
    try:
        result = await image_to_prompt_service.generate_prompt_from_image(
            file=file,
            style=style,
            detail_level=detail_level
        )
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

@router.get("/styles")
async def get_available_styles():
    """Get available prompt styles"""
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
    """Health check endpoint"""
    return {"status": "healthy", "service": "image-to-prompt"}
