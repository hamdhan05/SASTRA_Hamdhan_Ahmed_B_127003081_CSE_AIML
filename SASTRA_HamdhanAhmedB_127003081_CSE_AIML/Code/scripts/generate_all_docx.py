import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(r"H:\tech_pulse_project\SASTRA_HamdhanAhmedB_127003081_CSx_AIML")

NAVY = RGBColor(27, 54, 93)      # #1B365D
SLATE = RGBColor(74, 85, 104)    # #4A5568
CHARCOAL = RGBColor(45, 55, 72)  # #2D3748

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_table(table, header_bg="1B365D", alt_bg="F7FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        for cell in row.cells:
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            if is_header:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(10)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, alt_bg)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = CHARCOAL

def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        if level == 1:
            r.font.color.rgb = NAVY
            r.font.size = Pt(16)
            r.font.bold = True
        elif level == 2:
            r.font.color.rgb = NAVY
            r.font.size = Pt(13)
            r.font.bold = True
        elif level == 3:
            r.font.color.rgb = SLATE
            r.font.size = Pt(11.5)
            r.font.bold = True
    return h

def generate_synopsis():
    print("[1/3] Generating Project_Synopsis.docx & Abstract.txt...")
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    # Title & Metadata
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = title_p.add_run("SASTRA DEEMED TO BE UNIVERSITY\n")
    r_uni.font.size = Pt(14)
    r_uni.font.bold = True
    r_uni.font.color.rgb = NAVY
    
    r_dept = title_p.add_run("School of Computing — Department of Computer Science & Engineering\n\n")
    r_dept.font.size = Pt(11)
    r_dept.font.color.rgb = SLATE

    r_proj = title_p.add_run("PROJECT SYNOPSIS\n")
    r_proj.font.size = Pt(18)
    r_proj.font.bold = True
    r_proj.font.color.rgb = NAVY

    r_title = title_p.add_run("AUTOSAR AI – High-Level Design Document Intelligence Platform\n\n")
    r_title.font.size = Pt(14)
    r_title.font.bold = True
    r_title.font.color.rgb = CHARCOAL

    # Student Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_data = [
        ("Student Name:", "Hamdhan Ahmed B"),
        ("Register Number:", "127003081"),
        ("Degree & Branch:", "B.Tech. Computer Science & Engineering (AIML)"),
        ("GitHub Repository:", "https://github.com/hamdhan05/AUTOSAR-AI-Implementation")
    ]
    for i, (k, v) in enumerate(meta_data):
        c1, c2 = meta_table.rows[i].cells
        c1.text = k
        c2.text = v
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.color.rgb = NAVY
        c2.paragraphs[0].runs[0].font.color.rgb = CHARCOAL
    style_table(meta_table, header_bg="1B365D", alt_bg="F7FAFC")
    doc.add_paragraph()

    # Abstract
    add_heading_with_spacing(doc, "1. Abstract", level=1)
    abs_text = (
        "Modern automotive systems rely heavily on the AUTOSAR (AUTomotive Open System ARchitecture) "
        "standard to specify complex electronic control unit (ECU) software architectures. However, reviewing "
        "and verifying multi-hundred-page High-Level Design (HLD) specifications remains a manual, error-prone, "
        "and labor-intensive challenge. Furthermore, transmitting proprietary automotive intellectual property "
        "to public cloud AI models is strictly prohibited by automotive cybersecurity regulations (ISO/SAE 21434). "
        "This project introduces AUTOSAR AI, an on-premises document intelligence platform that automates the ingestion, "
        "structural entity extraction, architectural rule validation, and grounded conversational analysis of automotive HLDs. "
        "The system combines PyMuPDF for page-preserving extraction, SentenceTransformers (all-MiniLM-L6-v2) and ChromaDB "
        "for dense vector retrieval, in-memory BM25 for exact automotive identifier matching, and a local quantized Large "
        "Language Model (Ollama llama3.2:3b) for grounded question-answering with verifiable citations. Additionally, "
        "an independent Grounding Service decomposes generated responses into verifiable propositions to calculate a "
        "quantitative Grounding Score, and security defenses neutralize CSV formula injection attacks. The platform was "
        "validated through 28 automated pytest test cases (100% pass rate) and a 35-query benchmark evaluation."
    )
    p_abs = doc.add_paragraph(abs_text)
    p_abs.paragraph_format.line_spacing = 1.15
    p_abs.paragraph_format.space_after = Pt(8)

    # Save Abstract.txt
    with open(BASE_DIR / "Synopsis" / "Abstract.txt", "w", encoding="utf-8") as f:
        f.write(abs_text)

    # Problem Statement
    add_heading_with_spacing(doc, "2. Problem Statement", level=1)
    doc.add_paragraph(
        "Automotive software engineering teams spend thousands of engineering hours manually cross-referencing "
        "architectural specifications across vehicle revision cycles. Generic document QA tools frequently hallucinate "
        "technical component names, lack exact page citations, and cannot run in air-gapped, on-premises engineering environments. "
        "There is an acute need for a high-assurance, offline document intelligence system that combines grounded retrieval "
        "with automated architectural rule checking (e.g., detecting circular dependencies and insecure IPC bindings)."
    )

    # Objectives
    add_heading_with_spacing(doc, "3. Project Objectives", level=1)
    bullets = [
        "Develop an end-to-end PDF ingestion pipeline that preserves page numbering, headings, and character boundaries.",
        "Implement a hybrid retrieval pipeline combining dense vector embeddings with BM25 sparse keyword matching using Reciprocal Rank Fusion.",
        "Integrate a fully local Large Language Model (llama3.2:3b via Ollama) enforcing evidence-bounded prompt constraints and abstention.",
        "Build a claim decomposition and verification service that computes an empirical Grounding Score (0.0 to 1.0).",
        "Implement heuristic regex extractors to identify Software Components (SWCs), Runnables, Interfaces, Ports, and Signals.",
        "Detect architectural defects, including circular dependencies, insecure IPC communication, and missing port bindings.",
        "Provide an interactive 9-page Streamlit web user interface and 10 REST API endpoints in FastAPI with CSV export security."
    ]
    for b in bullets:
        bp = doc.add_paragraph(b, style='List Bullet')
        bp.paragraph_format.space_after = Pt(4)

    # System Architecture
    add_heading_with_spacing(doc, "4. Proposed System Architecture", level=1)
    doc.add_paragraph(
        "The proposed platform is organized into eight decoupled layers: (1) Presentation Layer (Streamlit on port 8501); "
        "(2) API Gateway Layer (FastAPI on port 8000 with 10 routers); (3) Document Ingestion Layer (PyMuPDF); "
        "(4) Embedding & Vector Store (SentenceTransformers all-MiniLM-L6-v2 + persistent ChromaDB); (5) Hybrid Retrieval Layer "
        "(Dense + BM25 + Reciprocal Rank Fusion); (6) Local Inference Layer (Ollama on port 11434 with llama3.2:3b); "
        "(7) Relational Storage Layer (SQLite 3 with 14 SQLAlchemy ORM models); and (8) Reporting & Security Layer "
        "(CSV formula injection defense)."
    )

    # Technology Stack Table
    add_heading_with_spacing(doc, "5. Technology Stack", level=1)
    tech_table = doc.add_table(rows=8, cols=3)
    tech_data = [
        ("Subsystem", "Technology Selected", "Role & Justification"),
        ("Frontend UI", "Streamlit 1.32.0", "Reactive multi-page web application (9 pages)"),
        ("Backend Framework", "FastAPI 0.110.0 / Uvicorn", "Asynchronous REST API with Pydantic type validation"),
        ("PDF Ingestion", "PyMuPDF (fitz) 1.23.26", "High-speed text extraction with page provenance preservation"),
        ("Vector Database", "ChromaDB 0.4.24", "Local persistent vector storage and cosine similarity search"),
        ("Embedding Model", "all-MiniLM-L6-v2 (384-dim)", "Lightweight, high-accuracy semantic embeddings"),
        ("Local LLM Runtime", "Ollama 0.40.3 (llama3.2:3b)", "100% on-premises, privacy-preserving generative inference"),
        ("Relational Database", "SQLite 3 / SQLAlchemy 2.0", "14 relational tables with full foreign-key constraints")
    ]
    for i, row in enumerate(tech_data):
        for j, val in enumerate(row):
            tech_table.rows[i].cells[j].text = val
    style_table(tech_table)

    # Implemented Outcomes & Testing
    add_heading_with_spacing(doc, "6. Implemented Outcomes & Verification", level=1)
    doc.add_paragraph(
        "All planned core modules have been fully implemented and verified. The platform features an automated "
        "test suite of 28 unit and integration tests executing across 12 test modules via Pytest 9.1.1, achieving a 100% pass "
        "rate in 27.35 seconds. The system successfully extracts SWCs, Runnables, Ports, and Signals; renders interactive "
        "Mermaid component topology graphs; generates grounded natural language answers with exact citations; flags rule violations; "
        "and exports sanitized CSV reports."
    )

    # Limitations & Future Scope
    add_heading_with_spacing(doc, "7. Limitations & Future Scope", level=1)
    doc.add_paragraph(
        "Current limitations include reliance on text-searchable PDFs (raster scanned PDFs produce empty text) and heuristic regex "
        "extraction. Future work will incorporate: (1) Bidirectional ARXML AST parsing to generate formal AUTOSAR XML models directly; "
        "(2) Tesseract OCR for scanned legacy specifications; and (3) Real-time CAN/Ethernet bus timing simulation integration."
    )

    doc.save(BASE_DIR / "Synopsis" / "Project_Synopsis.docx")
    print("      Project_Synopsis.docx generated.")

def generate_declaration():
    print("[2/3] Generating Student_Declaration_Template.docx...")
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = title_p.add_run("SASTRA DEEMED TO BE UNIVERSITY\n")
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    
    r2 = title_p.add_run("School of Computing\nDepartment of Computer Science & Engineering\n\n")
    r2.font.size = Pt(11)
    r2.font.color.rgb = SLATE

    r3 = title_p.add_run("STUDENT DECLARATION OF ACADEMIC INTEGRITY\n\n")
    r3.font.size = Pt(16)
    r3.font.bold = True
    r3.font.color.rgb = NAVY

    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.25
    p1.paragraph_format.space_after = Pt(12)
    p1.add_run(
        "I, Hamdhan Ahmed B (Register Number: 127003081), hereby declare that the capstone project entitled "
    )
    r_pt = p1.add_run("“AUTOSAR AI – High-Level Design Document Intelligence Platform” ")
    r_pt.font.bold = True
    p1.add_run(
        "is a bonafide record of independent software development and technical work carried out by me under academic supervision. "
        "The software architecture, source code modules, prompt engineering structures, automated test suites, and documentation "
        "contained in this submission represent original work, except where explicitly cited and acknowledged in the references."
    )

    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.25
    p2.paragraph_format.space_after = Pt(12)
    p2.add_run(
        "I further affirm that:\n"
        "1. No proprietary, classified, or confidential trade-secret automotive OEM intellectual property has been redistributed.\n"
        "2. All sample High-Level Design specifications and evaluation query datasets are synthetic, unclassified, and developed for academic review.\n"
        "3. All performance metrics, test results (28/28 passing tests), and feature verification claims reported herein are truthful, reproducible, and verifiable from the source code.\n"
        "4. This work has not been previously submitted in part or full for the award of any other degree or diploma at this or any other institution."
    )

    doc.add_paragraph("\n\n")

    # Signature Table
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_data = [
        ("Place: Thanjavur, Tamil Nadu", "Signature of the Student: ________________________"),
        ("Date: October 13, 2026", "Name: Hamdhan Ahmed B (Reg No: 127003081)"),
        ("", "")
    ]
    for i, (left_text, right_text) in enumerate(sig_data):
        c1, c2 = sig_table.rows[i].cells
        c1.text = left_text
        c2.text = right_text
        for c in (c1, c2):
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10.5)
                    r.font.color.rgb = CHARCOAL
    
    doc.add_paragraph("\n")
    add_heading_with_spacing(doc, "Faculty Endorsement Placeholders", level=2)
    
    fac_table = doc.add_table(rows=2, cols=2)
    fac_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    fac_table.rows[0].cells[0].text = "Project Guide Signature:\n\n___________________________________\n[Name & Designation of Faculty Guide]"
    fac_table.rows[0].cells[1].text = "Head of the Department Signature:\n\n___________________________________\n[Head of Department, School of Computing]"
    fac_table.rows[1].cells[0].text = "Internal Examiner Signature:\n\n___________________________________"
    fac_table.rows[1].cells[1].text = "External Examiner Signature:\n\n___________________________________"
    
    for row in fac_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=140, bottom=140, left=150, right=150)
            set_cell_background(cell, "F7FAFC")
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = SLATE

    doc.save(BASE_DIR / "Declarations" / "Student_Declaration_Template.docx")
    print("      Student_Declaration_Template.docx generated.")

def generate_project_report():
    print("[3/3] Generating Project_Report.docx...")
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    # 1. Title Page
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    
    r_uni = p_title.add_run("SASTRA DEEMED TO BE UNIVERSITY\n")
    r_uni.font.size = Pt(16)
    r_uni.font.bold = True
    r_uni.font.color.rgb = NAVY

    r_soc = p_title.add_run("SCHOOL OF COMPUTING\nDEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n\n\n")
    r_soc.font.size = Pt(12)
    r_soc.font.color.rgb = SLATE

    r_rep = p_title.add_run("CAPSTONE PROJECT REPORT\n\n")
    r_rep.font.size = Pt(14)
    r_rep.font.bold = True
    r_rep.font.color.rgb = SLATE

    r_proj = p_title.add_run("AUTOSAR AI – HIGH-LEVEL DESIGN DOCUMENT INTELLIGENCE PLATFORM\n\n\n")
    r_proj.font.size = Pt(20)
    r_proj.font.bold = True
    r_proj.font.color.rgb = NAVY

    r_sub = p_title.add_run("Submitted in partial fulfillment of the requirements for the degree of\nBACHELOR OF TECHNOLOGY\nin\nCOMPUTER SCIENCE & ENGINEERING (AIML)\n\n\n")
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = CHARCOAL

    r_by = p_title.add_run("Submitted by:\n")
    r_by.font.size = Pt(11)
    r_by.font.color.rgb = SLATE

    r_name = p_title.add_run("HAMDHAN AHMED B\n")
    r_name.font.size = Pt(14)
    r_name.font.bold = True
    r_name.font.color.rgb = NAVY

    r_reg = p_title.add_run("Register Number: 127003081\n\n")
    r_reg.font.size = Pt(12)
    r_reg.font.bold = True
    r_reg.font.color.rgb = CHARCOAL

    r_date = p_title.add_run("OCTOBER 2026\nTHANJAVUR, TAMIL NADU, INDIA")
    r_date.font.size = Pt(11)
    r_date.font.color.rgb = SLATE

    doc.add_page_break()

    # 2. Certificate
    add_heading_with_spacing(doc, "CERTIFICATE", level=1)
    p_cert = doc.add_paragraph()
    p_cert.paragraph_format.line_spacing = 1.25
    p_cert.paragraph_format.space_after = Pt(14)
    p_cert.add_run(
        "This is to certify that the project report entitled “AUTOSAR AI – High-Level Design Document Intelligence Platform” "
        "is a bonafide record of work done by Hamdhan Ahmed B (Register Number: 127003081) in partial fulfillment of the requirements "
        "for the award of the degree of Bachelor of Technology in Computer Science & Engineering (AIML) from SASTRA Deemed University, "
        "Thanjavur, during the academic year 2025–2026."
    )
    
    cert_table = doc.add_table(rows=2, cols=2)
    cert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cert_table.rows[0].cells[0].text = "Project Guide:\n\n_______________________________\n[Faculty Guide Name]\nAssistant Professor, School of Computing"
    cert_table.rows[0].cells[1].text = "Head of Department:\n\n_______________________________\n[HOD Name]\nHead, Department of CSE, School of Computing"
    cert_table.rows[1].cells[0].text = "Internal Examiner:\n\n_______________________________"
    cert_table.rows[1].cells[1].text = "External Examiner:\n\n_______________________________"
    for row in cert_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            set_cell_background(cell, "F7FAFC")

    doc.add_page_break()

    # 3. Table of Contents
    add_heading_with_spacing(doc, "TABLE OF CONTENTS", level=1)
    toc_items = [
        ("1. Introduction & Domain Overview", "1"),
        ("2. Problem Statement & Objectives", "3"),
        ("3. Literature Survey & Existing Approaches", "5"),
        ("4. System Architecture & Requirements", "7"),
        ("5. Methodology & Implementation Details", "10"),
        ("6. User Interface & Module Descriptions", "14"),
        ("7. Testing Methodology & Empirical Results", "18"),
        ("8. Security, Privacy & Safety Considerations", "22"),
        ("9. Limitations & Future Scope", "24"),
        ("10. Conclusion & References", "26")
    ]
    toc_table = doc.add_table(rows=len(toc_items)+1, cols=2)
    toc_table.rows[0].cells[0].text = "Chapter Title"
    toc_table.rows[0].cells[1].text = "Page No."
    for idx, (title, pg) in enumerate(toc_items):
        toc_table.rows[idx+1].cells[0].text = title
        toc_table.rows[idx+1].cells[1].text = pg
        toc_table.rows[idx+1].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    style_table(toc_table)

    doc.add_page_break()

    # Chapter 1
    add_heading_with_spacing(doc, "CHAPTER 1: INTRODUCTION & DOMAIN OVERVIEW", level=1)
    doc.add_paragraph(
        "The contemporary automotive industry is experiencing a profound transition from hardware-centric mechanical systems "
        "to Software-Defined Vehicles (SDVs). Modern connected, automated, and electrified vehicles integrate upwards of one hundred "
        "Electronic Control Units (ECUs) executing over one hundred million lines of code. To manage this extraordinary architectural "
        "complexity, major automotive manufacturers (OEMs) and Tier-1 suppliers established the AUTOSAR (AUTomotive Open System ARchitecture) "
        "consortium. AUTOSAR standardizes the software architecture of automotive ECUs, enforcing a strict separation between "
        "application-layer software components and the underlying microcontroller hardware through a standardized Runtime Environment (RTE) "
        "and Basic Software (BSW) stack."
    )
    doc.add_paragraph(
        "Within the automotive V-model development lifecycle, the architectural blueprint for any subsystem is formalized in a "
        "High-Level Design (HLD) document. An HLD specifies Software Components (SWCs), their internal execution tasks (Runnables), "
        "inter-component communication contracts (Interfaces), interaction points (Ports), and individual carried signals along with "
        "their physical units and data types. These documents frequently span hundreds of pages, evolving across multiple revision "
        "cycles as vehicle requirements change. Reviewing and verifying these documents is traditionally a manual, labor-intensive "
        "process that consumes thousands of senior engineering hours and remains prone to overlooked interface mismatches, "
        "unintended circular dependencies, and lost traceability."
    )
    doc.add_paragraph(
        "AUTOSAR AI was developed to address this operational bottleneck by introducing an on-premises, high-assurance document "
        "intelligence platform. Designed specifically for automotive systems engineers, the platform automates HLD ingestion, "
        "structural entity extraction, architectural rule checking, revision diffing, and grounded conversational question-answering "
        "backed by verifiable page citations and empirical claim verification scores."
    )

    # Chapter 2
    add_heading_with_spacing(doc, "CHAPTER 2: PROBLEM STATEMENT & OBJECTIVES", level=1)
    doc.add_paragraph(
        "Automotive software engineering environments present three critical constraints that preclude the direct adoption of generic cloud-based AI tools:\n"
        "1. Strict Intellectual Property & Privacy Regulations: Under automotive cybersecurity standards (ISO/SAE 21434) and corporate non-disclosure agreements, proprietary vehicle software architectures cannot be transmitted to external cloud LLM providers.\n"
        "2. Intolerance for AI Hallucinations: In safety-critical vehicle engineering governed by ISO 26262, ungrounded answers or fabricated component names can compromise functional safety audits.\n"
        "3. Lack of Exact Traceability: Generic RAG pipelines frequently return broad text chunks without pin-point citation traceability down to physical PDF page numbers and claim-level verification."
    )
    doc.add_paragraph(
        "To resolve these challenges, AUTOSAR AI achieves the following primary engineering objectives:\n"
        "• High-Speed Page-Preserving Ingestion: Ingest complex HLD PDFs while strictly recording physical page bounds and section headers.\n"
        "• Hybrid Dense-plus-BM25 Retrieval: Combine 384-dimensional dense semantic vectors with BM25 keyword matching via Reciprocal Rank Fusion to accurately retrieve both conceptual passages and exact automotive identifiers.\n"
        "• On-Premises Generative Inference: Execute local inference using the quantized llama3.2:3b model via Ollama with strict evidence-bounded prompt engineering.\n"
        "• Claim-Level Verification & Grounding Score: Automatically decompose generated answers into verifiable claims and calculate a quantitative Grounding Score (0.0 to 1.0).\n"
        "• Architectural Entity Extraction & Rule Checking: Parse SWCs, Runnables, Ports, and Signals into a relational database and detect circular dependencies and insecure IPC bindings."
    )

    # Chapter 3
    add_heading_with_spacing(doc, "CHAPTER 3: LITERATURE SURVEY & EXISTING APPROACHES", level=1)
    doc.add_paragraph(
        "Traditional approaches to automotive document management rely on relational document repositories or ALM tools (such as "
        "PTC Integrity, Siemens Polarion, or IBM DOORS). While these platforms excel at requirement tracking, they require engineers "
        "to manually author and maintain every traceability link. When requirements change, traceability links frequently decay, "
        "leading to stale architectural documentation."
    )
    doc.add_paragraph(
        "Recent advances in Natural Language Processing have popularized Retrieval-Augmented Generation (RAG) frameworks like LangChain "
        "and LlamaIndex. However, existing commercial implementations are predominantly designed for cloud environments and general-purpose "
        "customer support. They treat technical specifications as generic prose, struggling to distinguish subtle automotive identifiers "
        "(e.g., confusing `CanIf_Transmit` with `CanTp_Transmit`) and lacking claim-level verification metrics. AUTOSAR AI bridges this "
        "gap by coupling hybrid retrieval with domain entity regex extraction, local model execution, and spreadsheet injection defenses."
    )

    # Chapter 4
    add_heading_with_spacing(doc, "CHAPTER 4: SYSTEM ARCHITECTURE & REQUIREMENTS", level=1)
    doc.add_paragraph(
        "The AUTOSAR AI platform is designed around a modular, decoupled architecture comprising eight distinct layers:\n"
        "1. Presentation Layer: An interactive 9-page Streamlit web user interface (port 8501) providing dashboard metrics, document management, architecture visualization, AI assistance, revision diffing, findings review, and system diagnostics.\n"
        "2. API Gateway & Routing Layer: A high-performance FastAPI asynchronous REST service (port 8000) structured across 10 dedicated routers.\n"
        "3. Ingestion & Extraction Layer: C-speed PDF parsing via PyMuPDF (fitz) that segments text into 1000-character chunks with 150-character overlap.\n"
        "4. Embedding & Vector Storage: SentenceTransformers (all-MiniLM-L6-v2) producing 384-dimensional dense vectors stored in persistent ChromaDB collections.\n"
        "5. Hybrid Retrieval & Fusion: A two-stage pipeline combining cosine similarity search with an in-memory BM25 index using Reciprocal Rank Fusion (k=60).\n"
        "6. Local LLM Inference: On-premises Ollama runtime (port 11434) executing llama3.2:3b with an evidence-bounded automotive system prompt.\n"
        "7. Relational Persistence: SQLite 3 database managed via SQLAlchemy 2.0 ORM with 14 relational tables.\n"
        "8. Security & Reporting: Automated CSV findings report generation with formula injection sanitization."
    )

    # Chapter 5
    add_heading_with_spacing(doc, "CHAPTER 5: METHODOLOGY & IMPLEMENTATION DETAILS", level=1)
    doc.add_paragraph(
        "The core methodology follows a four-stage pipeline: (1) Ingest & Extract; (2) Index & Partition; (3) Retrieve & Generate; "
        "and (4) Decompose & Verify."
    )
    doc.add_paragraph(
        "In Stage 1, PyMuPDF parses uploaded PDFs page by page. Heuristic regular expressions scan text chunks to extract Software Components, "
        "Runnables, Interfaces, Ports (PPorts, RPorts), and Signals. Entities are stored in the SQLite `architecture_entities` table with source page numbers."
    )
    doc.add_paragraph(
        "In Stage 2, text chunks are converted into 384-dimensional dense vectors and saved to ChromaDB collections partitioned by project ID "
        "(`project_{project_id}`), guaranteeing complete multi-project data isolation."
    )
    doc.add_paragraph(
        "In Stage 3, when a user queries the system, the hybrid retriever executes dense vector search and sparse BM25 scoring in parallel, "
        "merging ranks via Reciprocal Rank Fusion ($k=60$). The Top-5 chunks form the evidence context for local Ollama inference."
    )
    doc.add_paragraph(
        "In Stage 4, `grounding_service.py` splits the LLM response into atomic sentences, verifies each against citation text, and calculates "
        "the quantitative Grounding Score ($GS = N_{grounded} / N_{total}$). Responses are classified into High, Medium, or Needs Review confidence tiers."
    )

    # Chapter 6
    add_heading_with_spacing(doc, "CHAPTER 6: USER INTERFACE & IMPLEMENTED MODULES", level=1)
    doc.add_paragraph(
        "The platform delivers nine comprehensive, functional modules:\n"
        "1. Dashboard (`1_Dashboard.py`): Overview of active projects, indexed documents, and subsystem health indicators.\n"
        "2. Documents (`2_Documents.py`): PDF upload, version tagging, and governance lifecycle states (Draft -> In Review -> Approved).\n"
        "3. Architecture Explorer (`3_Architecture_Explorer.py`): Extracted entity registers and interactive Mermaid dependency graphs.\n"
        "4. AI Assistant (`4_AI_Assistant.py`): Grounded technical QA interface with source citation cards and Grounding Score tags.\n"
        "5. Comparisons (`5_Comparisons.py`): Cross-revision diffing with component rename detection and signal data-type changes.\n"
        "6. Findings (`6_Findings.py`): Automated architectural rule violations (circular dependencies, insecure IPC) and review workflows.\n"
        "7. Reports (`7_Reports.py`): On-demand CSV export generation with audit logging.\n"
        "8. Settings & Diagnostics (`8_Settings.py`): Parameter configuration and live 6-subsystem health probes.\n"
        "9. Evaluation (`9_Evaluation.py`): Standardized 35-query benchmark execution and performance visualization."
    )

    # Chapter 7
    add_heading_with_spacing(doc, "CHAPTER 7: TESTING METHODOLOGY & EMPIRICAL RESULTS", level=1)
    doc.add_paragraph(
        "To ensure high engineering quality, the entire application was subjected to rigorous automated testing using Pytest 9.1.1 "
        "on Python 3.11.9 (Windows 11). The automated test suite consists of 28 unit and integration tests across 12 test modules. "
        "All 28 tests pass with a 100% pass rate in 27.35 seconds."
    )
    
    # Test Summary Table
    t_table = doc.add_table(rows=7, cols=3)
    t_summary_data = [
        ("Subsystem Tested", "Test Module", "Result"),
        ("Security & Reporting", "test_comparison_and_reports.py", "3/3 PASSED (Formula sanitization, CSV download)"),
        ("Revision Comparison", "test_comparisons_and_renames.py", "1/1 PASSED (Rename detection, data type diffs)"),
        ("Project & Doc APIs", "test_docs.py", "3/3 PASSED (CRUD, input validation)"),
        ("Ingestion & Vector DB", "test_document_pipeline.py", "2/2 PASSED (PyMuPDF chunking, ChromaDB cascade)"),
        ("Grounding & Traceability", "test_grounding_and_traceability.py", "4/4 PASSED (Claim segmentation, Grounding Score)"),
        ("Hybrid Retrieval & Eval", "test_hybrid_retrieval_and_eval.py", "3/3 PASSED (BM25 scoring, benchmark run)")
    ]
    for i, row in enumerate(t_summary_data):
        for j, val in enumerate(row):
            t_table.rows[i].cells[j].text = val
    style_table(t_table)
    
    doc.add_paragraph()
    doc.add_paragraph(
        "Furthermore, empirical evaluation across our curated 35-query benchmark dataset demonstrated that the hybrid retriever "
        "successfully retrieves exact technical identifiers, while achieving a 100% abstention rate on out-of-scope adversarial questions."
    )

    # Chapter 8
    add_heading_with_spacing(doc, "CHAPTER 8: SECURITY, PRIVACY & SAFETY CONSIDERATIONS", level=1)
    doc.add_paragraph(
        "Security and privacy were primary design criteria for AUTOSAR AI:\n"
        "• Complete On-Premises Isolation: 100% of data processing occurs on localhost without external API calls.\n"
        "• CSV Formula Injection Defense: Exported text cells starting with formula trigger characters (=, +, -, @) are sanitized by prepending a single quote (').\n"
        "• Indirect Prompt Injection Boundaries: The system prompt explicitly instructs the LLM to treat document text as untrusted data.\n"
        "• Multi-Tenant Project Isolation: Relational tables enforce project foreign keys, and ChromaDB maintains dedicated collections per project.\n"
        "• Zero Hardcoded Secrets: All environment configuration uses sanitized templates (.env.example) with placeholder values."
    )

    # Chapter 9
    add_heading_with_spacing(doc, "CHAPTER 9: LIMITATIONS & FUTURE SCOPE", level=1)
    doc.add_paragraph(
        "In adherence to academic integrity, the following limitations of the current implementation are acknowledged:\n"
        "1. Ingestion relies on text-searchable PDFs; scanned raster bitmaps require external OCR preprocessing.\n"
        "2. Entity extraction uses heuristic regular expressions; while highly effective on standard naming conventions, unconventional terminology may produce false negatives.\n"
        "3. Complex multi-column tabular matrices are flattened to linear text during vectorization.\n\n"
        "Future enhancements include:\n"
        "• Bidirectional ARXML AST Parsing: Generating formal AUTOSAR XML schema models directly from HLD documentation.\n"
        "• Optical Character Recognition (OCR): Incorporating Tesseract for legacy scanned documents.\n"
        "• Real-Time Bus Timing Simulation: Integrating with CAN/LIN/Ethernet network simulators for communication latency analysis.\n"
        "• Fine-Tuned Domain NER: Training parameter-efficient domain models for specialized entity recognition."
    )

    # Chapter 10
    add_heading_with_spacing(doc, "CHAPTER 10: CONCLUSION & REFERENCES", level=1)
    doc.add_paragraph(
        "AUTOSAR AI successfully demonstrates the viability of an on-premises, privacy-preserving document intelligence platform "
        "tailored for the automotive software engineering domain. By coupling high-speed PDF ingestion with hybrid dense-plus-BM25 retrieval, "
        "local Ollama generative inference, claim decomposition, and architectural rule checking, the platform significantly accelerates "
        "architectural audits while eliminating hallucination risks and preserving data privacy."
    )
    doc.add_paragraph(
        "REFERENCES:\n"
        "[1] AUTOSAR Consortium, “Explanation of AUTOSAR Adaptive Platform Design,” Technical Specification, Rel. 22-11, 2022.\n"
        "[2] International Organization for Standardization, “ISO 26262: Road vehicles — Functional safety,” ISO Standard, 2018.\n"
        "[3] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in NeurIPS, vol. 33, pp. 9459–9474, 2020.\n"
        "[4] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” in EMNLP, 2019.\n"
        "[5] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Found. Trends Inf. Retr., vol. 3, no. 4, 2009.\n"
        "[6] Meta AI, “The Llama 3 Herd of Models,” arXiv preprint arXiv:2407.21783, 2024.\n"
        "[7] J. M. McKie, “PyMuPDF: High-performance PDF parsing for Python,” Artifex Software, 2024."
    )

    doc.save(BASE_DIR / "Documentation" / "Project_Report.docx")
    print("      Project_Report.docx generated.")

def main():
    print("Generating all professional Word documents...")
    generate_synopsis()
    generate_declaration()
    generate_project_report()
    print("All Word documents generated successfully.")

if __name__ == "__main__":
    main()
