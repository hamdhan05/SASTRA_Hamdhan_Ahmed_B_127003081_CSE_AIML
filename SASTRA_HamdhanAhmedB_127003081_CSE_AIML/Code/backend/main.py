from fastapi import FastAPI
from backend.core.config import settings
from backend.database.connection import engine
from backend.database.base import Base
from backend.models import domain

from backend.database.schema_migrator import migrate_database

# Create tables and safely add any new columns
migrate_database()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AUTOSAR HLD Document Analysis Assistant"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/api/v1/health")
def health_check_v1():
    return {"status": "ok", "app": settings.APP_NAME, "version": "v1"}

from backend.api.v1 import projects, documents, sessions, entities, comparisons, findings, reports, diagnostics, settings as platform_settings, evaluation
from backend.database.connection import SessionLocal

# Ensure initial default project exists
def init_default_project():
    db = SessionLocal()
    try:
        proj = db.query(domain.Project).filter(domain.Project.id == 1).first()
        if not proj:
            db_proj = domain.Project(
                id=1,
                name="AUTOSAR Adaptive Platform HLD",
                description="Default engineering workspace for AUTOSAR High-Level Design document analysis",
                status="active"
            )
            db.add(db_proj)
            db.commit()
    except Exception:
        pass
    finally:
        db.close()

init_default_project()

app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(entities.router, prefix="/api/v1", tags=["entities"])
app.include_router(comparisons.router, prefix="/api/v1", tags=["comparisons"])
app.include_router(findings.router, prefix="/api/v1", tags=["findings"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(diagnostics.router, prefix="/api/v1", tags=["diagnostics"])
app.include_router(platform_settings.router, prefix="/api/v1", tags=["settings"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
