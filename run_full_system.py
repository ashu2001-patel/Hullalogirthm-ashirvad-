#!/usr/bin/env python
"""Run both backend and frontend servers."""

import subprocess
import sys
import time
import os
import webbrowser

def run_backend():
    """Start FastAPI backend server."""
    print("\n" + "="*60)
    print("STARTING BACKEND SERVER (Port 8001)")
    print("="*60)

    backend_dir = os.path.join(os.path.dirname(__file__), "backend", "coverage-service")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8001",
        "--reload"
    ]

    proc = subprocess.Popen(cmd, cwd=backend_dir)
    return proc

def run_frontend():
    """Start frontend HTTP server."""
    print("\n" + "="*60)
    print("STARTING FRONTEND SERVER (Port 8000)")
    print("="*60)

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    cmd = [
        sys.executable, "-m", "http.server",
        "8000",
        "--directory", frontend_dir
    ]

    proc = subprocess.Popen(cmd)
    return proc

def main():
    """Start both servers."""
    print("\n" + "="*60)
    print("GEOSPATIAL DELIVERY COVERAGE SYSTEM")
    print("Starting Backend & Frontend...")
    print("="*60)

    # Start backend
    backend_proc = run_backend()
    time.sleep(3)  # Wait for backend to start

    # Start frontend
    frontend_proc = run_frontend()
    time.sleep(2)  # Wait for frontend to start

    # Open browser
    print("\n" + "="*60)
    print("SYSTEM RUNNING")
    print("="*60)
    print("\nFrontend: http://127.0.0.1:8000")
    print("Backend API: http://127.0.0.1:8001/docs")
    print("\nOpening browser...")
    print("="*60 + "\n")

    try:
        webbrowser.open('http://127.0.0.1:8000')
    except:
        print("Please open http://127.0.0.1:8000 in your browser")

    # Wait for processes
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Done!")
        sys.exit(0)

if __name__ == "__main__":
    main()
