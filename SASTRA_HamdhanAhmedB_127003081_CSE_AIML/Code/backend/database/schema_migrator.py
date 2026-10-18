import logging
from sqlalchemy import text
from backend.database.connection import engine
from backend.database.base import Base
from backend.models import domain

logger = logging.getLogger(__name__)

MIGRATION_COLUMNS = {
    "documents": [
        ("governance_state", "VARCHAR DEFAULT 'DRAFT'"),
    ],
    "document_chunks": [
        ("version_label", "VARCHAR DEFAULT '1.0'"),
    ],
    "architecture_entities": [
        ("port_kind", "VARCHAR"),
        ("port_direction", "VARCHAR"),
        ("interface_name", "VARCHAR"),
        ("signal_data_type", "VARCHAR"),
        ("owner_component", "VARCHAR"),
        ("carried_signals", "VARCHAR"),
        ("properties_json", "TEXT"),
    ],
    "analysis_messages": [
        ("review_decision", "VARCHAR"),
        ("reviewer_id", "VARCHAR"),
        ("review_feedback", "TEXT"),
        ("corrected_facts", "TEXT"),
        ("reviewed_at", "DATETIME"),
        ("claims_json", "TEXT"),
        ("grounding_score", "FLOAT"),
        ("confidence_level", "VARCHAR"),
        ("review_recommendation", "VARCHAR"),
    ],
}

def migrate_database():
    """
    Ensures all tables and required columns exist in the SQLite database without
    altering existing data or resetting any records.
    """
    # 1. Create any missing tables (e.g. benchmark_runs)
    Base.metadata.create_all(bind=engine)

    # 2. Add any newly added columns to existing tables
    with engine.connect() as conn:
        for table_name, columns in MIGRATION_COLUMNS.items():
            try:
                # Check existing columns in the table
                result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                existing_cols = {row[1] for row in result}  # row[1] is column name
                
                for col_name, col_type in columns:
                    if col_name not in existing_cols:
                        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                        conn.execute(text(alter_query))
                        conn.commit()
            except Exception as e:
                logger.warning(f"Schema check error on table {table_name}: {e}")
