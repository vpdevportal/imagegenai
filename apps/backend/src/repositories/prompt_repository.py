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
                with conn.cursor() as cursor:
                    logger.debug(f"Creating new prompt with hash: {prompt.prompt_hash}")
                    cursor.execute("""
                        INSERT INTO prompts (
                            prompt_text, prompt_hash, model,
                            thumbnail_data, thumbnail_mime, thumbnail_width, thumbnail_height,
                            total_uses, total_fails
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        prompt.prompt_text,
                        prompt.prompt_hash,
                        prompt.model,
                        prompt.thumbnail_data,
                        prompt.thumbnail_mime,
                        prompt.thumbnail_width,
                        prompt.thumbnail_height,
                        prompt.total_uses,
                        prompt.total_fails
                    ))
                    result = cursor.fetchone()
                    prompt.id = result['id']
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
                with conn.cursor() as cursor:
                    logger.debug(f"Updating existing prompt with hash: {prompt.prompt_hash}")
                    cursor.execute("""
                        UPDATE prompts 
                        SET total_uses = total_uses + 1,
                            last_used_at = CURRENT_TIMESTAMP
                        WHERE prompt_hash = %s
                    """, (prompt.prompt_hash,))
                    
                    if cursor.rowcount > 0:
                        # Record was updated, get the updated record
                        logger.info(f"Successfully updated existing prompt - hash: {prompt.prompt_hash[:8]}..., rows affected: {cursor.rowcount}")
                        cursor.execute("""
                            SELECT * FROM prompts WHERE prompt_hash = %s
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

    def increment_usage_by_id(self, prompt_id: int) -> bool:
        """Increment usage count for a prompt by ID"""
        logger.info(f"Incrementing usage count for prompt - ID: {prompt_id}")
        
        try:
            with db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE prompts 
                        SET total_uses = total_uses + 1,
                            last_used_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (prompt_id,))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Successfully incremented usage count - ID: {prompt_id}, rows affected: {cursor.rowcount}")
                        conn.commit()
                        return True
                    else:
                        logger.warning(f"No prompt found to increment usage for ID: {prompt_id}")
                        return False
                    
        except Exception as e:
            logger.error(f"Error incrementing usage for prompt - ID: {prompt_id}, error: {str(e)}")
            raise
    
    def increment_failures_by_id(self, prompt_id: int) -> bool:
        """Increment failure count for a prompt by ID"""
        logger.info(f"Incrementing failure count for prompt - ID: {prompt_id}")
        
        try:
            with db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE prompts 
                        SET total_fails = total_fails + 1,
                            last_used_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (prompt_id,))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Successfully incremented failure count - ID: {prompt_id}, rows affected: {cursor.rowcount}")
                        conn.commit()
                        return True
                    else:
                        logger.warning(f"No prompt found to increment failures for ID: {prompt_id}")
                        return False
                    
        except Exception as e:
            logger.error(f"Error incrementing failures for prompt - ID: {prompt_id}, error: {str(e)}")
            raise
    
    def increment_failures(self, prompt_hash: str) -> bool:
        """Increment failure count for a prompt"""
        logger.info(f"Incrementing failure count for prompt - hash: {prompt_hash[:8]}...")
        
        try:
            with db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE prompts 
                        SET total_fails = total_fails + 1,
                            last_used_at = CURRENT_TIMESTAMP
                        WHERE prompt_hash = %s
                    """, (prompt_hash,))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Successfully incremented failure count - hash: {prompt_hash[:8]}..., rows affected: {cursor.rowcount}")
                        conn.commit()
                        return True
                    else:
                        logger.warning(f"No prompt found to increment failures for hash: {prompt_hash}")
                        return False
                    
        except Exception as e:
            logger.error(f"Error incrementing failures for prompt - hash: {prompt_hash[:8]}..., error: {str(e)}")
            raise
    
    def get_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """Get prompt by ID"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
                row = cursor.fetchone()
                return self._row_to_prompt(row) if row else None
    
    def get_by_hash(self, prompt_hash: str) -> Optional[Prompt]:
        """Get prompt by hash"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM prompts WHERE prompt_hash = %s", (prompt_hash,))
                row = cursor.fetchone()
                return self._row_to_prompt(row) if row else None
    
    def exists_by_prompt(self, prompt: Prompt) -> bool:
        """Check if prompt already exists by Prompt object"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM prompts WHERE prompt_hash = %s", (prompt.prompt_hash,))
                row = cursor.fetchone()
                return row is not None
    
    def get_recent(self, limit: int = 50, model: Optional[str] = None) -> List[Prompt]:
        """Get recent prompts (excludes thumbnail_data BLOB for performance)"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                if model:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE model = %s AND thumbnail_data IS NOT NULL
                        ORDER BY last_used_at DESC
                        LIMIT %s
                    """, (model, limit))
                else:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE thumbnail_data IS NOT NULL
                        ORDER BY last_used_at DESC
                        LIMIT %s
                    """, (limit,))
                
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def get_popular(self, limit: int = 50, model: Optional[str] = None) -> List[Prompt]:
        """Get popular prompts (excludes thumbnail_data BLOB for performance)"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                if model:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE model = %s AND thumbnail_data IS NOT NULL
                        ORDER BY total_uses DESC, last_used_at DESC
                        LIMIT %s
                    """, (model, limit))
                else:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE thumbnail_data IS NOT NULL
                        ORDER BY total_uses DESC, last_used_at DESC
                        LIMIT %s
                    """, (limit,))
                
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def get_most_failed(self, limit: int = 50, model: Optional[str] = None) -> List[Prompt]:
        """Get most failed prompts (excludes thumbnail_data BLOB for performance)"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                if model:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE model = %s AND thumbnail_data IS NOT NULL AND total_fails > 0
                        ORDER BY total_fails DESC, last_used_at DESC
                        LIMIT %s
                    """, (model, limit))
                else:
                    cursor.execute("""
                        SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                               first_used_at, last_used_at, model,
                               thumbnail_mime, thumbnail_width, thumbnail_height
                        FROM prompts 
                        WHERE thumbnail_data IS NOT NULL AND total_fails > 0
                        ORDER BY total_fails DESC, last_used_at DESC
                        LIMIT %s
                    """, (limit,))
                
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Prompt]:
        """Search prompts by text (excludes thumbnail_data BLOB for performance)"""
        search_term = f"%{query.lower()}%"
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, prompt_text, prompt_hash, total_uses, total_fails,
                           first_used_at, last_used_at, model,
                           thumbnail_mime, thumbnail_width, thumbnail_height
                    FROM prompts 
                    WHERE LOWER(prompt_text) LIKE %s
                    ORDER BY total_uses DESC, last_used_at DESC
                    LIMIT %s
                """, (search_term, limit))
                
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def get_thumbnail(self, prompt_id: int) -> Optional[bytes]:
        """Get thumbnail data"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT thumbnail_data FROM prompts WHERE id = %s", (prompt_id,))
                row = cursor.fetchone()
                return row['thumbnail_data'] if row and row.get('thumbnail_data') else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                # Total prompts
                cursor.execute("SELECT COUNT(*) as count FROM prompts")
                total_prompts = cursor.fetchone()['count']
                
                # Total uses
                cursor.execute("SELECT SUM(total_uses) as total FROM prompts")
                total_uses = cursor.fetchone()['total'] or 0
                
                # Total failures
                cursor.execute("SELECT SUM(total_fails) as total FROM prompts")
                total_fails = cursor.fetchone()['total'] or 0
                
                # Prompts with thumbnails
                cursor.execute("SELECT COUNT(*) as count FROM prompts WHERE thumbnail_data IS NOT NULL")
                prompts_with_thumbnails = cursor.fetchone()['count']
                
                # Most popular prompt
                cursor.execute("""
                    SELECT prompt_text, total_uses 
                    FROM prompts 
                    ORDER BY total_uses DESC 
                    LIMIT 1
                """)
                most_popular = cursor.fetchone()
                
                # Most failed prompt
                cursor.execute("""
                    SELECT prompt_text, total_fails 
                    FROM prompts 
                    WHERE total_fails > 0
                    ORDER BY total_fails DESC 
                    LIMIT 1
                """)
                most_failed = cursor.fetchone()
                
                return {
                    "total_prompts": total_prompts,
                    "total_uses": total_uses,
                    "total_fails": total_fails,
                    "prompts_with_thumbnails": prompts_with_thumbnails,
                    "most_popular_prompt": most_popular['prompt_text'] if most_popular else None,
                    "most_popular_uses": most_popular['total_uses'] if most_popular else 0,
                    "most_failed_prompt": most_failed['prompt_text'] if most_failed else None,
                    "most_failed_count": most_failed['total_fails'] if most_failed else 0
                }
    
    def delete(self, prompt_id: int) -> bool:
        """Delete a prompt"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    def cleanup_old(self, days: int = 90) -> int:
        """Clean up old prompts without thumbnails"""
        with db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                # PostgreSQL interval syntax: use make_interval or string concatenation
                # Since days is an integer, this is safe from SQL injection
                cursor.execute("""
                    DELETE FROM prompts 
                    WHERE thumbnail_data IS NULL 
                    AND last_used_at < CURRENT_TIMESTAMP - ({} || ' days')::INTERVAL
                """.format(days))
                conn.commit()
                return cursor.rowcount
    
    def _row_to_prompt(self, row) -> Prompt:
        """Convert database row to Prompt model"""
        # Handle cases where thumbnail_data might not be in the SELECT (for performance)
        # psycopg2 RealDictCursor uses dict-like access
        # Helper to safely get value from row
        def safe_get(key, default=None):
            if row and key in row:
                try:
                    value = row[key]
                    return value if value is not None else default
                except (KeyError, IndexError):
                    return default
            return default
        
        thumbnail_data = safe_get('thumbnail_data')
        
        first_used_at = safe_get('first_used_at')
        if first_used_at:
            # PostgreSQL returns datetime objects directly, but handle string conversion if needed
            if isinstance(first_used_at, str):
                try:
                    first_used_at = datetime.fromisoformat(first_used_at.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    first_used_at = None
            elif not isinstance(first_used_at, datetime):
                first_used_at = None
        
        last_used_at = safe_get('last_used_at')
        if last_used_at:
            # PostgreSQL returns datetime objects directly, but handle string conversion if needed
            if isinstance(last_used_at, str):
                try:
                    last_used_at = datetime.fromisoformat(last_used_at.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    last_used_at = None
            elif not isinstance(last_used_at, datetime):
                last_used_at = None
        
        return Prompt(
            id=row['id'],
            prompt_text=row['prompt_text'],
            prompt_hash=row['prompt_hash'],
            total_uses=row['total_uses'],
            total_fails=safe_get('total_fails', 0),
            first_used_at=first_used_at,
            last_used_at=last_used_at,
            model=safe_get('model'),
            thumbnail_data=thumbnail_data,
            thumbnail_mime=safe_get('thumbnail_mime'),
            thumbnail_width=safe_get('thumbnail_width'),
            thumbnail_height=safe_get('thumbnail_height')
        )

# Global repository instance
prompt_repository = PromptRepository()
