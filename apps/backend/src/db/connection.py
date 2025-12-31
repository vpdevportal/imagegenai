"""
Database connection and configuration
"""
import os
import psycopg2
import psycopg2.extras
import psycopg2.errors
import logging
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """PostgreSQL database connection manager"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            # Create table
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompts (
                        id SERIAL PRIMARY KEY,
                        prompt_text TEXT NOT NULL,
                        prompt_hash TEXT NOT NULL UNIQUE,
                        total_uses INTEGER NOT NULL DEFAULT 0,
                        total_fails INTEGER NOT NULL DEFAULT 0,
                        first_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        model TEXT,
                        thumbnail_data BYTEA,
                        thumbnail_mime TEXT,
                        thumbnail_width INTEGER,
                        thumbnail_height INTEGER
                    )
                """)
                conn.commit()
            
            # Add total_fails column if it doesn't exist (for existing databases)
            # Check if column exists first to avoid transaction errors
            try:
                with conn.cursor() as check_cursor:
                    check_cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='prompts' AND column_name='total_fails'
                    """)
                    if not check_cursor.fetchone():
                        with conn.cursor() as alter_cursor:
                            alter_cursor.execute("ALTER TABLE prompts ADD COLUMN total_fails INTEGER NOT NULL DEFAULT 0")
                            conn.commit()
                            logger.info("Added total_fails column to prompts table")
            except Exception as e:
                conn.rollback()
                logger.warning(f"Could not add total_fails column (may already exist): {e}")
            
            # Create indexes (these are idempotent with IF NOT EXISTS)
            try:
                with conn.cursor() as index_cursor:
                    index_cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_hash ON prompts (prompt_hash)")
                    index_cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_last_used ON prompts (last_used_at DESC)")
                    index_cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_total_uses ON prompts (total_uses DESC)")
                    index_cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_model ON prompts (model)")
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.warning(f"Error creating indexes (may already exist): {e}")
            
            logger.info("Database initialized")
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = psycopg2.connect(
                self.database_url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

# Global database connection
db_connection = DatabaseConnection()
