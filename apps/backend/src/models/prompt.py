"""
Prompt data models
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib
import unicodedata
import re

@dataclass
class Prompt:
    """Prompt data model"""
    id: Optional[int] = None
    prompt_text: str = ""
    prompt_hash: str = ""
    total_uses: int = 0
    total_fails: int = 0
    first_used_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    model: Optional[str] = None
    thumbnail_data: Optional[bytes] = None
    thumbnail_mime: Optional[str] = None
    thumbnail_width: Optional[int] = None
    thumbnail_height: Optional[int] = None
    
    @classmethod
    def normalize_prompt(cls, prompt: str) -> str:
        """Normalize prompt text for consistent hashing"""
        if not prompt:
            return ""
        
        # Unicode normalize
        normalized = unicodedata.normalize("NFKC", prompt)
        
        # Convert to lowercase and strip
        normalized = normalized.lower().strip()
        
        # Collapse multiple whitespace to single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    @classmethod
    def hash_prompt(cls, prompt: str) -> str:
        """Generate SHA256 hash for normalized prompt"""
        normalized = cls.normalize_prompt(prompt)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def __post_init__(self):
        """Auto-generate hash if not provided"""
        if self.prompt_text and not self.prompt_hash:
            self.prompt_hash = self.hash_prompt(self.prompt_text)
