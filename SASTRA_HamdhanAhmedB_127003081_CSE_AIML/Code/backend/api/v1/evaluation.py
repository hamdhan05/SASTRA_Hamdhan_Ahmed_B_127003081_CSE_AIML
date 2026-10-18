from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import json

from backend.database.connection import get_db
from backend.models import domain as models
from backend.services.evaluation_service import run_evaluation_benchmark, load_benchmark_dataset

router = APIRouter()

class BenchmarkRequest(BaseModel):
    strategy: Optional[str] = "dense" # "dense" or "hybrid"
    top_k: Optional[int] = Field(default=5, ge=1, le=10)
    max_queries: Optional[int] = Field(default=None, ge=1, le=50)

@router.get("/projects/{project_id}/evaluation/dataset")
def get_dataset_info(project_id: int):
    dataset = load_benchmark_dataset()
    return {
        "dataset_version": dataset.get("dataset_version", "1.0"),
        "name": dataset.get("name"),
        "total_queries": len(dataset.get("queries", [])),
        "provenance": dataset.get("provenance")
    }

@router.post("/projects/{project_id}/evaluation/run")
def execute_benchmark(project_id: int, req: BenchmarkRequest, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        results = run_evaluation_benchmark(
            db=db,
            project_id=project_id,
            strategy=req.strategy or "dense",
            top_k=req.top_k or 5,
            max_queries=req.max_queries
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation benchmark execution failed: {str(e)}")

@router.get("/projects/{project_id}/evaluation/history")
def get_benchmark_history(project_id: int, db: Session = Depends(get_db)):
    runs = db.query(models.BenchmarkRun).filter(
        models.BenchmarkRun.project_id == project_id
    ).order_by(models.BenchmarkRun.created_at.desc()).all()
    
    return [{
        "id": r.id,
        "dataset_version": r.dataset_version,
        "strategy": r.retrieval_strategy,
        "top_k": r.top_k,
        "total_queries": r.total_queries,
        "mrr": r.mrr,
        "hit_rate_at_1": r.hit_rate_at_1,
        "citation_precision": r.citation_precision,
        "supported_claim_rate": r.supported_claim_rate,
        "abstention_accuracy": r.abstention_accuracy,
        "avg_latency_ms": r.avg_latency_ms,
        "created_at": str(r.created_at)
    } for r in runs]

@router.get("/projects/{project_id}/evaluation/runs/{run_id}")
def get_benchmark_run_detail(project_id: int, run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.BenchmarkRun).filter(
        models.BenchmarkRun.id == run_id,
        models.BenchmarkRun.project_id == project_id
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Benchmark run not found")

    detail = json.loads(run.results_json or "{}")
    return {
        "id": run.id,
        "dataset_version": run.dataset_version,
        "strategy": run.retrieval_strategy,
        "top_k": run.top_k,
        "mrr": run.mrr,
        "hit_rate_at_1": run.hit_rate_at_1,
        "citation_precision": run.citation_precision,
        "supported_claim_rate": run.supported_claim_rate,
        "abstention_accuracy": run.abstention_accuracy,
        "avg_latency_ms": run.avg_latency_ms,
        "created_at": str(run.created_at),
        "results": detail
    }
