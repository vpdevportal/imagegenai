"""
Prompt service for business logic
"""
import logging
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..models.prompt import Prompt
from ..repositories.prompt_repository import prompt_repository
from ..utils.thumbnail import ThumbnailGenerator
from ..schemas.prompt import PromptResponse, PromptWithThumbnail, PromptStats

logger = logging.getLogger(__name__)

class PromptService:
    """Service for prompt business logic"""
    
    def create_or_update_prompt(
        self,
        prompt_text: str,
        model: Optional[str] = None,
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None
    ) -> PromptResponse:
        """Create or update a prompt with optional thumbnail"""
        try:
            # Create prompt model
            prompt = Prompt(
                prompt_text=prompt_text,
                model=model
            )
            
            # Generate thumbnail if image is provided
            if image_path or image_data:
                thumbnail_result = self._generate_thumbnail(image_path, image_data)
                if thumbnail_result["success"]:
                    prompt.thumbnail_data = thumbnail_result["thumbnail_data"]
                    prompt.thumbnail_mime = thumbnail_result["mime_type"]
                    prompt.thumbnail_width = thumbnail_result["width"]
                    prompt.thumbnail_height = thumbnail_result["height"]
                else:
                    logger.warning(f"Failed to generate thumbnail: {thumbnail_result['error']}")
            
            # Save to database
            saved_prompt = prompt_repository.create_or_update(prompt)
            
            # Convert to response schema
            return PromptResponse(
                id=saved_prompt.id,
                prompt_text=saved_prompt.prompt_text,
                prompt_hash=saved_prompt.prompt_hash,
                total_uses=saved_prompt.total_uses,
                first_used_at=saved_prompt.first_used_at,
                last_used_at=saved_prompt.last_used_at,
                model=saved_prompt.model,
                thumbnail_mime=saved_prompt.thumbnail_mime,
                thumbnail_width=saved_prompt.thumbnail_width,
                thumbnail_height=saved_prompt.thumbnail_height
            )
            
        except Exception as e:
            logger.error(f"Failed to create/update prompt: {e}")
            raise
    
    def get_prompt(self, prompt_id: int) -> Optional[PromptResponse]:
        """Get prompt by ID"""
        prompt = prompt_repository.get_by_id(prompt_id)
        if not prompt:
            return None
        
        return PromptResponse(
            id=prompt.id,
            prompt_text=prompt.prompt_text,
            prompt_hash=prompt.prompt_hash,
            total_uses=prompt.total_uses,
            first_used_at=prompt.first_used_at,
            last_used_at=prompt.last_used_at,
            model=prompt.model,
            thumbnail_mime=prompt.thumbnail_mime,
            thumbnail_width=prompt.thumbnail_width,
            thumbnail_height=prompt.thumbnail_height
        )
    
    def get_prompt_with_thumbnail(self, prompt_id: int) -> Optional[PromptWithThumbnail]:
        """Get prompt with thumbnail data"""
        prompt = prompt_repository.get_by_id(prompt_id)
        if not prompt:
            return None
        
        return PromptWithThumbnail(
            id=prompt.id,
            prompt_text=prompt.prompt_text,
            prompt_hash=prompt.prompt_hash,
            total_uses=prompt.total_uses,
            first_used_at=prompt.first_used_at,
            last_used_at=prompt.last_used_at,
            model=prompt.model,
            thumbnail_mime=prompt.thumbnail_mime,
            thumbnail_width=prompt.thumbnail_width,
            thumbnail_height=prompt.thumbnail_height,
            thumbnail_data=prompt.thumbnail_data
        )
    
    def get_recent_prompts(
        self,
        limit: int = 50,
        model: Optional[str] = None
    ) -> List[PromptResponse]:
        """Get recent prompts"""
        prompts = prompt_repository.get_recent(limit, model)
        return [self._prompt_to_response(prompt) for prompt in prompts]
    
    def get_popular_prompts(
        self,
        limit: int = 50,
        model: Optional[str] = None
    ) -> List[PromptResponse]:
        """Get popular prompts"""
        prompts = prompt_repository.get_popular(limit, model)
        return [self._prompt_to_response(prompt) for prompt in prompts]
    
    def search_prompts(self, query: str, limit: int = 20) -> List[PromptResponse]:
        """Search prompts"""
        prompts = prompt_repository.search(query, limit)
        return [self._prompt_to_response(prompt) for prompt in prompts]
    
    def get_thumbnail(self, prompt_id: int) -> Optional[bytes]:
        """Get thumbnail data"""
        return prompt_repository.get_thumbnail(prompt_id)
    
    def get_stats(self) -> PromptStats:
        """Get database statistics"""
        stats_data = prompt_repository.get_stats()
        return PromptStats(**stats_data)
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """Delete a prompt"""
        return prompt_repository.delete(prompt_id)
    
    def cleanup_old_prompts(self, days: int = 90) -> int:
        """Clean up old prompts without thumbnails"""
        return prompt_repository.cleanup_old(days)
    
    def _generate_thumbnail(
        self,
        image_path: Optional[str],
        image_data: Optional[bytes]
    ) -> Dict[str, Any]:
        """Generate thumbnail from image path or data"""
        if image_path:
            return ThumbnailGenerator.generate_thumbnail(image_path)
        elif image_data:
            return ThumbnailGenerator.generate_thumbnail_from_bytes(image_data)
        else:
            return ThumbnailGenerator._error_result("No image provided")
    
    def _prompt_to_response(self, prompt: Prompt) -> PromptResponse:
        """Convert Prompt model to PromptResponse"""
        return PromptResponse(
            id=prompt.id,
            prompt_text=prompt.prompt_text,
            prompt_hash=prompt.prompt_hash,
            total_uses=prompt.total_uses,
            first_used_at=prompt.first_used_at,
            last_used_at=prompt.last_used_at,
            model=prompt.model,
            thumbnail_mime=prompt.thumbnail_mime,
            thumbnail_width=prompt.thumbnail_width,
            thumbnail_height=prompt.thumbnail_height
        )

# Global service instance
prompt_service = PromptService()
