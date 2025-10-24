# 🤖 AI Agent System - Offline & Online Code Generation

A powerful, full-stack AI agent system that combines **local LLM models** (via Ollama) and **online AI services** (OpenAI, Gemini, Mistral) for intelligent code generation, project management, and automatic GitHub integration.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### 🎯 Core Capabilities
- **🤖 Multi-Model AI Support**: Use local models (CodeLlama, Mistral, Llama2) or cloud APIs (OpenAI, Gemini, Mistral)
- **💻 Code Generation**: Generate complete, production-ready code from natural language prompts
- **📁 Smart File Management**: Automatic project organization with src/, tests/, and docs/ structure
- **🔄 GitHub Auto-Upload**: Automatically push generated code to GitHub repositories
- **💬 Conversation Memory**: Context-aware conversations with SQLite-backed history
- **🎨 Modern Web UI**: Beautiful React/TypeScript frontend with real-time updates
- **🔍 Health Monitoring**: Built-in service health checks and API key validation
- **🌐 Multi-Agent Workflows**: Coordinator, coder, tester, and reviewer agents working together

### ⚡ Advanced Features
- **Dynamic Model Discovery**: Automatically detects available Ollama models
- **API Key Management**: Centralized key storage with validation
- **Port Conflict Resolution**: Smart port management for multiple services
- **Service Orchestration**: Start/stop all services with a single command
- **Real-time Streaming**: WebSocket support for live code generation
- **Syntax Validation**: Automatic code validation before saving
- **Project Templates**: Pre-configured templates for common project types

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - [Download](https://python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Ollama** (optional, for local models) - [Download](https://ollama.ai/)

### 🎬 One-Command Startup

#### Windows
```bash
# Double-click or run:
start_all.bat
```

#### macOS/Linux
```bash
python start_all.py
```

#### PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File start_all.ps1
```

That's it! The system will:
- ✅ Check dependencies
- ✅ Install packages
- ✅ Start all services
- ✅ Open your browser to http://localhost:3000

---

## 📦 Manual Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/GodSpeedn/cube-ai-assign4.git
cd cube-ai-assign4
```

### Step 2: Backend Setup
```bash
cd backend-ai
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
cd offline-ai-frontend
npm install
```

### Step 4: Ollama Setup (Optional)
```bash
# Install Ollama
# Windows: winget install Ollama.Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Download models
ollama pull codellama:7b-instruct
ollama pull mistral
ollama pull llama2
```

### Step 5: Configure API Keys
Edit `backend-ai/keys.txt`:
```bash
# OpenAI (optional)
OPENAI_API_KEY=sk-your-key-here

# Mistral (optional)
MISTRAL_API_KEY=your-key-here

# Gemini (optional)
GEMINI_API_KEY=your-key-here

# GitHub (for auto-upload)
GITHUB_TOKEN=ghp_your-token-here
GITHUB_USERNAME=your-username
```

---

## 🎮 Usage

### Starting Services Individually

#### Backend API
```bash
cd backend-ai
python main.py
# Runs on http://localhost:8000
```

#### Online Agent Service
```bash
cd backend-ai
python online_agent_service.py
# Runs on http://localhost:8001
```

#### Frontend
```bash
cd offline-ai-frontend
npm run dev
# Runs on http://localhost:3000
```

### Service URLs
| Service | URL | Purpose |
|---------|-----|---------|
| 🌐 Frontend | http://localhost:3000 | Main web interface |
| 📡 Main Backend | http://localhost:8000 | Core API & file management |
| 🤖 Online Agents | http://localhost:8001 | AI agent workflows |
| 📚 API Docs | http://localhost:8000/docs | Interactive API documentation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)               │
│              TypeScript + Vite + TailwindCSS                │
└─────────────┬────────────────────────────┬──────────────────┘
              │                            │
              ▼                            ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│   Main Backend (8000)   │  │ Online Agents (8001)        │
│   FastAPI + SQLite      │  │ Multi-Agent Workflows       │
│   File Management       │  │ GitHub Integration          │
│   Conversation History  │  │ Code Validation             │
└────────┬────────────────┘  └─────────┬───────────────────┘
         │                             │
         ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Models & Services                           │
│  ┌────────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐   │
│  │   Ollama   │  │ OpenAI  │  │ Gemini │  │ Mistral  │   │
│  │ (Local AI) │  │  (API)  │  │ (API)  │  │  (API)   │   │
│  └────────────┘  └─────────┘  └────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Key Components

### Backend Services

#### 1️⃣ **Main Backend** (`main.py`)
- FastAPI server with CORS support
- Conversation management with SQLite
- File generation and organization
- Health monitoring endpoints
- Model discovery and validation

#### 2️⃣ **Online Agent Service** (`online_agent_service.py`)
- Multi-agent orchestration
- Coordinator, Coder, Tester, Reviewer agents
- Automatic GitHub repository creation
- Code validation and testing
- Project metadata management

#### 3️⃣ **File Manager** (`file_manager.py`)
- Smart project structure creation
- Automatic README generation
- GitHub integration
- File tracking and metadata

#### 4️⃣ **GitHub Service** (`git-integration/github_service.py`)
- Repository creation and management
- File upload via Git Tree API
- Token validation
- Branch management

### Frontend Application

#### Modern React + TypeScript UI
- 🎨 **TailwindCSS** for styling
- ⚡ **Vite** for fast builds
- 🔄 **React Router** for navigation
- 💾 **State Management** with Context API
- 🌐 **WebSocket** for real-time updates
- 🎭 **Modal Components** for file exploration

#### Key Features
- Chat interface for AI interactions
- Real-time code generation
- File explorer modal
- GitHub repository viewer
- Model selector
- Conversation history

---

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Port Configuration
Default ports:
- **Frontend**: 3000
- **Main Backend**: 8000
- **Online Agents**: 8001
- **Ollama**: 11434

To change ports, edit `start_all.py` or set environment variables.

---

## 📚 API Documentation

### Main Backend Endpoints

#### Chat & Conversation
```http
POST /chat
Content-Type: application/json

{
  "message": "Create a Python calculator",
  "model": "codellama:7b-instruct"
}
```

#### Generate Code
```http
POST /generate
Content-Type: application/json

{
  "prompt": "Create a REST API with FastAPI",
  "language": "python",
  "model": "gpt-4"
}
```

#### List Models
```http
GET /models
```

#### Health Check
```http
GET /health
```

### Online Agent Endpoints

#### Create Workflow
```http
POST /create-workflow
Content-Type: application/json

{
  "task": "Create a todo app",
  "language": "javascript",
  "github_upload": true
}
```

#### GitHub Upload
```http
POST /git/auto-upload
Content-Type: application/json

{
  "project_path": "/path/to/project",
  "repository_name": "my-project"
}
```

---

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend-ai
python test_health_monitoring_comprehensive.py
python test_github_integration.py
python test_full_workflow.py

# Frontend tests
cd offline-ai-frontend
npm test
```

### Health Monitoring
```bash
# Start with health monitoring
cd backend-ai
python start_with_health_monitoring.py
```

---

## 🐛 Troubleshooting

### Common Issues

#### ❌ "Port already in use"
```bash
# Stop all services
stop_all.bat

# Or kill specific ports
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### ❌ "Ollama not found"
```bash
# Install Ollama
winget install Ollama.Ollama

# Start Ollama service
ollama serve

# Download models
ollama pull codellama:7b-instruct
```

#### ❌ "GitHub upload failed"
1. Check `backend-ai/keys.txt` has valid token
2. Verify token scopes: `repo`, `workflow`, `write:packages`
3. Check token at https://github.com/settings/tokens

#### ❌ "Frontend won't load"
1. Wait 1-2 minutes for compilation
2. Check console for errors
3. Verify backend is running on port 8000
4. Clear browser cache and refresh

#### ❌ "Module not found" errors
```bash
# Reinstall dependencies
cd backend-ai
pip install -r requirements.txt

cd offline-ai-frontend
npm install
```

---

## 📖 Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Startup Guide](STARTUP_GUIDE.md) - How to start services
- [API Keys Setup](API_KEYS_SETUP.md) - Configure API credentials
- [Port Management](PORT_MANAGEMENT_GUIDE.md) - Handle port conflicts
- [GitHub Upload](GITHUB_UPLOAD_FIX.md) - GitHub integration details
- [Health Monitoring](HEALTH_MONITORING_README.md) - Service monitoring

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLite** - Conversation storage
- **LangChain** - LLM integration
- **Pydantic** - Data validation
- **Requests** - HTTP client

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **Lucide Icons** - Icon library

### AI Models
- **Ollama** - Local LLM server
- **CodeLlama** - Code generation
- **Mistral** - General purpose
- **Llama2** - General purpose
- **OpenAI GPT** - Cloud API
- **Google Gemini** - Cloud API
- **Mistral AI** - Cloud API

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Ollama** - For making local LLMs accessible
- **FastAPI** - For the amazing web framework
- **React Team** - For the powerful UI library
- **LangChain** - For LLM integration tools
- **All Contributors** - For making this project better

---

## 📞 Support

Having issues? Here's how to get help:

1. **Check Documentation** - Read the guides in the docs/ folder
2. **Common Issues** - See the Troubleshooting section above
3. **GitHub Issues** - Open an issue with detailed information
4. **Logs** - Check service logs for error messages

---

## 🎯 Roadmap

### Upcoming Features
- [ ] Docker containerization
- [ ] Database migration system
- [ ] User authentication
- [ ] Project templates library
- [ ] Code collaboration features
- [ ] CI/CD pipeline integration
- [ ] Multi-language support
- [ ] Plugin system
- [ ] Cloud deployment guides
- [ ] Mobile responsive UI

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ by the AI Agent System Team**

[⬆ Back to Top](#-ai-agent-system---offline--online-code-generation)

</div>
