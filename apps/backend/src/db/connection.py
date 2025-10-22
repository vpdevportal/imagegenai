"""
Database connection and configuration
"""
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """SQLite database connection manager"""
    
    def __init__(self, db_path: str = "data/prompts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_text TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL UNIQUE,
                    total_uses INTEGER NOT NULL DEFAULT 0,
                    total_fails INTEGER NOT NULL DEFAULT 0,
                    first_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    model TEXT,
                    thumbnail_data BLOB,
                    thumbnail_mime TEXT,
                    thumbnail_width INTEGER,
                    thumbnail_height INTEGER
                )
            """)
            
            # Add total_fails column if it doesn't exist (for existing databases)
            try:
                conn.execute("ALTER TABLE prompts ADD COLUMN total_fails INTEGER NOT NULL DEFAULT 0")
                logger.info("Added total_fails column to prompts table")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prompts_hash ON prompts (prompt_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prompts_last_used ON prompts (last_used_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prompts_total_uses ON prompts (total_uses DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prompts_model ON prompts (model)")
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

# Global database connection
db_connection = DatabaseConnection()
