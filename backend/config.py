"""
Configuration Module - تمام تنظیمات برنامه
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """تنظیمات برنامه از environment variables"""
    
    # App
    APP_NAME: str = "IKCO Store"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ikco_store.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-strong-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")
    SENDER_NAME: str = os.getenv("SENDER_NAME", "IKCO Store")
    
    # Stripe
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # TON
    TON_API_URL: str = os.getenv("TON_API_URL", "https://testnet.toncenter.com/api/v2")
    TON_MAINNET_URL: str = os.getenv("TON_MAINNET_URL", "https://toncenter.com/api/v2")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
