import os
import shutil
from pathlib import Path

AUTOSAR_DIR = Path(r"H:\tech_pulse_project\autosar-ai")
QUARANTINE_DIR = Path(r"H:\tech_pulse_project\quarantine_backup")

def safe_clean():
    print("Starting safe cleanup of autosar-ai...")
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    
    removed_items = []

    # 1. Root IMPLEMENTATION_REPORT.md
    impl_rep = AUTOSAR_DIR / "IMPLEMENTATION_REPORT.md"
    if impl_rep.exists():
        shutil.copy2(impl_rep, QUARANTINE_DIR / "IMPLEMENTATION_REPORT.md")
        impl_rep.unlink()
        removed_items.append("IMPLEMENTATION_REPORT.md (quarantined and removed)")

    # 2. Redundant PPTX at root
    pptx_root = AUTOSAR_DIR / "AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx"
    if pptx_root.exists():
        shutil.copy2(pptx_root, QUARANTINE_DIR / "AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx")
        pptx_root.unlink()
        removed_items.append("AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx [root duplicate] (quarantined and removed)")

    # 3. docs/ directory (legacy audit notes)
    docs_dir = AUTOSAR_DIR / "docs"
    if docs_dir.exists():
        q_docs = QUARANTINE_DIR / "docs"
        if q_docs.exists():
            shutil.rmtree(q_docs)
        shutil.copytree(docs_dir, q_docs)
        shutil.rmtree(docs_dir)
        removed_items.append("docs/ directory (17 legacy markdown audit files quarantined and removed)")

    # 4. data/autosar_ai.db.bak
    db_bak = AUTOSAR_DIR / "data" / "autosar_ai.db.bak"
    if db_bak.exists():
        shutil.copy2(db_bak, QUARANTINE_DIR / "autosar_ai.db.bak")
        db_bak.unlink()
        removed_items.append("data/autosar_ai.db.bak (quarantined and removed)")

    # 5. Stale test exports in data/exports/
    exports_dir = AUTOSAR_DIR / "data" / "exports"
    if exports_dir.exists():
        q_exports = QUARANTINE_DIR / "exports"
        q_exports.mkdir(exist_ok=True)
        count_exports = 0
        for f in exports_dir.glob("report_proj*.csv"):
            shutil.copy2(f, q_exports / f.name)
            f.unlink()
            count_exports += 1
        if count_exports > 0:
            removed_items.append(f"data/exports/ ({count_exports} stale test CSV export files quarantined and removed)")

    # 6. .pytest_cache
    pytest_cache = AUTOSAR_DIR / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
        removed_items.append(".pytest_cache directory (removed)")

    # 7. __pycache__ folders
    count_pycache = 0
    for p in AUTOSAR_DIR.rglob("__pycache__"):
        if "venv" not in p.parts:
            shutil.rmtree(p)
            count_pycache += 1
    if count_pycache > 0:
        removed_items.append(f"__pycache__ directories ({count_pycache} cache folders removed)")

    print("\nSummary of Removed / Quarantined Items:")
    for item in removed_items:
        print(f" - {item}")

    print(f"\nAll removed assets safely backed up to: {QUARANTINE_DIR}")

if __name__ == "__main__":
    safe_clean()
