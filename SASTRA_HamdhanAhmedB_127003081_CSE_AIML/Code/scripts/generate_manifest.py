import os
from pathlib import Path

ROOT_DIR = Path(r"H:\tech_pulse_project\SASTRA_HamdhanAhmedB_127003081_CSx_AIML")
MANIFEST_PATH = ROOT_DIR / "requirements_and_file_manifest.txt"

def generate_manifest():
    lines = []
    lines.append("=" * 80)
    lines.append("AUTOSAR AI — UNIVERSITY SUBMISSION FILE MANIFEST & REQUIREMENTS")
    lines.append("=" * 80)
    lines.append("Student Name    : Hamdhan Ahmed B")
    lines.append("Register Number : 127003081")
    lines.append("Degree & Branch : B.Tech. Computer Science & Engineering (AIML)")
    lines.append("University      : SASTRA Deemed University")
    lines.append("Project Title   : AUTOSAR AI – High-Level Design Document Intelligence Platform")
    lines.append("Repository      : https://github.com/hamdhan05/AUTOSAR-AI-Implementation")
    lines.append("Submission Date : October 13, 2026")
    lines.append("=" * 80)
    lines.append("")
    lines.append("1. SYSTEM & RUNTIME PREREQUISITES")
    lines.append("-" * 80)
    lines.append("Operating System : Windows 10 / Windows 11 (64-bit)")
    lines.append("Python Runtime   : Python 3.11.x (tested on Python 3.11.9)")
    lines.append("Local LLM Server : Ollama 0.40+ (http://localhost:11434)")
    lines.append("Active Model     : llama3.2:3b (quantized Q4_K_M GGUF, 3.21B parameters)")
    lines.append("Embedding Model  : sentence-transformers/all-MiniLM-L6-v2 (384-dimensional dense vectors)")
    lines.append("Vector Store     : ChromaDB 0.4.24 (Local persistent disk storage)")
    lines.append("Database Engine  : SQLite 3 with SQLAlchemy 2.0 ORM (14 relational models)")
    lines.append("Web Frontend     : Streamlit 1.32.0 (9 interactive pages)")
    lines.append("API Backend      : FastAPI 0.110.0 / Uvicorn (10 REST routers on port 8000)")
    lines.append("Automated Tests  : Pytest 9.1.1 (28 automated tests across 12 modules, 100% pass rate)")
    lines.append("")
    lines.append("=" * 80)
    lines.append("2. COMPLETE SUBMISSION FILE INVENTORY & SIZES")
    lines.append("-" * 80)
    lines.append(f"{'Relative Path':<65} | {'Size (Bytes)':>12}")
    lines.append("-" * 80)

    total_files = 0
    total_bytes = 0

    for root, dirs, files in os.walk(ROOT_DIR):
        # Sort for deterministic output
        dirs.sort()
        files.sort()
        for f in files:
            if f == "requirements_and_file_manifest.txt":
                continue
            full_path = Path(root) / f
            rel_path = full_path.relative_to(ROOT_DIR).as_posix()
            size = full_path.stat().st_size
            lines.append(f"{rel_path:<65} | {size:>12,}")
            total_files += 1
            total_bytes += size

    lines.append("-" * 80)
    lines.append(f"Total Files Cataloged: {total_files}")
    lines.append(f"Total Package Size   : {total_bytes:,} bytes ({total_bytes / (1024*1024):.2f} MB)")
    lines.append("=" * 80)
    lines.append("")
    lines.append("3. INTENTIONALLY EXCLUDED LOCAL-ONLY RESOURCES")
    lines.append("-" * 80)
    lines.append("1. Python Virtual Environment (venv/): Excluded (~1.8 GB). Recreated via requirements.txt.")
    lines.append("2. Ollama Model Weights (H:\\OllamaModels): Excluded (~2.0 GB). Obtained via `ollama pull llama3.2:3b`.")
    lines.append("3. Local Vector Store Binaries (data/vector_store/): Excluded. Auto-generated on PDF ingestion.")
    lines.append("4. Local Active SQLite DB (data/autosar_ai.db): Excluded. Clean tables initialized on backend startup.")
    lines.append("5. Python Bytecode (__pycache__, *.pyc): Cleaned from submission package.")
    lines.append("=" * 80)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"File manifest created at {MANIFEST_PATH}")
    print(f"Total files: {total_files}, Total size: {total_bytes / (1024*1024):.2f} MB")

if __name__ == "__main__":
    generate_manifest()
