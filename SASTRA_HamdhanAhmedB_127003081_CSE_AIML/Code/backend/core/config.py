import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AUTOSAR AI"
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "supersecretkey12345"
    
    DATABASE_URL: str = "sqlite:///./data/autosar_ai.db"
    
    UPLOAD_DIR: str = "./data/uploads"
    EXPORT_DIR: str = "./data/exports"
    VECTOR_STORE_DIR: str = "./data/vector_store"
    
    MAX_UPLOAD_MB: int = 50
    
    LLM_PROVIDER: str = "ollama"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "llama3.2:3b"
    LLM_BASE_URL: str = "http://localhost:11434"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.5
    
    OCR_ENABLED: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
