import os
import re
import hashlib
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import pymupdf  # PyMuPDF

from backend.database.connection import SessionLocal
from backend.models import domain as models
from backend.core.config import settings
from backend.services.vector_store_service import add_chunks, delete_chunks_by_document

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Chunks text into overlapping blocks."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += (chunk_size - overlap)
        if start >= len(text):
            break
    return chunks

def extract_entities_from_text(text: str, page_num: int) -> List[Dict[str, Any]]:
    """
    Identifies AUTOSAR architectural entities using engineering patterns:
    - Software Components (SWC)
    - Runnables
    - Interfaces
    - Ports (PPort, RPort, Port)
    - Signals & Data Types
    """
    entities = []
    
    # 1. Software Components
    swc_pattern = r'\b([A-Z][A-Za-z0-9_]*(?:_SWC|Component|Controller|Manager|Handler|Sensor|Actuator|ECU))\b'
    swc_names = []
    for match in re.finditer(swc_pattern, text):
        name = match.group(1)
        swc_names.append(name)
        start_pos = max(0, match.start() - 60)
        end_pos = min(len(text), match.end() + 60)
        excerpt = text[start_pos:end_pos].strip()
        entities.append({
            "type": "Software Component",
            "name": name,
            "description": f"Extracted Software Component identified on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.92
        })
        
    # 2. Runnables
    runnable_pattern = r'\b(Runnable_[A-Za-z0-9_]+|[A-Za-z0-9_]+_Runnable|run_[A-Za-z0-9_]+)\b'
    for match in re.finditer(runnable_pattern, text):
        name = match.group(1)
        start_pos = max(0, match.start() - 60)
        end_pos = min(len(text), match.end() + 60)
        excerpt = text[start_pos:end_pos].strip()
        entities.append({
            "type": "Runnable",
            "name": name,
            "description": f"Extracted Runnable task identified on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.90
        })

    # 3. Interfaces
    if_pattern = r'\b([A-Za-z0-9_]+_IF|[A-Za-z0-9_]+_Interface|SenderReceiver_[A-Za-z0-9_]+|ClientServer_[A-Za-z0-9_]+)\b'
    interface_names = []
    for match in re.finditer(if_pattern, text):
        name = match.group(1)
        interface_names.append(name)
        start_pos = max(0, match.start() - 60)
        end_pos = min(len(text), match.end() + 60)
        excerpt = text[start_pos:end_pos].strip()
        entities.append({
            "type": "Interface",
            "name": name,
            "description": f"Extracted AUTOSAR Interface specification identified on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.88
        })

    # 4. Ports (PPort, RPort, Port_*)
    port_pattern = r'\b(PPort_[A-Za-z0-9_]+|RPort_[A-Za-z0-9_]+|Port_[A-Za-z0-9_]+|InPort_[A-Za-z0-9_]+|OutPort_[A-Za-z0-9_]+)\b'
    for match in re.finditer(port_pattern, text):
        name = match.group(1)
        start_pos = max(0, match.start() - 80)
        end_pos = min(len(text), match.end() + 80)
        excerpt = text[start_pos:end_pos].strip()

        # Determine Port Kind and Direction
        if name.startswith("PPort_") or name.startswith("OutPort_") or re.search(r'\b(?:provides?|provider)\b', excerpt, re.IGNORECASE):
            port_kind = "PPort"
            port_dir = "Output"
        elif name.startswith("RPort_") or name.startswith("InPort_") or re.search(r'\b(?:requires?|receiver)\b', excerpt, re.IGNORECASE):
            port_kind = "RPort"
            port_dir = "Input"
        else:
            port_kind = "Port"
            port_dir = "InOut"

        # Associate interface from nearby text
        associated_if = None
        for if_name in interface_names:
            if if_name in excerpt:
                associated_if = if_name
                break
        if not associated_if:
            if_match = re.search(if_pattern, excerpt)
            if if_match:
                associated_if = if_match.group(1)

        # Associate owning component from nearby text
        owner_comp = None
        for swc in swc_names:
            if swc in excerpt:
                owner_comp = swc
                break

        # Check carried signal
        sig_match = re.search(r'\b(Signal_[A-Za-z0-9_]+|Sig_[A-Za-z0-9_]+|VehicleSpeed|MotorTorque|BatterySOC|EngineRPM)\b', excerpt)
        carried_sig = sig_match.group(1) if sig_match else None

        entities.append({
            "type": "Port",
            "name": name,
            "description": f"Extracted {port_kind} ({port_dir}) identified on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.90,
            "port_kind": port_kind,
            "port_direction": port_dir,
            "interface_name": associated_if,
            "owner_component": owner_comp,
            "carried_signals": carried_sig
        })

    # 5. Signals & Data Types
    signal_pattern = r'\b(Signal_[A-Za-z0-9_]+|Sig_[A-Za-z0-9_]+)\b'
    for match in re.finditer(signal_pattern, text):
        name = match.group(1)
        start_pos = max(0, match.start() - 80)
        end_pos = min(len(text), match.end() + 80)
        excerpt = text[start_pos:end_pos].strip()

        # Extract data type
        dt_match = re.search(r'\b(float32|float64|uint8|uint16|uint32|int8|int16|int32|boolean|bool)\b', excerpt, re.IGNORECASE)
        data_type = dt_match.group(1).lower() if dt_match else "unspecified"

        # Check associated interface
        associated_if = None
        for if_name in interface_names:
            if if_name in excerpt:
                associated_if = if_name
                break

        entities.append({
            "type": "Signal",
            "name": name,
            "description": f"Extracted Signal ({data_type}) identified on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.89,
            "signal_data_type": data_type,
            "interface_name": associated_if
        })

    # Typed declarations e.g. "VehicleSpeed: float32" or "EngineTorque: float64"
    typed_decl_pattern = r'\b([A-Za-z][A-Za-z0-9_]*(?:Speed|Torque|Temp|Voltage|Current|Pressure|SOC|SOH))\s*:\s*(float32|float64|uint8|uint16|uint32|int16|int32|boolean)\b'
    for match in re.finditer(typed_decl_pattern, text, re.IGNORECASE):
        sig_name = f"Signal_{match.group(1)}"
        data_type = match.group(2).lower()
        start_pos = max(0, match.start() - 60)
        end_pos = min(len(text), match.end() + 60)
        excerpt = text[start_pos:end_pos].strip()
        entities.append({
            "type": "Signal",
            "name": sig_name,
            "description": f"Extracted typed signal {match.group(1)} ({data_type}) on page {page_num}",
            "source_page": page_num,
            "source_excerpt": excerpt,
            "confidence": 0.91,
            "signal_data_type": data_type
        })
        
    return entities

def run_enterprise_rule_checks(db: Session, project_id: int, document_id: int, full_text: str):
    """
    Applies enterprise architectural validation rules:
    - Circular dependency detection
    - Insecure IPC verification
    - Missing array bounds checks
    - Undefined or unresolved interfaces
    - Inconsistent signal data types
    """
    findings = []
    
    # Check 1: Insecure IPC or raw pointers
    insecure_patterns = [
        (r'(shared\s+memory|raw\s+pointer|direct\s+memory\s+access|bypassing\s+RTE)', "High", "Insecure IPC / Direct Memory Access: Document references unmanaged inter-process memory communication bypassing AUTOSAR RTE safeguards."),
        (r'(unauthenticated\s+CAN|cleartext\s+IPC|unencrypted\s+bus)', "High", "Insecure Bus Communication: Unauthenticated communication pathway detected without SecOC validation."),
    ]
    for pattern, severity, desc in insecure_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            start_pos = max(0, match.start() - 50)
            end_pos = min(len(full_text), match.end() + 50)
            evidence = full_text[start_pos:end_pos].strip()
            findings.append(models.Finding(
                project_id=project_id,
                document_id=document_id,
                finding_type="Insecure IPC",
                severity=severity,
                description=desc,
                evidence_json=json.dumps({"excerpt": evidence, "matched": match.group(0)}),
                review_status="open"
            ))

    # Check 2: Missing boundary definitions on arrays
    array_matches = re.finditer(r'(\b\w+\s*\[\s*\]|\bunbounded\s+array|\bvariable\s+length\s+buffer)', full_text, re.IGNORECASE)
    for match in array_matches:
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(full_text), match.end() + 50)
        evidence = full_text[start_pos:end_pos].strip()
        findings.append(models.Finding(
            project_id=project_id,
            document_id=document_id,
            finding_type="Missing Boundary Definition",
            severity="Medium",
            description="Missing boundary definition: Unbounded array or dynamic buffer detected without explicit AUTOSAR upper-bound constraint.",
            evidence_json=json.dumps({"excerpt": evidence, "matched": match.group(0)}),
            review_status="open"
        ))
        break # Flag once per document to avoid duplicate alert flooding

    # Check 3: Circular Dependencies in entities
    entities = db.query(models.ArchitectureEntity).filter(
        models.ArchitectureEntity.document_id == document_id,
        models.ArchitectureEntity.entity_type == "Software Component"
    ).all()
    
    if len(entities) >= 2:
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1, e2 = entities[i], entities[j]
                if e1.name in (e2.source_excerpt or "") and e2.name in (e1.source_excerpt or ""):
                    findings.append(models.Finding(
                        project_id=project_id,
                        document_id=document_id,
                        finding_type="Circular Dependency",
                        severity="High",
                        description=f"Potential circular dependency detected between Software Components '{e1.name}' and '{e2.name}'.",
                        evidence_json=json.dumps({"component_a": e1.name, "component_b": e2.name}),
                        review_status="open"
                    ))

    # Check 4: Unresolved Interface (Ports requiring/providing an interface not declared in the project)
    port_entities = db.query(models.ArchitectureEntity).filter(
        models.ArchitectureEntity.document_id == document_id,
        models.ArchitectureEntity.entity_type == "Port"
    ).all()
    all_interfaces = {
        e.name for e in db.query(models.ArchitectureEntity).filter(
            models.ArchitectureEntity.document_id == document_id,
            models.ArchitectureEntity.entity_type == "Interface"
        ).all()
    }
    for p in port_entities:
        if p.interface_name and p.interface_name not in all_interfaces:
            findings.append(models.Finding(
                project_id=project_id,
                document_id=document_id,
                finding_type="Unresolved Interface Reference",
                severity="Medium",
                description=f"Port '{p.name}' references interface '{p.interface_name}', but this interface is not defined in the specification.",
                evidence_json=json.dumps({"port": p.name, "unresolved_interface": p.interface_name, "page": p.source_page}),
                review_status="open"
            ))

    # Check 5: Signal Data Type Incompatibility (e.g. float32 vs float64)
    signals = db.query(models.ArchitectureEntity).filter(
        models.ArchitectureEntity.document_id == document_id,
        models.ArchitectureEntity.entity_type == "Signal"
    ).all()
    sig_types = {}
    for s in signals:
        if s.signal_data_type and s.signal_data_type != "unspecified":
            base_sig = s.name.replace("Signal_", "").replace("Sig_", "")
            if base_sig in sig_types and sig_types[base_sig]["type"] != s.signal_data_type:
                findings.append(models.Finding(
                    project_id=project_id,
                    document_id=document_id,
                    finding_type="Inconsistent Signal Data Type",
                    severity="High",
                    description=f"Inconsistent data type detected for signal '{base_sig}': declared as '{sig_types[base_sig]['type']}' and '{s.signal_data_type}'.",
                    evidence_json=json.dumps({
                        "signal": base_sig,
                        "type_a": sig_types[base_sig]["type"],
                        "type_b": s.signal_data_type,
                        "page_a": sig_types[base_sig]["page"],
                        "page_b": s.source_page
                    }),
                    review_status="open"
                ))
            else:
                sig_types[base_sig] = {"type": s.signal_data_type, "page": s.source_page}

    for f in findings:
        db.add(f)
    db.commit()

def process_document(document_id: int, db: Optional[Session] = None):
    """
    Full document ingestion pipeline:
    1. Parse PDF pages and extract bookmarks/TOC for section headings
    2. Extract text & preserve page numbers
    3. Generate chunks & compute hashes with version and section metadata
    4. Index chunks into ChromaDB
    5. Extract architectural entities (SWCs, Runnables, Interfaces, Ports, Signals)
    6. Extract & link ArchitectureRelationships (PROVIDES, REQUIRES, DEPENDS_ON)
    7. Execute enterprise rule checks & record findings
    8. Update document status to READY
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not doc:
            return

        doc.status = "PROCESSING"
        doc.error_message = None
        db.commit()

        if not os.path.exists(doc.storage_path):
            raise FileNotFoundError(f"Document file not found at: {doc.storage_path}")

        # Clean existing chunks & vectors if reprocessing
        db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == document_id).delete()
        db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == document_id).delete()
        db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.document_id == document_id).delete()
        db.query(models.Finding).filter(models.Finding.document_id == document_id).delete()
        delete_chunks_by_document(doc.project_id, document_id)
        db.commit()

        # Open PDF
        pdf_doc = pymupdf.open(doc.storage_path)
        doc.page_count = len(pdf_doc)

        # 1. Extract TOC / bookmarks for section headings
        page_headings = {}
        try:
            toc = pdf_doc.get_toc()
            if toc:
                for item in toc:
                    if len(item) >= 3:
                        p_num = item[2]
                        if p_num not in page_headings:
                            page_headings[p_num] = item[1].strip()
        except Exception:
            pass
        
        all_chunks_for_db = []
        all_chunks_for_vector = []
        full_document_text = ""
        chunk_index = 0
        extracted_entities_all = []
        version_val = doc.version_label or "1.0"

        for page_idx in range(len(pdf_doc)):
            page_num = page_idx + 1  # 1-indexed
            page_obj = pdf_doc[page_idx]
            page_text = page_obj.get_text()
            full_document_text += f"\n--- Page {page_num} ---\n" + page_text

            # Section heading from TOC or top line of page
            current_heading = page_headings.get(page_num, "")
            if not current_heading:
                lines = [l.strip() for l in page_text.splitlines() if l.strip()]
                for l in lines[:3]:
                    if re.match(r'^(?:[0-9]+\.[0-9]*\s+[A-Za-z0-9\s]+|[A-Z][A-Z\s]{4,})$', l):
                        current_heading = l
                        break
            
            # Extract entities from page text
            page_entities = extract_entities_from_text(page_text, page_num)
            extracted_entities_all.extend(page_entities)
            
            # Chunk page text
            page_chunks = chunk_text(
                page_text, 
                chunk_size=getattr(settings, "CHUNK_SIZE", 1000), 
                overlap=getattr(settings, "CHUNK_OVERLAP", 150)
            )
            
            for c_text in page_chunks:
                c_hash = hashlib.sha256(c_text.encode('utf-8')).hexdigest()
                db_chunk = models.DocumentChunk(
                    project_id=doc.project_id,
                    document_id=doc.id,
                    chunk_index=chunk_index,
                    page_start=page_num,
                    page_end=page_num,
                    section_heading=current_heading or None,
                    version_label=version_val,
                    text_content=c_text,
                    content_hash=c_hash
                )
                all_chunks_for_db.append(db_chunk)
                all_chunks_for_vector.append({
                    "chunk_index": chunk_index,
                    "text_content": c_text,
                    "page_start": page_num,
                    "page_end": page_num,
                    "version_label": version_val,
                    "section_heading": current_heading or ""
                })
                chunk_index += 1

        # Bulk save chunks
        if all_chunks_for_db:
            db.add_all(all_chunks_for_db)
            db.commit()
            
        # Index in ChromaDB
        if all_chunks_for_vector:
            add_chunks(doc.project_id, doc.id, all_chunks_for_vector)

        # Deduplicate & insert extracted entities
        seen_entities = set()
        db_entities = []
        for ent in extracted_entities_all:
            key = (ent["type"], ent["name"])
            if key not in seen_entities:
                seen_entities.add(key)
                db_ent = models.ArchitectureEntity(
                    project_id=doc.project_id,
                    document_id=doc.id,
                    entity_type=ent["type"],
                    name=ent["name"],
                    description=ent["description"],
                    source_page=ent["source_page"],
                    source_excerpt=ent["source_excerpt"],
                    extraction_method="engineering_heuristics",
                    confidence=ent["confidence"],
                    review_status="pending",
                    port_kind=ent.get("port_kind"),
                    port_direction=ent.get("port_direction"),
                    interface_name=ent.get("interface_name"),
                    signal_data_type=ent.get("signal_data_type"),
                    owner_component=ent.get("owner_component"),
                    carried_signals=ent.get("carried_signals"),
                    properties_json=json.dumps({
                        "version": version_val,
                        "port_kind": ent.get("port_kind"),
                        "port_direction": ent.get("port_direction"),
                        "interface_name": ent.get("interface_name"),
                        "signal_data_type": ent.get("signal_data_type"),
                        "owner_component": ent.get("owner_component"),
                        "carried_signals": ent.get("carried_signals")
                    })
                )
                db_entities.append(db_ent)

        if db_entities:
            db.add_all(db_entities)
            db.commit()

        # 6. Extract & link ArchitectureRelationships
        swcs = [e for e in db_entities if e.entity_type == "Software Component"]
        ports = [e for e in db_entities if e.entity_type == "Port"]
        ifaces = [e for e in db_entities if e.entity_type == "Interface"]

        created_relationships = []
        seen_edges = set()

        # Link SWCs to their Ports
        for p in ports:
            # Find owning component
            target_swc = None
            if p.owner_component:
                target_swc = next((s for s in swcs if s.name == p.owner_component), None)
            if not target_swc and swcs:
                # Same page fallback
                target_swc = next((s for s in swcs if s.source_page == p.source_page), swcs[0])
            
            if target_swc:
                rel_type = "PROVIDES" if p.port_direction in ("Output", "InOut") else "REQUIRES"
                edge_key = (target_swc.id, p.id, rel_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    created_relationships.append(models.ArchitectureRelationship(
                        project_id=doc.project_id,
                        document_id=doc.id,
                        source_entity_id=target_swc.id,
                        target_entity_id=p.id,
                        relationship_type=rel_type,
                        source_excerpt=p.source_excerpt,
                        source_page=p.source_page,
                        review_status="pending"
                    ))

            # Link Port to Interface if defined
            if p.interface_name:
                matching_if = next((i for i in ifaces if i.name == p.interface_name), None)
                if matching_if and target_swc:
                    rel_type = "PROVIDES" if p.port_direction in ("Output", "InOut") else "REQUIRES"
                    edge_key = (target_swc.id, matching_if.id, rel_type)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        created_relationships.append(models.ArchitectureRelationship(
                            project_id=doc.project_id,
                            document_id=doc.id,
                            source_entity_id=target_swc.id,
                            target_entity_id=matching_if.id,
                            relationship_type=rel_type,
                            source_excerpt=p.source_excerpt,
                            source_page=p.source_page,
                            review_status="pending"
                        ))

        # SWC-to-SWC Communication relationships
        if len(swcs) >= 2:
            comm_patterns = [
                r'([A-Za-z0-9_]+)\s+(?:communicates\s+with|calls|triggers|sends\s+data\s+to|depends\s+on)\s+([A-Za-z0-9_]+)',
            ]
            for pat in comm_patterns:
                for match in re.finditer(pat, full_document_text):
                    s1_name, s2_name = match.group(1), match.group(2)
                    swc1 = next((s for s in swcs if s.name == s1_name), None)
                    swc2 = next((s for s in swcs if s.name == s2_name), None)
                    if swc1 and swc2 and swc1.id != swc2.id:
                        edge_key = (swc1.id, swc2.id, "DEPENDS_ON")
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            created_relationships.append(models.ArchitectureRelationship(
                                project_id=doc.project_id,
                                document_id=doc.id,
                                source_entity_id=swc1.id,
                                target_entity_id=swc2.id,
                                relationship_type="DEPENDS_ON",
                                source_excerpt=match.group(0),
                                source_page=swc1.source_page or 1,
                                review_status="pending"
                            ))

        if created_relationships:
            db.add_all(created_relationships)
            db.commit()

        # Run enterprise rule validation on the extracted content
        run_enterprise_rule_checks(db, doc.project_id, doc.id, full_document_text)

        pdf_doc.close()
        
        # Mark document as READY
        doc.status = "READY"
        doc.error_message = None
        db.commit()

    except Exception as e:
        if doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()
    finally:
        if own_session:
            db.close()
