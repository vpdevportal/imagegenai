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
    
    def create_or_update(self, prompt: Prompt) -> Prompt:
        """Create or update a prompt"""
        with db_connection.get_connection() as conn:
            # Try to update existing record
            cursor = conn.execute("""
                UPDATE prompts 
                SET total_uses = total_uses + 1,
                    last_used_at = CURRENT_TIMESTAMP,
                    thumbnail_data = COALESCE(?, thumbnail_data),
                    thumbnail_mime = COALESCE(?, thumbnail_mime),
                    thumbnail_width = COALESCE(?, thumbnail_width),
                    thumbnail_height = COALESCE(?, thumbnail_height)
                WHERE prompt_hash = ?
            """, (
                prompt.thumbnail_data,
                prompt.thumbnail_mime,
                prompt.thumbnail_width,
                prompt.thumbnail_height,
                prompt.prompt_hash
            ))
            
            if cursor.rowcount > 0:
                # Record was updated, get the updated record
                cursor = conn.execute("""
                    SELECT * FROM prompts WHERE prompt_hash = ?
                """, (prompt.prompt_hash,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_prompt(row)
            else:
                # Record doesn't exist, insert new one
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
            
            conn.commit()
            return prompt
    
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
