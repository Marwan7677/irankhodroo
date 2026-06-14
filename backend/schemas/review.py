"""
Review Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    product_id: int
    rating: float = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: float
    title: Optional[str]
    comment: Optional[str]
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
