"""
Prompt repository for database operations
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..db.connection import db_connection
from ..models.prompt import Prompt

logger = logging.getLogger(__name__)

class PromptRepository:
    """Repository for prompt database operations"""
    
    def create(self, prompt: Prompt) -> Prompt:
        """Create a new prompt"""
        logger.info(f"Starting create for prompt - hash: {prompt.prompt_hash[:8]}..., text: '{prompt.prompt_text[:50]}{'...' if len(prompt.prompt_text) > 50 else ''}', model: {prompt.model}")
        
        try:
            with db_connection.get_connection() as conn:
                logger.debug(f"Creating new prompt with hash: {prompt.prompt_hash}")
                cursor = conn.execute("""
                    INSERT INTO prompts (
                        prompt_text, prompt_hash, model,
                        thumbnail_data, thumbnail_mime, thumbnail_width, thumbnail_height
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prompt.prompt_text,
                    prompt.prompt_hash,
                    prompt.model,
                    prompt.thumbnail_data,
                    prompt.thumbnail_mime,
                    prompt.thumbnail_width,
                    prompt.thumbnail_height
                ))
                prompt.id = cursor.lastrowid
                logger.info(f"Successfully created new prompt - ID: {prompt.id}, hash: {prompt.prompt_hash[:8]}..., total_uses: {prompt.total_uses}")
                conn.commit()
                logger.debug(f"Database transaction committed for new prompt - ID: {prompt.id}")
                return prompt
                    
        except Exception as e:
            logger.error(f"Error in create for prompt - hash: {prompt.prompt_hash[:8]}..., error: {str(e)}")
            raise
    
    def update(self, prompt: Prompt) -> Prompt:
        """Update an existing prompt (only updates usage stats, no thumbnail modification)"""
        logger.info(f"Starting update for prompt - hash: {prompt.prompt_hash[:8]}..., text: '{prompt.prompt_text[:50]}{'...' if len(prompt.prompt_text) > 50 else ''}', model: {prompt.model}")
        
        try:
            with db_connection.get_connection() as conn:
                logger.debug(f"Updating existing prompt with hash: {prompt.prompt_hash}")
                cursor = conn.execute("""
                    UPDATE prompts 
                    SET total_uses = total_uses + 1,
                        last_used_at = CURRENT_TIMESTAMP
                    WHERE prompt_hash = ?
                """, (prompt.prompt_hash,))
                
                if cursor.rowcount > 0:
                    # Record was updated, get the updated record
                    logger.info(f"Successfully updated existing prompt - hash: {prompt.prompt_hash[:8]}..., rows affected: {cursor.rowcount}")
                    cursor = conn.execute("""
                        SELECT * FROM prompts WHERE prompt_hash = ?
                    """, (prompt.prompt_hash,))
                    row = cursor.fetchone()
                    if row:
                        updated_prompt = self._row_to_prompt(row)
                        logger.info(f"Retrieved updated prompt - ID: {updated_prompt.id}, total_uses: {updated_prompt.total_uses}, last_used_at: {updated_prompt.last_used_at}")
                        conn.commit()
                        logger.debug(f"Database transaction committed for updated prompt - ID: {updated_prompt.id}")
                        return updated_prompt
                    else:
                        logger.error(f"Failed to retrieve updated prompt after update - hash: {prompt.prompt_hash}")
                        conn.rollback()
                        return prompt
                else:
                    logger.warning(f"No prompt found to update with hash: {prompt.prompt_hash}")
                    conn.rollback()
                    return prompt
                    
        except Exception as e:
            logger.error(f"Error in update for prompt - hash: {prompt.prompt_hash[:8]}..., error: {str(e)}")
            raise
    
    def get_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """Get prompt by ID"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
            row = cursor.fetchone()
            return self._row_to_prompt(row) if row else None
    
    def get_by_hash(self, prompt_hash: str) -> Optional[Prompt]:
        """Get prompt by hash"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM prompts WHERE prompt_hash = ?", (prompt_hash,))
            row = cursor.fetchone()
            return self._row_to_prompt(row) if row else None
    
    def exists_by_prompt(self, prompt: Prompt) -> bool:
        """Check if prompt already exists by Prompt object"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM prompts WHERE prompt_hash = ?", (prompt.prompt_hash,))
            row = cursor.fetchone()
            return row is not None
    
    def get_recent(self, limit: int = 50, model: Optional[str] = None) -> List[Prompt]:
        """Get recent prompts"""
        with db_connection.get_connection() as conn:
            if model:
                cursor = conn.execute("""
                    SELECT * FROM prompts 
                    WHERE model = ? AND thumbnail_data IS NOT NULL
                    ORDER BY last_used_at DESC
                    LIMIT ?
                """, (model, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM prompts 
                    WHERE thumbnail_data IS NOT NULL
                    ORDER BY last_used_at DESC
                    LIMIT ?
                """, (limit,))
            
            return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def get_popular(self, limit: int = 50, model: Optional[str] = None) -> List[Prompt]:
        """Get popular prompts"""
        with db_connection.get_connection() as conn:
            if model:
                cursor = conn.execute("""
                    SELECT * FROM prompts 
                    WHERE model = ? AND thumbnail_data IS NOT NULL
                    ORDER BY total_uses DESC, last_used_at DESC
                    LIMIT ?
                """, (model, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM prompts 
                    WHERE thumbnail_data IS NOT NULL
                    ORDER BY total_uses DESC, last_used_at DESC
                    LIMIT ?
                """, (limit,))
            
            return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Prompt]:
        """Search prompts by text"""
        search_term = f"%{query.lower()}%"
        with db_connection.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM prompts 
                WHERE LOWER(prompt_text) LIKE ?
                ORDER BY total_uses DESC, last_used_at DESC
                LIMIT ?
            """, (search_term, limit))
            
            return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def get_thumbnail(self, prompt_id: int) -> Optional[bytes]:
        """Get thumbnail data"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("SELECT thumbnail_data FROM prompts WHERE id = ?", (prompt_id,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with db_connection.get_connection() as conn:
            # Total prompts
            cursor = conn.execute("SELECT COUNT(*) FROM prompts")
            total_prompts = cursor.fetchone()[0]
            
            # Total uses
            cursor = conn.execute("SELECT SUM(total_uses) FROM prompts")
            total_uses = cursor.fetchone()[0] or 0
            
            # Prompts with thumbnails
            cursor = conn.execute("SELECT COUNT(*) FROM prompts WHERE thumbnail_data IS NOT NULL")
            prompts_with_thumbnails = cursor.fetchone()[0]
            
            # Most popular prompt
            cursor = conn.execute("""
                SELECT prompt_text, total_uses 
                FROM prompts 
                ORDER BY total_uses DESC 
                LIMIT 1
            """)
            most_popular = cursor.fetchone()
            
            return {
                "total_prompts": total_prompts,
                "total_uses": total_uses,
                "prompts_with_thumbnails": prompts_with_thumbnails,
                "most_popular_prompt": most_popular[0] if most_popular else None,
                "most_popular_uses": most_popular[1] if most_popular else 0
            }
    
    def delete(self, prompt_id: int) -> bool:
        """Delete a prompt"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def cleanup_old(self, days: int = 90) -> int:
        """Clean up old prompts without thumbnails"""
        with db_connection.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM prompts 
                WHERE thumbnail_data IS NULL 
                AND last_used_at < datetime('now', '-{} days')
            """.format(days))
            conn.commit()
            return cursor.rowcount
    
    def _row_to_prompt(self, row) -> Prompt:
        """Convert database row to Prompt model"""
        return Prompt(
            id=row['id'],
            prompt_text=row['prompt_text'],
            prompt_hash=row['prompt_hash'],
            total_uses=row['total_uses'],
            first_used_at=datetime.fromisoformat(row['first_used_at']) if row['first_used_at'] else None,
            last_used_at=datetime.fromisoformat(row['last_used_at']) if row['last_used_at'] else None,
            model=row['model'],
            thumbnail_data=row['thumbnail_data'],
            thumbnail_mime=row['thumbnail_mime'],
            thumbnail_width=row['thumbnail_width'],
            thumbnail_height=row['thumbnail_height']
        )

# Global repository instance
prompt_repository = PromptRepository()
