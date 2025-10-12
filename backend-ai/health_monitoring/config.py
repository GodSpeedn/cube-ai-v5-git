"""
Configuration management for health monitoring system.
"""
from dataclasses import dataclass
from typing import Dict, List
import os


@dataclass
class ServiceConfig:
    """Configuration for a single service."""
    name: str
    port: int
    health_endpoint: str
    startup_command: str
    startup_args: List[str]
    working_directory: str
    environment_vars: Dict[str, str]
    dependencies: List[str]  # Other services this depends on
    startup_timeout: int = 30  # seconds
    health_check_timeout: int = 5  # seconds


class HealthMonitorConfig:
    """Central configuration for the health monitoring system."""
    
    def __init__(self):
        self.services = self._get_default_services()
        self.health_check_interval = 30  # seconds
        self.startup_retry_attempts = 3
        self.startup_retry_delay = 5  # seconds
        
    def _get_default_services(self) -> Dict[str, ServiceConfig]:
        """Define default service configurations."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return {
            "backend": ServiceConfig(
                name="backend",
                port=8000,
                health_endpoint="/health",
                startup_command="uvicorn",
                startup_args=["main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                working_directory=base_dir,
                environment_vars={},
                dependencies=[],
                startup_timeout=45,
                health_check_timeout=10
            ),
            "frontend": ServiceConfig(
                name="frontend",
                port=5173,
                health_endpoint="/",
                startup_command="npm",
                startup_args=["run", "dev"],
                working_directory=os.path.join(os.path.dirname(base_dir), "offline-ai-frontend"),
                environment_vars={"PORT": "5173"},
                dependencies=["backend"],
                startup_timeout=60,
                health_check_timeout=10
            )
        }
    
    def get_service_config(self, service_name: str) -> ServiceConfig:
        """Get configuration for a specific service."""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        return self.services[service_name]
    
    def get_all_services(self) -> List[str]:
        """Get list of all configured service names."""
        return list(self.services.keys())
    
    def get_startup_order(self) -> List[str]:
        """Get services in dependency order for startup."""
        # Simple topological sort based on dependencies
        ordered = []
        remaining = set(self.services.keys())
        
        while remaining:
            # Find services with no unmet dependencies
            ready = []
            for service in remaining:
                deps = set(self.services[service].dependencies)
                if deps.issubset(set(ordered)):
                    ready.append(service)
            
            if not ready:
                # Circular dependency or missing dependency
                # Add remaining services in arbitrary order
                ready = list(remaining)
            
            # Sort ready services alphabetically for consistency
            ready.sort()
            ordered.extend(ready)
            remaining -= set(ready)
        
        return ordered