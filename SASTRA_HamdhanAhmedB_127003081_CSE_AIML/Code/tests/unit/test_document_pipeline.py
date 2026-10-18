import os
import io
import pymupdf
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models
from backend.services.document_service import process_document, chunk_text, extract_entities_from_text
from backend.services.vector_store_service import search_chunks

client = TestClient(app)

def create_synthetic_pdf(filepath: str):
    """Generates a small synthetic test PDF with known architectural keywords."""
    doc = pymupdf.open()
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        "AUTOSAR Software Architecture High-Level Specification.\n"
        "Software Component PowertrainManager_SWC handles engine operations.\n"
        "It communicates with BatteryManagement_SWC and calls Runnable_MonitorTemp.\n"
        "The interface used is SensorReceiver_IF.\n"
    )
    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        "Safety and Boundary Constraints:\n"
        "A variable length buffer torque_data[] is allocated without fixed limits.\n"
        "Warning: Some debug routines use shared memory bypassing RTE to communicate with sensors.\n"
    )
    doc.save(filepath)
    doc.close()

def test_chunking_and_entity_extraction():
    sample_text = "The component EngineControl_SWC triggers Runnable_StepTorque through Port_IF."
    chunks = chunk_text(sample_text, chunk_size=100, overlap=20)
    assert len(chunks) >= 1
    
    entities = extract_entities_from_text(sample_text, page_num=1)
    types = [e["type"] for e in entities]
    names = [e["name"] for e in entities]
    assert "Software Component" in types
    assert "EngineControl_SWC" in names

def test_full_document_ingestion_and_cleanup(tmp_path):
    test_pdf_path = str(tmp_path / "test_spec.pdf")
    create_synthetic_pdf(test_pdf_path)
    
    db = SessionLocal()
    try:
        # Create a test project
        proj = models.Project(name="Test Pipeline Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)
        
        # Create a test document record
        doc = models.Document(
            project_id=proj.id,
            original_filename="test_spec.pdf",
            storage_path=test_pdf_path,
            sha256_hash="dummyhash12345",
            status="UPLOADED"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id
        proj_id = proj.id
        
        # Run processing pipeline
        process_document(doc_id, db=db)
        
        # Verify status is READY and page_count == 2
        refreshed_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        assert refreshed_doc.status == "READY"
        assert refreshed_doc.page_count == 2
        
        # Verify chunks created
        chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc_id).all()
        assert len(chunks) >= 2
        assert all(c.page_start in [1, 2] for c in chunks)
        
        # Verify entities extracted
        entities = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == doc_id).all()
        ent_names = [e.name for e in entities]
        assert any("PowertrainManager_SWC" in n for n in ent_names)
        
        # Verify enterprise rule checks generated findings (Insecure IPC & Missing Boundary)
        findings = db.query(models.Finding).filter(models.Finding.document_id == doc_id).all()
        f_types = [f.finding_type for f in findings]
        assert "Insecure IPC" in f_types or "Missing Boundary Definition" in f_types
        
        # Verify Vector Store search
        search_res = search_chunks(project_id=proj_id, query="PowertrainManager_SWC", top_k=2)
        assert search_res and len(search_res["documents"][0]) > 0
        
        # Test document deletion endpoint clean up
        del_resp = client.delete(f"/api/v1/documents/{doc_id}")
        assert del_resp.status_code == 200
        
        # Verify chunks and entities deleted
        assert db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc_id).count() == 0
        assert db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == doc_id).count() == 0
        assert db.query(models.Finding).filter(models.Finding.document_id == doc_id).count() == 0
        assert db.query(models.Document).filter(models.Document.id == doc_id).count() == 0
        
    finally:
        db.close()
