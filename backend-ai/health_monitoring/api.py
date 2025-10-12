"""
FastAPI integration for health monitoring system.
"""
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .health_monitor import HealthMonitor
from .models import HealthStatus, SystemStatus, StartupResult, ValidationResult

logger = logging.getLogger(__name__)

# Pydantic models for API responses
class HealthResponse(BaseModel):
    overall_status: str
    services: Dict[str, Any]
    dependencies: Dict[str, Any]
    issues: List[Dict[str, Any]]
    last_check: str

class SystemStatusResponse(BaseModel):
    health: HealthResponse
    uptime: float
    resource_usage: Dict[str, float]
    active_connections: int

class StartupResponse(BaseModel):
    success: bool
    message: str
    started_services: List[str]
    failed_services: List[str]

class ValidationResponse(BaseModel):
    success: bool
    message: str
    missing_dependencies: List[str]
    installation_commands: List[str]

class APIKeyRequest(BaseModel):
    provider: str
    key: str

class APIKeyResponse(BaseModel):
    success: bool
    message: str
    providers: Dict[str, Any] | None = None

class ModelDiscoveryResponse(BaseModel):
    models: Dict[str, List[Dict[str, Any]]]

# Global health monitor instance
health_monitor = None

def create_health_api() -> FastAPI:
    """Create FastAPI app with health monitoring endpoints."""
    global health_monitor
    
    app = FastAPI(
        title="Health Monitoring API",
        description="API for monitoring system health and managing services",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize health monitor
    health_monitor = HealthMonitor()
    
    @app.on_event("startup")
    async def startup_event():
        """Start health monitoring on startup."""
        logger.info("Starting health monitoring system")
        await health_monitor.start_monitoring()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop health monitoring on shutdown."""
        logger.info("Stopping health monitoring system")
        await health_monitor.stop_monitoring()
        await health_monitor.service_manager.stop_all_services()
    
    @app.get("/health", response_model=HealthResponse)
    async def get_health():
        """Get current system health status."""
        try:
            health_status = await health_monitor.check_system_health()
            
            # Convert to response format
            services = {}
            for name, service in health_status.services.items():
                services[name] = {
                    "status": service.status.value,
                    "port": service.port,
                    "url": service.url,
                    "response_time": service.response_time,
                    "last_check": service.last_check.isoformat() if service.last_check else None,
                    "error_message": service.error_message,
                    "process_id": service.process_id,
                    "resource_usage": service.resource_usage,
                    "uptime": service.uptime
                }
            
            dependencies = {
                "python_deps_ok": health_status.dependencies.python_deps_ok,
                "node_deps_ok": health_status.dependencies.node_deps_ok,
                "api_keys_configured": health_status.dependencies.api_keys_configured,
                "missing_python_deps": health_status.dependencies.missing_python_deps,
                "missing_node_deps": health_status.dependencies.missing_node_deps,
                "missing_api_keys": health_status.dependencies.missing_api_keys
            }
            
            issues = [
                {
                    "severity": issue.severity.value,
                    "component": issue.component,
                    "message": issue.message,
                    "suggested_action": issue.suggested_action,
                    "timestamp": issue.timestamp.isoformat()
                }
                for issue in health_status.issues
            ]
            
            return HealthResponse(
                overall_status=health_status.overall_status.value,
                services=services,
                dependencies=dependencies,
                issues=issues,
                last_check=health_status.last_check.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/system-status", response_model=SystemStatusResponse)
    async def get_system_status():
        """Get detailed system status including resource usage."""
        try:
            system_status = await health_monitor.get_system_status()
            
            # Convert health status to response format
            health_response = HealthResponse(
                overall_status=system_status.health.overall_status.value,
                services={
                    name: {
                        "status": service.status.value,
                        "port": service.port,
                        "url": service.url,
                        "response_time": service.response_time,
                        "last_check": service.last_check.isoformat() if service.last_check else None,
                        "error_message": service.error_message,
                        "process_id": service.process_id,
                        "resource_usage": service.resource_usage,
                        "uptime": service.uptime
                    }
                    for name, service in system_status.health.services.items()
                },
                dependencies={
                    "python_deps_ok": system_status.health.dependencies.python_deps_ok,
                    "node_deps_ok": system_status.health.dependencies.node_deps_ok,
                    "api_keys_configured": system_status.health.dependencies.api_keys_configured,
                    "missing_python_deps": system_status.health.dependencies.missing_python_deps,
                    "missing_node_deps": system_status.health.dependencies.missing_node_deps,
                    "missing_api_keys": system_status.health.dependencies.missing_api_keys
                },
                issues=[
                    {
                        "severity": issue.severity.value,
                        "component": issue.component,
                        "message": issue.message,
                        "suggested_action": issue.suggested_action,
                        "timestamp": issue.timestamp.isoformat()
                    }
                    for issue in system_status.health.issues
                ],
                last_check=system_status.health.last_check.isoformat()
            )
            
            return SystemStatusResponse(
                health=health_response,
                uptime=system_status.uptime or 0,
                resource_usage=system_status.resource_usage or {},
                active_connections=system_status.active_connections
            )
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/start-services", response_model=StartupResponse)
    async def start_services():
        """Start all configured services."""
        try:
            result = await health_monitor.start_services()
            return StartupResponse(
                success=result.success,
                message=result.message,
                started_services=result.started_services,
                failed_services=result.failed_services
            )
        except Exception as e:
            logger.error(f"Error starting services: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/stop-services")
    async def stop_services():
        """Stop all running services."""
        try:
            await health_monitor.service_manager.stop_all_services()
            return {"message": "All services stopped"}
        except Exception as e:
            logger.error(f"Error stopping services: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/validate-dependencies", response_model=ValidationResponse)
    async def validate_dependencies():
        """Validate system dependencies."""
        try:
            result = await health_monitor.validate_dependencies()
            return ValidationResponse(
                success=result.success,
                message=result.message,
                missing_dependencies=result.missing_dependencies,
                installation_commands=result.installation_commands
            )
        except Exception as e:
            logger.error(f"Error validating dependencies: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api-keys")
    async def get_api_keys():
        """Get current API key status."""
        try:
            return health_monitor.get_api_key_status()
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api-keys", response_model=APIKeyResponse)
    async def set_api_key(request: APIKeyRequest):
        """Set an API key for a provider."""
        try:
            success = health_monitor.set_api_key(request.provider, request.key)
            if success:
                # Return current provider status including new providers
                return APIKeyResponse(
                    success=True,
                    message=f"API key set for {request.provider}",
                    providers=health_monitor.get_api_key_status()
                )
            else:
                return APIKeyResponse(
                    success=False,
                    message=f"Failed to set API key for {request.provider}"
                )
        except Exception as e:
            logger.error(f"Error setting API key: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/models", response_model=ModelDiscoveryResponse)
    async def discover_models():
        """Discover available models from all providers."""
        try:
            models = await health_monitor.discover_models()
            return ModelDiscoveryResponse(models=models)
        except Exception as e:
            logger.error(f"Error discovering models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/debug/validate-keys")
    async def debug_validate_keys():
        """Debug endpoint to test validation directly."""
        try:
            print("DEBUG: Calling validate_all_keys directly")
            results = await health_monitor.api_key_manager.validate_all_keys()
            print(f"DEBUG: Validation results: {results}")
            return {"validation_results": {k.value: v for k, v in results.items()}}
        except Exception as e:
            logger.error(f"Error in debug validation: {str(e)}")
            return {"error": str(e)}
    
    @app.get("/services")
    async def get_services():
        """Get list of all configured services."""
        try:
            services = health_monitor.config.get_all_services()
            running_services = health_monitor.service_manager.get_running_services()
            
            return {
                "configured_services": services,
                "running_services": running_services
            }
        except Exception as e:
            logger.error(f"Error getting services: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        """Root endpoint with basic info."""
        return {
            "message": "Health Monitoring API",
            "version": "1.0.0",
            "endpoints": [
                "/health",
                "/system-status",
                "/start-services",
                "/stop-services",
                "/validate-dependencies",
                "/api-keys",
                "/models",
                "/services"
            ]
        }
    
    return app
