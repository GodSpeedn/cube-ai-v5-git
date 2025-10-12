#!/usr/bin/env python3
"""
Universal startup script for all services
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 Starting All Services - Backend, Online Agent, Frontend")
    print("=" * 60)
    print()

def check_requirements():
    """Check if Python and Node.js are available"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print(f"✅ Python: {python_version}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ Node.js not found")
        return False
    
    return True

def setup_python_environment():
    """Setup Python virtual environment and install dependencies"""
    print("\n📦 Setting up Python environment...")
    
    venv_path = Path("backend-ai/venv")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like (macOS, Linux)
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Install Python dependencies
    if Path("backend-ai/requirements.txt").exists():
        print("Installing Python dependencies...")
        try:
            subprocess.run([str(pip_exe), "install", "-r", "backend-ai/requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Python dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Some Python dependencies may not have installed correctly")
    
    return python_exe

def setup_node_environment():
    """Setup Node.js environment and install dependencies"""
    print("\n📦 Setting up Node.js environment...")
    
    node_modules_path = Path("offline-ai-frontend/node_modules")
    
    if not node_modules_path.exists():
        print("Installing Node.js dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd="offline-ai-frontend", 
                         check=True, capture_output=True)
            print("✅ Node.js dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Some Node.js dependencies may not have installed correctly")
    else:
        print("✅ Node.js dependencies already installed")

def check_github_config():
    """Check GitHub configuration"""
    print("\n🔍 Checking GitHub configuration...")
    
    keys_file = Path("backend-ai/keys.txt")
    if keys_file.exists():
        content = keys_file.read_text()
        if "GITHUB_TOKEN=" in content and "your_github_token_here" not in content:
            print("✅ GitHub configuration found")
        else:
            print("⚠️ Warning: GitHub token not configured in keys.txt")
            print("Code will be saved locally but not uploaded to GitHub")
    else:
        print("⚠️ Warning: keys.txt not found")
        print("GitHub auto-upload will not work")

def start_services(python_exe):
    """Start all services"""
    print("\n" + "=" * 60)
    print("🚀 Starting Services...")
    print("=" * 60)
    print()
    
    processes = []
    
    # Start Main Backend (Port 8000)
    print("📡 Starting Main Backend (Port 8000)...")
    try:
        if os.name == 'nt':  # Windows
            backend_process = subprocess.Popen(
                [str(python_exe), "main.py"],
                cwd="backend-ai",
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix-like
            backend_process = subprocess.Popen(
                [str(python_exe), "main.py"],
                cwd="backend-ai"
            )
        processes.append(("Main Backend", backend_process))
        print("✅ Main Backend started")
    except Exception as e:
        print(f"❌ Failed to start Main Backend: {e}")
    
    time.sleep(3)
    
    # Start Online Agent Service (Port 8001)
    print("🤖 Starting Online Agent Service (Port 8001)...")
    try:
        if os.name == 'nt':  # Windows
            online_process = subprocess.Popen(
                [str(python_exe), "online_agent_service.py"],
                cwd="backend-ai",
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix-like
            online_process = subprocess.Popen(
                [str(python_exe), "online_agent_service.py"],
                cwd="backend-ai"
            )
        processes.append(("Online Agent Service", online_process))
        print("✅ Online Agent Service started")
    except Exception as e:
        print(f"❌ Failed to start Online Agent Service: {e}")
    
    time.sleep(3)
    
    # Start Frontend (Port 3000)
    print("🌐 Starting Frontend (Port 3000)...")
    try:
        if os.name == 'nt':  # Windows
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="offline-ai-frontend",
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix-like
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="offline-ai-frontend"
            )
        processes.append(("Frontend", frontend_process))
        print("✅ Frontend started")
    except Exception as e:
        print(f"❌ Failed to start Frontend: {e}")
    
    return processes

def main():
    """Main function"""
    print_header()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if we're in the right directory
    if not Path("backend-ai").exists():
        print("❌ Error: backend-ai folder not found")
        print("Please run this script from the project root directory")
        input("Press Enter to exit...")
        return
    
    if not Path("offline-ai-frontend").exists():
        print("❌ Error: offline-ai-frontend folder not found")
        print("Please run this script from the project root directory")
        input("Press Enter to exit...")
        return
    
    # Check requirements
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    # Setup environments
    python_exe = setup_python_environment()
    setup_node_environment()
    check_github_config()
    
    # Start services
    processes = start_services(python_exe)
    
    # Show status
    print("\n" + "=" * 60)
    print("✅ All Services Started!")
    print("=" * 60)
    print()
    print("📡 Main Backend:     http://localhost:8000")
    print("🤖 Online Agents:    http://localhost:8001")
    print("🌐 Frontend:         http://localhost:3000")
    print()
    print("📋 Service Status:")
    for name, process in processes:
        status = "Running" if process.poll() is None else "Stopped"
        print(f"   - {name}: {status}")
    print()
    print("💡 Tips:")
    print("   - Each service runs in its own window/process")
    print("   - Check the windows for any error messages")
    print("   - Frontend may take a moment to compile")
    print("   - GitHub auto-upload requires valid credentials in keys.txt")
    print()
    print("🔧 To stop all services:")
    print("   - Close all the opened windows")
    print("   - Or press Ctrl+C in each window")
    print()
    
    # Open frontend in browser
    print("🌐 Opening frontend in browser...")
    time.sleep(5)
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Frontend opened in browser")
    except:
        print("⚠️ Could not open browser automatically")
        print("Please open http://localhost:3000 manually")
    
    print()
    print("🎉 Setup complete! Check the service windows for any issues.")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
