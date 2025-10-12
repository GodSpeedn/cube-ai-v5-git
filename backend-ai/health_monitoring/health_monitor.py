"""
Main health monitor service that orchestrates system health management.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .models import (
    HealthStatus, SystemStatus, StartupResult, ValidationResult,
    ServiceHealth, Issue, DependencyStatus, OverallStatus, IssueSeverity, ServiceStatus
)
from .config import HealthMonitorConfig
logger = logging.getLogger(__name__)


class HealthMonitor:
    """Central orchestrator for system health management."""
    
    def __init__(self):
        self.config = HealthMonitorConfig()
        # Import here to avoid circular imports
        from .service_manager import ServiceManager
        from .dependency_validator import DependencyValidator
        from .api_key_manager import APIKeyManager
        from .model_discovery import ModelDiscoveryService
        
        self.service_manager = ServiceManager(self.config)
        self.dependency_validator = DependencyValidator()
        self.api_key_manager = APIKeyManager()
        self.model_discovery = ModelDiscoveryService(self.api_key_manager)
        self._last_health_check: Optional[datetime] = None
        self._cached_status: Optional[HealthStatus] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def check_system_health(self) -> HealthStatus:
        """Perform comprehensive health check of all system components."""
        logger.info("Starting comprehensive system health check")
        
        # Check service health
        service_health = await self._check_all_services()
        
        # Check dependencies
        validation_result = await self.dependency_validator.validate_all_dependencies()
        
        # Get API key status
        api_key_status = await self.api_key_manager.validate_all_keys()
        api_keys_configured = any(api_key_status.values())
        
        dependency_status = DependencyStatus(
            python_deps_ok=validation_result.success,
            node_deps_ok=validation_result.success,
            api_keys_configured=api_keys_configured,
            missing_python_deps=validation_result.missing_dependencies if not validation_result.success else [],
            missing_node_deps=validation_result.missing_dependencies if not validation_result.success else [],
            missing_api_keys=[provider.value for provider, is_valid in api_key_status.items() if not is_valid]
        )
        
        # Collect issues
        issues = self._collect_issues(service_health, dependency_status)
        
        # Determine overall status
        overall_status = self._determine_overall_status(service_health, dependency_status, issues)
        
        health_status = HealthStatus(
            overall_status=overall_status,
            services=service_health,
            dependencies=dependency_status,
            last_check=datetime.now(),
            issues=issues
        )
        
        self._cached_status = health_status
        self._last_health_check = datetime.now()
        
        logger.info(f"Health check completed. Overall status: {overall_status.value}")
        return health_status
    
    async def start_services(self) -> StartupResult:
        """Coordinate startup sequence for all services."""
        logger.info("Starting coordinated service startup")
        
        # Validate dependencies first
        validation_result = await self.dependency_validator.validate_all_dependencies()
        if not validation_result.success:
            return StartupResult(
                success=False,
                message=f"Dependency validation failed: {validation_result.message}",
                failed_services=self.config.get_all_services()
            )
        
        # Start services in dependency order
        startup_order = self.config.get_startup_order()
        started_services = []
        failed_services = []
        
        for service_name in startup_order:
            try:
                logger.info(f"Starting service: {service_name}")
                result = await self.service_manager.start_service(service_name)
                
                if result.success:
                    started_services.append(service_name)
                    logger.info(f"Successfully started {service_name}")
                else:
                    failed_services.append(service_name)
                    logger.error(f"Failed to start {service_name}: {result.message}")
                    # Stop previously started services on failure
                    await self._stop_started_services(started_services)
                    break
                    
            except Exception as e:
                logger.error(f"Exception starting {service_name}: {str(e)}")
                failed_services.append(service_name)
                await self._stop_started_services(started_services)
                break
        
        success = len(failed_services) == 0
        message = "All services started successfully" if success else f"Failed to start: {', '.join(failed_services)}"
        
        return StartupResult(
            success=success,
            message=message,
            started_services=started_services,
            failed_services=failed_services
        )
    
    async def validate_dependencies(self) -> ValidationResult:
        """Ensure all dependencies are available."""
        return await self.dependency_validator.validate_all_dependencies()
    
    async def discover_models(self) -> Dict[str, List[Dict]]:
        """Discover available models from all providers."""
        discovered_models = await self.model_discovery.discover_all_models()
        
        # Convert to serializable format
        result = {}
        for provider, models in discovered_models.items():
            result[provider.value] = [
                {
                    "id": model.id,
                    "name": model.name,
                    "capabilities": [cap.value for cap in model.capabilities],
                    "max_tokens": model.max_tokens,
                    "context_length": model.context_length,
                    "is_available": model.is_available,
                    "description": model.description
                }
                for model in models
            ]
        
        return result
    
    def get_api_key_status(self) -> Dict[str, any]:
        """Get current API key status."""
        return self.api_key_manager.get_validation_status()
    
    def set_api_key(self, provider: str, key: str) -> bool:
        """Set an API key for a provider."""
        from .api_key_manager import APIProvider
        try:
            provider_enum = APIProvider(provider.lower())
            return self.api_key_manager.set_key(provider_enum, key)
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            return False
    
    async def get_system_status(self) -> SystemStatus:
        """Return current system state with additional metrics."""
        # Get fresh health status if cache is stale
        if (self._cached_status is None or 
            self._last_health_check is None or 
            (datetime.now() - self._last_health_check).seconds > 60):
            health_status = await self.check_system_health()
        else:
            health_status = self._cached_status
        
        # Calculate uptime (simplified - time since first health check)
        uptime = None
        if self._last_health_check:
            uptime = (datetime.now() - self._last_health_check).total_seconds()
        
        # Get resource usage (placeholder for now)
        resource_usage = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0
        }
        
        return SystemStatus(
            health=health_status,
            uptime=uptime,
            resource_usage=resource_usage,
            active_connections=0
        )
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring already running")
            return
        
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started continuous health monitoring")
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while True:
            try:
                await self.check_system_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all configured services."""
        service_health = {}
        
        for service_name in self.config.get_all_services():
            try:
                health = await self.service_manager.check_service_health(service_name)
                service_health[service_name] = health
            except Exception as e:
                logger.error(f"Error checking health of {service_name}: {str(e)}")
                # Create error health status
                config = self.config.get_service_config(service_name)
                service_health[service_name] = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.ERROR,
                    port=config.port,
                    url=f"http://localhost:{config.port}",
                    error_message=str(e),
                    last_check=datetime.now()
                )
        
        return service_health
    
    def _collect_issues(self, service_health: Dict[str, ServiceHealth], 
                       dependency_status: DependencyStatus) -> List[Issue]:
        """Collect all system issues with suggested actions."""
        issues = []
        
        # Service issues
        for service_name, health in service_health.items():
            if health.status == ServiceStatus.ERROR:
                issues.append(Issue(
                    severity=IssueSeverity.CRITICAL,
                    component=f"service.{service_name}",
                    message=f"Service {service_name} is not running: {health.error_message or 'Unknown error'}",
                    suggested_action=f"Check service logs and restart {service_name}"
                ))
            elif health.status == ServiceStatus.STOPPED:
                issues.append(Issue(
                    severity=IssueSeverity.WARNING,
                    component=f"service.{service_name}",
                    message=f"Service {service_name} is stopped",
                    suggested_action=f"Start {service_name} service"
                ))
        
        # Dependency issues
        if dependency_status.missing_python_deps:
            issues.append(Issue(
                severity=IssueSeverity.CRITICAL,
                component="dependencies.python",
                message=f"Missing Python dependencies: {', '.join(dependency_status.missing_python_deps)}",
                suggested_action="Run: pip install -r requirements.txt"
            ))
        
        if dependency_status.missing_node_deps:
            issues.append(Issue(
                severity=IssueSeverity.CRITICAL,
                component="dependencies.node",
                message=f"Missing Node.js dependencies: {', '.join(dependency_status.missing_node_deps)}",
                suggested_action="Run: npm install"
            ))
        
        if dependency_status.missing_api_keys:
            issues.append(Issue(
                severity=IssueSeverity.WARNING,
                component="configuration.api_keys",
                message=f"Missing API keys: {', '.join(dependency_status.missing_api_keys)}",
                suggested_action="Configure API keys in environment variables or .env file"
            ))
        
        return issues
    
    def _determine_overall_status(self, service_health: Dict[str, ServiceHealth],
                                dependency_status: DependencyStatus,
                                issues: List[Issue]) -> OverallStatus:
        """Determine overall system health status."""
        # Check for critical issues
        critical_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
        if critical_issues:
            return OverallStatus.UNHEALTHY
        
        # Check service status
        running_services = sum(1 for h in service_health.values() if h.status == ServiceStatus.RUNNING)
        total_services = len(service_health)
        
        if running_services == 0:
            return OverallStatus.UNHEALTHY
        elif running_services < total_services:
            return OverallStatus.DEGRADED
        
        # Check for warnings
        warning_issues = [i for i in issues if i.severity == IssueSeverity.WARNING]
        if warning_issues:
            return OverallStatus.DEGRADED
        
        return OverallStatus.HEALTHY
    
    async def _stop_started_services(self, started_services: List[str]):
        """Stop services that were successfully started."""
        for service_name in reversed(started_services):
            try:
                await self.service_manager.stop_service(service_name)
                logger.info(f"Stopped {service_name} during cleanup")
            except Exception as e:
                logger.error(f"Error stopping {service_name} during cleanup: {str(e)}")


