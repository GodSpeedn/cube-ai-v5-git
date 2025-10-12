#!/usr/bin/env python3
"""
Start all AI Coding Assistant services
"""
import subprocess
import time
import sys
import os
from pathlib import Path

def start_service(name, command, cwd=None):
    """Start a service in a new process"""
    print(f"Starting {name}...")
    try:
        if cwd:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
        print(f"✅ {name} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🚀 Starting AI Coding Assistant Services...")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend-ai"
    frontend_dir = project_root / "offline-ai-frontend"
    
    processes = []
    
    try:
        # Start Main Service (Port 8000)
        print("\n1. Starting Main Service (Port 8000)...")
        main_process = start_service(
            "Main Service",
            "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            cwd=backend_dir
        )
        if main_process:
            processes.append(("Main Service", main_process))
        
        print("   Waiting 5 seconds for main service to initialize...")
        time.sleep(5)
        
        # Start Online Service (Port 8001)
        print("\n2. Starting Online Service (Port 8001)...")
        online_process = start_service(
            "Online Service", 
            "python online_agent_service.py",
            cwd=backend_dir
        )
        if online_process:
            processes.append(("Online Service", online_process))
        
        print("   Waiting 3 seconds for online service to initialize...")
        time.sleep(3)
        
        # Start Frontend (Port 5173)
        print("\n3. Starting Frontend (Port 5173)...")
        frontend_process = start_service(
            "Frontend",
            "npm run dev",
            cwd=frontend_dir
        )
        if frontend_process:
            processes.append(("Frontend", frontend_process))
        
        print("\n" + "=" * 50)
        print("🎉 All services are starting!")
        print("=" * 50)
        print("Main Service:    http://localhost:8000")
        print("Online Service:  http://localhost:8001")
        print("Frontend:        http://localhost:5173")
        print("\n💡 Models will be visible once both backend services are running!")
        print("   - Offline models: Available through Main Service")
        print("   - Online models:  Available through Online Service")
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping all services...")
            for name, process in processes:
                try:
                    process.terminate()
                    print(f"   Stopped {name}")
                except:
                    pass
            print("✅ All services stopped.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


