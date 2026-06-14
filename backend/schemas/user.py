"""
User Schemas - Pydantic models for validation and serialization
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "علی احمدی",
                "email": "ali@example.com",
                "phone": "09121234567",
                "password": "SecurePass123!"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    is_active: bool
    is_admin: bool
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
