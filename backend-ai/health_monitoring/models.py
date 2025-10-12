"""
Data models for the health monitoring system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class OverallStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class IssueSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ServiceHealth:
    """Health information for a single service."""
    name: str
    status: ServiceStatus
    port: int
    url: str
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    process_id: Optional[int] = None
    resource_usage: Optional[Dict[str, float]] = None
    uptime: Optional[float] = None


@dataclass
class Issue:
    """Represents a system issue with suggested resolution."""
    severity: IssueSeverity
    component: str
    message: str
    suggested_action: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DependencyStatus:
    """Status of system dependencies."""
    python_deps_ok: bool = False
    node_deps_ok: bool = False
    api_keys_configured: bool = False
    missing_python_deps: List[str] = field(default_factory=list)
    missing_node_deps: List[str] = field(default_factory=list)
    missing_api_keys: List[str] = field(default_factory=list)


@dataclass
class HealthStatus:
    """Overall system health status."""
    overall_status: OverallStatus
    services: Dict[str, ServiceHealth] = field(default_factory=dict)
    dependencies: DependencyStatus = field(default_factory=DependencyStatus)
    last_check: datetime = field(default_factory=datetime.now)
    issues: List[Issue] = field(default_factory=list)


@dataclass
class StartupResult:
    """Result of service startup operation."""
    success: bool
    message: str
    failed_services: List[str] = field(default_factory=list)
    started_services: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of dependency validation."""
    success: bool
    message: str
    missing_dependencies: List[str] = field(default_factory=list)
    installation_commands: List[str] = field(default_factory=list)


@dataclass
class SystemStatus:
    """Complete system status information."""
    health: HealthStatus
    uptime: Optional[float] = None
    resource_usage: Optional[Dict[str, float]] = None
    active_connections: int = 0