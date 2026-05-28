# ==============================================================================
# JEE MENTOR AI - BACKEND APPLICATION SETTINGS
# ==============================================================================
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # System Environment
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Security & Authentication
    JWT_SECRET: str = "supersecretjwtsecretkeychangeinproduction123456!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database URL
    # If not specified or PostgreSQL is not run, our DB layer falls back to local SQLite automatically
    DATABASE_URL: Optional[str] = None
    
    # Redis Caching
    # If empty or connection fails, the cache layer falls back to a thread-safe local in-memory dict
    REDIS_URL: Optional[str] = None
    
    # Vector DB
    CHROMA_DB_PATH: str = "./data/chroma"
    
    # OCR Priority
    OCR_ENGINE: str = "auto" # auto (tries paddle -> easyocr -> tesseract), paddle, easyocr, tesseract
    
    # Causal LLM Models
    BASE_MODEL_NAME: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    LORA_ADAPTER_PATH: str = "./models/adapters"
    
    # Hugging Face Access keys
    HF_TOKEN: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra env keys to prevent boot failures
    )

# Instantiate global settings
settings = Settings()
