from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from backend.database.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProjectMembership(Base):
    __tablename__ = "project_memberships"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    sha256_hash = Column(String, nullable=False)
    version_label = Column(String, default="1.0", nullable=True)
    governance_state = Column(String, default="DRAFT")
    status = Column(String, default="UPLOADED")
    page_count = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer, nullable=False)
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)
    section_heading = Column(String, nullable=True)
    version_label = Column(String, default="1.0", nullable=True)
    text_content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ArchitectureEntity(Base):
    __tablename__ = "architecture_entities"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    entity_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    source_excerpt = Column(Text, nullable=True)
    extraction_method = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    review_status = Column(String, default="pending")
    # Extended attributes for Ports & Signals
    port_kind = Column(String, nullable=True)       # e.g., PPort, RPort
    port_direction = Column(String, nullable=True)  # e.g., Input, Output, InOut
    interface_name = Column(String, nullable=True)  # Associated AUTOSAR Interface
    signal_data_type = Column(String, nullable=True)# e.g., float32, uint16
    owner_component = Column(String, nullable=True) # Owning SWC
    carried_signals = Column(String, nullable=True) # Signal names or list
    properties_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ArchitectureRelationship(Base):
    __tablename__ = "architecture_relationships"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    source_entity_id = Column(Integer, ForeignKey("architecture_entities.id"))
    target_entity_id = Column(Integer, ForeignKey("architecture_entities.id"))
    relationship_type = Column(String, nullable=False)
    source_excerpt = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    review_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AnalysisMessage(Base):
    __tablename__ = "analysis_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    # Review & Claim-level verification attributes
    claims_json = Column(Text, nullable=True)
    grounding_score = Column(Float, nullable=True)
    confidence_level = Column(String, nullable=True)
    review_recommendation = Column(String, nullable=True)
    review_decision = Column(String, nullable=True) # Accepted, Rejected, Needs Modification
    reviewer_id = Column(String, nullable=True)
    review_feedback = Column(Text, nullable=True)
    corrected_facts = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    finding_type = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=True)
    review_status = Column(String, default="open")
    reviewer_comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentComparison(Base):
    __tablename__ = "document_comparisons"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    baseline_document_id = Column(Integer, ForeignKey("documents.id"))
    comparison_document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String, default="pending")
    results_json = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    report_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    dataset_version = Column(String, default="1.0")
    retrieval_strategy = Column(String, default="dense") # dense or hybrid
    top_k = Column(Integer, default=5)
    total_queries = Column(Integer, default=0)
    completed_queries = Column(Integer, default=0)
    failed_queries = Column(Integer, default=0)
    mrr = Column(Float, nullable=True)
    hit_rate_at_1 = Column(Float, nullable=True)
    citation_precision = Column(Float, nullable=True)
    supported_claim_rate = Column(Float, nullable=True)
    abstention_accuracy = Column(Float, nullable=True)
    avg_latency_ms = Column(Float, nullable=True)
    results_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
