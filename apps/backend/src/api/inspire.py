from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import List
import tempfile
import os
from PIL import Image
import io
import base64

from ..services.image_to_prompt_generator import get_image_to_prompt_generator
from ..services.prompt_service import PromptService
from ..db.config import settings

router = APIRouter(prefix="/inspire", tags=["inspire"])

# Initialize the services
prompt_service = PromptService()

@router.post("/generate-prompt")
async def generate_prompt_from_image(
    file: UploadFile = File(...),
    style: str = "photorealistic",
    detail_level: str = "detailed"
):
    """
    Generate a prompt from an uploaded image
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read the uploaded file
        contents = await file.read()
        
        # Validate image
        try:
            image = Image.open(io.BytesIO(contents))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Get the generator instance
        generator = get_image_to_prompt_generator()
        
        # Generate prompt from image
        prompt = await generator.generate_prompt_from_image(
            image=image,
            style=style,
            detail_level=detail_level
        )
        
        # Generate a thumbnail for the uploaded image
        thumbnail_data = generator.generate_thumbnail(image)
        
        # Save the prompt to the database
        try:
            saved_prompt = await prompt_service.create_prompt(
                prompt_text=prompt,
                model="gemini-2.0-flash-exp",  # The model used for generation
                thumbnail_data=thumbnail_data,
                source="inspire_tab"  # Mark as generated from inspire tab
            )
            prompt_id = saved_prompt.id
        except Exception as e:
            print(f"Error saving prompt to database: {e}")
            # Continue even if database save fails
            prompt_id = None
        
        return JSONResponse(content={
            "success": True,
            "prompt": prompt,
            "style": style,
            "detail_level": detail_level,
            "thumbnail": base64.b64encode(thumbnail_data).decode('utf-8'),
            "original_filename": file.filename,
            "prompt_id": prompt_id,
            "saved_to_database": prompt_id is not None
        })
        
    except HTTPException:
        raise
    except Exception as e:
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
