from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_by: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    original_filename: str
    version_label: Optional[str] = "1.0"
    governance_state: Optional[str] = "DRAFT"

class DocumentResponse(DocumentBase):
    id: int
    project_id: int
    status: str
    governance_state: Optional[str] = "DRAFT"
    page_count: Optional[int]
    sha256_hash: Optional[str] = None
    metadata_json: Optional[str]
    error_message: Optional[str]
    uploaded_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PageTextResponse(BaseModel):
    chunk_index: int
    page_start: Optional[int]
    page_end: Optional[int]
    text_content: str
