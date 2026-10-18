import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.core.config import settings

router = APIRouter()

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "settings.json")

class PlatformSettings(BaseModel):
    # Extraction parameters
    chunk_size: int = Field(default=1000, ge=200, le=3000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)
    enable_table_extraction: bool = True
    ocr_enabled: bool = False
    
    # Enterprise validation rules
    flag_circular_dependencies: bool = True
    enforce_secure_ipc: bool = True
    require_boundary_definitions: bool = True

def load_persisted_settings() -> PlatformSettings:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return PlatformSettings(**data)
        except Exception:
            pass
    return PlatformSettings()

def save_persisted_settings(config: PlatformSettings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2)
    # Apply to runtime settings
    settings.CHUNK_SIZE = config.chunk_size
    settings.CHUNK_OVERLAP = config.chunk_overlap
    settings.OCR_ENABLED = config.ocr_enabled

@router.get("/settings", response_model=PlatformSettings)
def get_settings():
    return load_persisted_settings()

@router.post("/settings", response_model=PlatformSettings)
def update_settings(new_settings: PlatformSettings):
    if new_settings.chunk_overlap >= new_settings.chunk_size:
        raise HTTPException(
            status_code=400, 
            detail=f"Chunk overlap ({new_settings.chunk_overlap}) must be strictly less than chunk size ({new_settings.chunk_size})."
        )
    save_persisted_settings(new_settings)
    return new_settings
