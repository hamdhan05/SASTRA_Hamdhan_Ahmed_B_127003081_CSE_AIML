from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.models import domain as models

from pydantic import BaseModel
from typing import Optional

class FindingUpdate(BaseModel):
    severity: Optional[str] = None
    review_status: Optional[str] = None
    reviewer_comments: Optional[str] = None

class FindingReview(BaseModel):
    status: str

router = APIRouter()

@router.get("/projects/{project_id}/findings")
def get_findings(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Finding).filter(models.Finding.project_id == project_id).all()

@router.get("/findings/{finding_id}")
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding

@router.patch("/findings/{finding_id}")
def update_finding(finding_id: int, finding_update: FindingUpdate, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    update_data = finding_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(finding, key, value)
        
    db.commit()
    db.refresh(finding)
    return finding

@router.post("/findings/{finding_id}/review")
def review_finding(finding_id: int, review: FindingReview, db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    finding.review_status = review.status
    db.commit()
    db.refresh(finding)
    return finding
