"""
GitHub API Server for Online Manual Agents
Provides API endpoints for GitHub integration
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from online_agent_github_integration import online_agent_github

# Create FastAPI app
app = FastAPI(
    title="GitHub Integration API",
    description="API for GitHub integration with online manual agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class GitHubConfigRequest(BaseModel):
    token: str
    username: str
    email: Optional[str] = None

class UploadRequest(BaseModel):
    workflow_id: Optional[str] = None
    repo_name: Optional[str] = None
    commit_message: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    repository_url: Optional[str] = None
    commit_sha: Optional[str] = None
    files_pushed: Optional[int] = None
    error: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GitHub Integration API",
        "version": "1.0.0",
        "description": "API for GitHub integration with online manual agents",
        "endpoints": {
            "health": "/health",
            "configure": "/configure",
            "upload": "/upload",
            "repositories": "/repositories",
            "status": "/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "github_integration_api",
        "timestamp": datetime.now().isoformat(),
        "github_configured": online_agent_github.is_configured()
    }

@app.post("/configure")
async def configure_github(request: GitHubConfigRequest):
    """Configure GitHub integration"""
    try:
        result = online_agent_github.configure_github(
            token=request.token,
            username=request.username,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "GitHub configured successfully",
                "user": result["user"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")

@app.post("/upload")
async def upload_to_github(request: UploadRequest):
    """Upload generated code to GitHub"""
    try:
        if not online_agent_github.is_configured():
            raise HTTPException(
                status_code=400, 
                detail="GitHub not configured. Please configure GitHub first."
            )
        
        if request.workflow_id:
            # Upload specific workflow
            result = await online_agent_github.extract_and_upload_workflow_result(
                workflow_id=request.workflow_id,
                repo_name=request.repo_name,
                commit_message=request.commit_message
            )
        else:
            # Upload latest generated code
            result = await online_agent_github.upload_latest_generated_code(
                repo_name=request.repo_name
            )
        
        if result["success"]:
            return UploadResponse(
                success=True,
                message=result["message"],
                repository_url=result.get("repository_url"),
                commit_sha=result.get("commit_sha"),
                files_pushed=result.get("files_pushed")
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/repositories")
async def list_repositories():
    """List GitHub repositories"""
    try:
        if not online_agent_github.is_configured():
            raise HTTPException(
                status_code=400, 
                detail="GitHub not configured. Please configure GitHub first."
            )
        
        result = online_agent_github.list_repositories()
        
        if result["success"]:
            return {
                "success": True,
                "repositories": result["repositories"],
                "count": result["count"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")

@app.get("/status")
async def get_status():
    """Get GitHub integration status"""
    return {
        "github_configured": online_agent_github.is_configured(),
        "timestamp": datetime.now().isoformat(),
        "service": "github_integration_api"
    }

@app.get("/workflow/{workflow_id}/files")
async def get_workflow_files(workflow_id: str):
    """Get files generated by a specific workflow"""
    try:
        result = online_agent_github.get_workflow_files(workflow_id)
        
        if result["success"]:
            return {
                "success": True,
                "workflow_id": workflow_id,
                "files": result["files"],
                "stats": result["stats"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow files: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting GitHub Integration API Server...")
    print("📚 API Documentation: http://localhost:8002/docs")
    print("🔗 Endpoints:")
    print("   POST /configure - Configure GitHub")
    print("   POST /upload - Upload code to GitHub")
    print("   GET /repositories - List repositories")
    print("   GET /status - Get status")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
