"""
Product Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    alt_text: Optional[str]
    is_primary: bool
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    discount_percentage: float = Field(0, ge=0, le=100)
    category_id: int
    
    engine_cc: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    seats: int = Field(5, ge=1, le=10)
    color: Optional[str] = None
    
    stock: int = Field(0, ge=0)
    is_featured: bool = False
    is_presale: bool = False

class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    price: float
    discount_percentage: float
    discount_price: Optional[float]
    category_id: int
    stock: int
    is_active: bool
    is_featured: bool
    is_presale: bool
    average_rating: float
    review_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductDetail(ProductResponse):
    description: Optional[str]
    sku: Optional[str]
    engine_cc: Optional[str]
    transmission: Optional[str]
    fuel_type: Optional[str]
    seats: int
    color: Optional[str]
    images: List[ProductImageResponse]
    updated_at: datetime

class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    search: Optional[str] = None
    is_presale: Optional[bool] = None
    sort_by: Optional[str] = Field("newest", regex="^(newest|price_asc|price_desc|rating)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
