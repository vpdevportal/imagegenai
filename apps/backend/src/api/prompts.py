"""
API endpoints for prompt management
"""
import logging
from fastapi import APIRouter, HTTPException, Query, Path, Form, Body
from fastapi.responses import Response
from typing import Optional, List

from ..services.prompt_service import prompt_service
from ..ai.factory import ImageGeneratorFactory
from ..db.config import settings
from ..schemas.prompt import (
    PromptResponse, PromptWithThumbnail, PromptListResponse, 
    PromptStats, PromptSearchRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.get("/", response_model=PromptListResponse)
async def get_prompts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    model: Optional[str] = Query(None, description="Filter by model"),
    sort_by: str = Query("recent", description="Sort by: recent, popular")
):
    """Get paginated list of prompts"""
    try:
        if sort_by == "popular":
            prompts = prompt_service.get_popular_prompts(limit, model)
        else:
            prompts = prompt_service.get_recent_prompts(limit, model)
        
        # Get total count for pagination
        stats = prompt_service.get_stats()
        
        return PromptListResponse(
            prompts=prompts,
            total=stats.total_prompts,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Failed to get prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompts")

@router.get("/search", response_model=List[PromptResponse])
async def search_prompts(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=10000, description="Maximum results")
):
    """Search prompts by text content"""
    try:
        return prompt_service.search_prompts(query, limit)
    except Exception as e:
        logger.error(f"Failed to search prompts: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/popular", response_model=List[PromptResponse])
async def get_popular_prompts(
    limit: int = Query(50, ge=1, le=10000, description="Maximum results"),
    model: Optional[str] = Query(None, description="Filter by model")
):
    """Get most popular prompts"""
    try:
        return prompt_service.get_popular_prompts(limit, model)
    except Exception as e:
        logger.error(f"Failed to get popular prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve popular prompts")

@router.get("/recent", response_model=List[PromptResponse])
async def get_recent_prompts(
    limit: int = Query(50, ge=1, le=10000, description="Maximum results"),
    model: Optional[str] = Query(None, description="Filter by model")
):
    """Get recently used prompts"""
    try:
        return prompt_service.get_recent_prompts(limit, model)
    except Exception as e:
        logger.error(f"Failed to get recent prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recent prompts")

@router.get("/most-failed", response_model=List[PromptResponse])
async def get_most_failed_prompts(
    limit: int = Query(50, ge=1, le=10000, description="Maximum results"),
    model: Optional[str] = Query(None, description="Filter by model")
):
    """Get most failed prompts"""
    try:
        return prompt_service.get_most_failed_prompts(limit, model)
    except Exception as e:
        logger.error(f"Failed to get most failed prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve most failed prompts")

@router.get("/health")
async def health_check():
    """Health check for prompts API"""
    try:
        stats = prompt_service.get_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "total_prompts": stats.total_prompts,
            "message": "Prompts API is working correctly"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int = Path(..., description="Prompt ID")
):
    """Get a specific prompt by ID"""
    try:
        prompt = prompt_service.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompt")

@router.get("/{prompt_id}/thumbnail")
async def get_prompt_thumbnail(
    prompt_id: int = Path(..., description="Prompt ID")
):
    """Get thumbnail image for a prompt"""
    try:
        thumbnail_data = prompt_service.get_thumbnail(prompt_id)
        if not thumbnail_data:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        # Get prompt info to determine MIME type
        prompt = prompt_service.get_prompt(prompt_id)
        if not prompt or not prompt.thumbnail_mime:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        return Response(
            content=thumbnail_data,
            media_type=prompt.thumbnail_mime,
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get thumbnail for prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve thumbnail")

@router.get("/{prompt_id}/full", response_model=PromptWithThumbnail)
async def get_prompt_with_thumbnail(
    prompt_id: int = Path(..., description="Prompt ID")
):
    """Get prompt with thumbnail data included"""
    try:
        prompt = prompt_service.get_prompt_with_thumbnail(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt with thumbnail {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompt")

@router.get("/stats/overview", response_model=PromptStats)
async def get_prompt_stats():
    """Get database statistics"""
    try:
        return prompt_service.get_stats()
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int = Path(..., description="Prompt ID"),
    prompt_text: str = Body(..., embed=True, min_length=1, max_length=2000, description="New prompt text")
):
    """Update prompt text by ID"""
    try:
        updated = prompt_service.update_prompt_text(prompt_id, prompt_text.strip())
        if not updated:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prompt")

@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: int = Path(..., description="Prompt ID")
):
    """Delete a prompt"""
    try:
        success = prompt_service.delete_prompt(prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prompt")

@router.post("/save", response_model=PromptResponse)
async def save_prompt(
    prompt: str = Form(..., description="Prompt text to save")
):
    """Save a prompt to the database with generated thumbnail"""
    try:
        # Always generate thumbnail from prompt text
        thumbnail_data = None
        try:
            # Use default provider for thumbnail generation
            default_provider = getattr(settings, 'default_ai_provider', 'gemini')
            generator = ImageGeneratorFactory.create(default_provider)
            thumbnail_data, _ = generator.generate_from_text(prompt)
        except Exception as gen_error:
            logger.warning(f"Failed to generate thumbnail: {gen_error}")
            # Continue without thumbnail - attempt_save_prompt handles None thumbnail_data
        
        # Save prompt using existing service logic
        saved_prompt = prompt_service.attempt_save_prompt(prompt, thumbnail_data)
        
        if not saved_prompt:
            raise HTTPException(status_code=500, detail="Failed to save prompt")
        
        return saved_prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_prompts(
    days: int = Query(90, ge=1, le=365, description="Delete prompts older than this many days")
):
    """Clean up old prompts without thumbnails"""
    try:
        deleted_count = prompt_service.cleanup_old_prompts(days)
        return {
            "message": "Cleanup completed",
            "deleted_count": deleted_count,
            "days_threshold": days
        }
    except Exception as e:
        logger.error(f"Failed to cleanup old prompts: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")
