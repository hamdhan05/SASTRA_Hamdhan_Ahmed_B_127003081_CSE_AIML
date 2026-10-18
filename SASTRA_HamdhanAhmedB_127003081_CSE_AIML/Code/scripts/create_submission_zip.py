import os
import zipfile
from pathlib import Path

BASE_DIR = Path(r"H:\tech_pulse_project")
SOURCE_FOLDER = BASE_DIR / "SASTRA_HamdhanAhmedB_127003081_CSE_AIML"
ZIP_OUTPUT = BASE_DIR / "SASTRA_HamdhanAhmedB_127003081_CSE_AIML.zip"

EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", ".idea", ".vscode"}
EXCLUDED_EXTS = {".pyc", ".pyo", ".pyd"}

def create_zip():
    print(f"Creating ZIP archive from {SOURCE_FOLDER}...")
    if ZIP_OUTPUT.exists():
        ZIP_OUTPUT.unlink()

    file_count = 0
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            dirs.sort()
            files.sort()
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDED_EXTS) or file in {".DS_Store", "Thumbs.db"}:
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(BASE_DIR).as_posix()
                zipf.write(file_path, arcname)
                file_count += 1

    zip_size_mb = ZIP_OUTPUT.stat().st_size / (1024 * 1024)
    print(f"Successfully created ZIP archive: {ZIP_OUTPUT}")
    print(f"Total files compressed: {file_count}")
    print(f"Final ZIP archive size: {zip_size_mb:.2f} MB")

if __name__ == "__main__":
    create_zip()
