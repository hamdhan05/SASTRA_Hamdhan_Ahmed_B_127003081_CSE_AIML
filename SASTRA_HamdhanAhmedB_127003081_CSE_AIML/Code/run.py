import os
import socket
import subprocess
import sys
import time
from pathlib import Path

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def find_python_interpreter() -> str:
    script_dir = Path(__file__).resolve().parent

    # 1. Check if the invoking Python interpreter has uvicorn and streamlit
    try:
        import uvicorn
        import streamlit
        return sys.executable
    except ImportError:
        pass

    # 2. Check for project virtual environments
    candidates = [
        script_dir / "venv" / "Scripts" / "python.exe",
        script_dir / "venv" / "bin" / "python",
        script_dir.parent / "autosar-ai" / "venv" / "Scripts" / "python.exe",
        script_dir.parent / "venv" / "Scripts" / "python.exe",
        Path(r"H:\tech_pulse_project\autosar-ai\venv\Scripts\python.exe"),
    ]
    for cand in candidates:
        if cand.is_file():
            return str(cand)

    return sys.executable

def start_services():
    script_dir = Path(__file__).resolve().parent
    py_exec = find_python_interpreter()

    print("=" * 60)
    print("AUTOSAR AI — Starting Services...")
    print("=" * 60)
    if py_exec != sys.executable:
        print(f"[INFO] Using virtual environment interpreter:")
        print(f"       {py_exec}")
    
    processes = []
    
    # Check Backend (port 8000)
    if is_port_in_use(8000):
        print("[INFO] Backend API is already running on http://127.0.0.1:8000")
    else:
        print("[START] Launching Backend API server on http://127.0.0.1:8000...")
        backend_cmd = [py_exec, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
        backend_proc = subprocess.Popen(backend_cmd, cwd=str(script_dir))
        processes.append(("Backend", backend_proc))
        
        # Wait for backend to be ready
        for _ in range(15):
            time.sleep(0.5)
            if is_port_in_use(8000):
                print("[READY] Backend is listening on port 8000.")
                break
    
    # Check Frontend (port 8501)
    if is_port_in_use(8501):
        print("[INFO] Frontend Streamlit UI is already running on http://localhost:8501")
    else:
        print("[START] Launching Frontend Streamlit UI on http://localhost:8501...")
        frontend_cmd = [py_exec, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"]
        frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(script_dir))
        processes.append(("Frontend", frontend_proc))
    
    if not processes:
        print("[READY] Both Backend and Frontend are already active and running!")
        return

    print("=" * 60)
    print("Application is active! Access the web interface at: http://localhost:8501")
    print("Press Ctrl+C to stop launched services.")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[WARN] {name} process exited with code {proc.returncode}.")
                    return
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down launched services...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("[DONE] Shutdown complete.")

if __name__ == "__main__":
    start_services()
