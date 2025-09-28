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
        logger.info(f"Starting prompt creation - prompt_length: {len(prompt_text)}, model: {model}, has_image_data: {image_data is not None}")
        
        try:
            # Create prompt model
            logger.debug("Creating prompt model")
            prompt = Prompt(
                prompt_text=prompt_text,
                model=model,
                total_uses=total_uses
            )
            logger.debug(f"Prompt model created - hash: {prompt.prompt_hash}")
            
            # Generate thumbnail if image is provided (only for create)
            if image_data:
                logger.debug("Generating thumbnail for new prompt")
                thumbnail_result = self._generate_thumbnail(image_data)
                if thumbnail_result["success"]:
                    prompt.thumbnail_data = thumbnail_result["thumbnail_data"]
                    prompt.thumbnail_mime = thumbnail_result["mime_type"]
                    prompt.thumbnail_width = thumbnail_result["width"]
                    prompt.thumbnail_height = thumbnail_result["height"]
                    logger.info(f"Thumbnail generated successfully - size: {thumbnail_result['width']}x{thumbnail_result['height']}, mime: {thumbnail_result['mime_type']}")
                else:
                    logger.warning(f"Failed to generate thumbnail: {thumbnail_result['error']}")
            else:
                logger.debug("No image provided, creating prompt without thumbnail")
            
            # Save to database using create (will create new record)
            logger.debug("Creating prompt in database")
            saved_prompt = prompt_repository.create(prompt)
            logger.info(f"Prompt created successfully - id: {saved_prompt.id}, total_uses: {saved_prompt.total_uses}")
            
            # Convert to response schema
            logger.debug("Converting to response schema")
            response = PromptResponse(
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
            
            logger.info(f"Prompt creation completed successfully - id: {response.id}")
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
        logger.info(f"Starting prompt update - prompt_length: {len(prompt_text)}, model: {model}")
        
        try:
            # Create prompt model (without thumbnail data)
            logger.debug("Creating prompt model for update")
            prompt = Prompt(
                prompt_text=prompt_text,
                model=model
            )
            logger.debug(f"Prompt model created - hash: {prompt.prompt_hash}")
            
            # Check if prompt exists before attempting update
            if not prompt_repository.exists_by_prompt(prompt):
                logger.warning(f"Prompt does not exist, cannot update - hash: {prompt.prompt_hash}")
                raise ValueError(f"Prompt with text '{prompt_text[:50]}{'...' if len(prompt_text) > 50 else ''}' does not exist and cannot be updated")
            
            # Update in database (without modifying thumbnail)
            logger.debug("Updating prompt in database (usage stats only)")
            saved_prompt = prompt_repository.update(prompt)
            logger.info(f"Prompt updated successfully - id: {saved_prompt.id}, total_uses: {saved_prompt.total_uses}")
            
            # Convert to response schema
            logger.debug("Converting to response schema")
            response = PromptResponse(
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
            
            logger.info(f"Prompt update completed successfully - id: {response.id}")
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
        logger.debug(f"Checking if prompt exists by text - length: {len(prompt_text)}")
        
        # Create a temporary Prompt object to use with exists_by_prompt
        temp_prompt = Prompt(prompt_text=prompt_text)
        exists = prompt_repository.exists_by_prompt(temp_prompt)
        
        logger.debug(f"Prompt exists check result: {exists}")
        return exists
    
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
        logger.debug("Attempting to save prompt to database")
        
        try:
            if self.exists_by_text(prompt_text):
                logger.info("Prompt already exists in database")
                return self.update_prompt(prompt_text, settings.gemini_model)
            else:
                logger.info("Prompt does not exist in database")
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
    
    def _generate_thumbnail(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """Generate thumbnail from image data"""
        logger.debug(f"Generating thumbnail from image data - size: {len(image_data)} bytes")
        result = ThumbnailGenerator.generate_thumbnail_from_bytes(image_data)
        
        if result["success"]:
            logger.debug(f"Thumbnail generation successful - size: {result['width']}x{result['height']}, mime: {result['mime_type']}")
        else:
            logger.error(f"Thumbnail generation failed - error: {result['error']}")
        
        return result
    
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
