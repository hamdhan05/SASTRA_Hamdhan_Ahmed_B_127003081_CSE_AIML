import sys
from pathlib import Path

# Add project root (Code directory) to sys.path so tests can import backend and frontend
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
