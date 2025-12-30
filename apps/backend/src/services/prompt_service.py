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
from ..db.config import settings

logger = logging.getLogger(__name__)

class PromptService:
    """Service for prompt business logic"""
    
    def create_prompt(
        self,
        prompt_text: str,
        model: Optional[str] = None,
        image_data: Optional[bytes] = None,
        total_uses: int = 0
    ) -> PromptResponse:
        """Create a new prompt with thumbnail (only inserts, no updating)"""
        try:
            prompt = Prompt(
                prompt_text=prompt_text,
                model=model,
                total_uses=total_uses
            )
            
            # Generate thumbnail if image is provided (only for create)
            if image_data:
                thumbnail_result = self._generate_thumbnail(image_data)
                if thumbnail_result["success"]:
                    prompt.thumbnail_data = thumbnail_result["thumbnail_data"]
                    prompt.thumbnail_mime = thumbnail_result["mime_type"]
                    prompt.thumbnail_width = thumbnail_result["width"]
                    prompt.thumbnail_height = thumbnail_result["height"]
                else:
                    logger.warning(f"Failed to generate thumbnail: {thumbnail_result['error']}")
            
            saved_prompt = prompt_repository.create(prompt)
            response = PromptResponse(
                id=saved_prompt.id,
                prompt_text=saved_prompt.prompt_text,
                prompt_hash=saved_prompt.prompt_hash,
                total_uses=saved_prompt.total_uses,
                total_fails=saved_prompt.total_fails,
                first_used_at=saved_prompt.first_used_at,
                last_used_at=saved_prompt.last_used_at,
                model=saved_prompt.model,
                thumbnail_mime=saved_prompt.thumbnail_mime,
                thumbnail_width=saved_prompt.thumbnail_width,
                thumbnail_height=saved_prompt.thumbnail_height
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create prompt - error: {str(e)}", exc_info=True)
            raise
    
    def update_prompt(
        self,
        prompt_text: str,
        model: Optional[str] = None
    ) -> PromptResponse:
        """Update an existing prompt (only updates usage stats, no thumbnail modification)"""
        try:
            prompt = Prompt(
                prompt_text=prompt_text,
                model=model
            )
            
            # Check if prompt exists before attempting update
            if not prompt_repository.exists_by_prompt(prompt):
                raise ValueError(f"Prompt with text '{prompt_text[:50]}{'...' if len(prompt_text) > 50 else ''}' does not exist and cannot be updated")
            
            saved_prompt = prompt_repository.update(prompt)
            response = PromptResponse(
                id=saved_prompt.id,
                prompt_text=saved_prompt.prompt_text,
                prompt_hash=saved_prompt.prompt_hash,
                total_uses=saved_prompt.total_uses,
                total_fails=saved_prompt.total_fails,
                first_used_at=saved_prompt.first_used_at,
                last_used_at=saved_prompt.last_used_at,
                model=saved_prompt.model,
                thumbnail_mime=saved_prompt.thumbnail_mime,
                thumbnail_width=saved_prompt.thumbnail_width,
                thumbnail_height=saved_prompt.thumbnail_height
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to update prompt - error: {str(e)}", exc_info=True)
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
    
    def get_most_failed_prompts(
        self,
        limit: int = 50,
        model: Optional[str] = None
    ) -> List[PromptResponse]:
        """Get most failed prompts"""
        prompts = prompt_repository.get_most_failed(limit, model)
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
    
    def exists_by_text(self, prompt_text: str) -> bool:
        """Check if a prompt exists by its text using the existing exists_by_prompt method"""
        temp_prompt = Prompt(prompt_text=prompt_text)
        return prompt_repository.exists_by_prompt(temp_prompt)
    
    def attempt_save_prompt(self, prompt_text: str, thumbnail_data: Optional[bytes] = None) -> Optional[PromptResponse]:
        """
        Attempt to save a prompt to the database.
        If prompt exists, update usage count. If not, create new prompt with thumbnail.
        
        Args:
            prompt_text: The prompt text to save
            thumbnail_data: Optional thumbnail data for new prompts
            
        Returns:
            PromptResponse if successful, None if failed
        """
        try:
            if self.exists_by_text(prompt_text):
                return self.update_prompt(prompt_text, settings.gemini_model)
            else:
                return self.create_prompt(
                    prompt_text=prompt_text,
                    model=settings.gemini_model,
                    image_data=thumbnail_data,
                    total_uses=1
                )
        except Exception as db_error:
            logger.error(f"Failed to save prompt to database: {db_error}", exc_info=True)
            return None
    
    def cleanup_old_prompts(self, days: int = 90) -> int:
        """Clean up old prompts without thumbnails"""
        return prompt_repository.cleanup_old(days)
    
    def increment_usage_by_id(self, prompt_id: int) -> bool:
        """Increment usage count for a prompt by ID"""
        try:
            return prompt_repository.increment_usage_by_id(prompt_id)
        except Exception as e:
            logger.error(f"Error incrementing usage for prompt ID {prompt_id} - error: {str(e)}", exc_info=True)
            return False
    
    def track_failure_by_id(self, prompt_id: int) -> bool:
        """Track a failure for a prompt by ID"""
        try:
            return prompt_repository.increment_failures_by_id(prompt_id)
        except Exception as e:
            logger.error(f"Error tracking failure for prompt ID {prompt_id} - error: {str(e)}", exc_info=True)
            return False
    
    def track_failure(self, prompt_text: str) -> bool:
        """Track a failure for a prompt"""
        try:
            prompt = Prompt(prompt_text=prompt_text)
            success = prompt_repository.increment_failures(prompt.prompt_hash)
            return success
            
        except Exception as e:
            logger.error(f"Error tracking failure for prompt - error: {str(e)}", exc_info=True)
            return False
    
    def _generate_thumbnail(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """Generate thumbnail from image data"""
        result = ThumbnailGenerator.generate_thumbnail_from_bytes(image_data)
        
        if not result["success"]:
            logger.error(f"Thumbnail generation failed - error: {result['error']}")
        
        return result
    
    def _prompt_to_response(self, prompt: Prompt) -> PromptResponse:
        """Convert Prompt model to PromptResponse"""
        return PromptResponse(
            id=prompt.id,
            prompt_text=prompt.prompt_text,
            prompt_hash=prompt.prompt_hash,
            total_uses=prompt.total_uses,
            total_fails=prompt.total_fails,
            first_used_at=prompt.first_used_at,
            last_used_at=prompt.last_used_at,
            model=prompt.model,
            thumbnail_mime=prompt.thumbnail_mime,
            thumbnail_width=prompt.thumbnail_width,
            thumbnail_height=prompt.thumbnail_height
        )

# Global service instance
prompt_service = PromptService()
