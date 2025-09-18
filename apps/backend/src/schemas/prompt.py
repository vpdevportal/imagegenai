"""
Pydantic schemas for prompt API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PromptBase(BaseModel):
    """Base prompt schema"""
    prompt_text: str = Field(..., min_length=1, max_length=2000)
    model: Optional[str] = Field(None, max_length=100)

class PromptCreate(PromptBase):
    """Schema for creating a prompt"""
    pass

class PromptResponse(BaseModel):
    """Schema for prompt response (without BLOB data)"""
    id: int
    prompt_text: str
    prompt_hash: str
    total_uses: int
    first_used_at: Optional[datetime]
    last_used_at: Optional[datetime]
    model: Optional[str]
    thumbnail_mime: Optional[str]
    thumbnail_width: Optional[int]
    thumbnail_height: Optional[int]
    
    class Config:
        from_attributes = True

class PromptWithThumbnail(PromptResponse):
    """Schema for prompt with thumbnail data"""
    thumbnail_data: Optional[bytes] = None

class PromptListResponse(BaseModel):
    """Schema for paginated prompt list"""
    prompts: List[PromptResponse]
    total: int
    page: int = 1
    limit: int = 50

class PromptStats(BaseModel):
    """Schema for prompt statistics"""
    total_prompts: int
    total_uses: int
    prompts_with_thumbnails: int
    most_popular_prompt: Optional[str] = None
    most_popular_uses: int = 0

class PromptSearchRequest(BaseModel):
    """Schema for prompt search request"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(20, ge=1, le=100)
