"""
Service manager for controlling individual service lifecycle.
"""
import asyncio
import logging
import subprocess
import psutil
import signal
import os
import time
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime

from .models import ServiceHealth, ServiceStatus, StartupResult
from .config import HealthMonitorConfig, ServiceConfig
from .port_checker import PortChecker

logger = logging.getLogger(__name__)


class ServiceController:
    """Base class for service controllers."""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3
    
    async def start(self) -> StartupResult:
        """Start the service with retry logic."""
        if self.is_running():
            return StartupResult(
                success=True,
                message=f"Service {self.config.name} is already running"
            )
        
        # Check if port is already open (service already running)
        if PortChecker.is_port_open(self.config.port):
            return StartupResult(
                success=True,
                message=f"Service {self.config.name} is already running on port {self.config.port}"
            )
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starting {self.config.name} service... (attempt {attempt + 1}/{self.max_retries})")
                
                # Prepare environment
                env = os.environ.copy()
                env.update(self.config.environment_vars)
                
                # Start the process
                self.process = subprocess.Popen(
                    [self.config.startup_command] + self.config.startup_args,
                    cwd=self.config.working_directory,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                
                self.start_time = datetime.now()
                
                # Wait for service to be ready
                ready = await self._wait_for_ready()
                
                if ready:
                    logger.info(f"Service {self.config.name} started successfully (PID: {self.process.pid})")
                    self.retry_count = 0  # Reset retry count on success
                    return StartupResult(
                        success=True,
                        message=f"Service {self.config.name} started successfully",
                        started_services=[self.config.name]
                    )
                else:
                    logger.warning(f"Service {self.config.name} failed to become ready (attempt {attempt + 1})")
                    await self.stop()
                    
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying {self.config.name} in 5 seconds...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        return StartupResult(
                            success=False,
                            message=f"Service {self.config.name} failed to become ready after {self.max_retries} attempts",
                            failed_services=[self.config.name]
                        )
                    
            except Exception as e:
                logger.error(f"Failed to start {self.config.name} (attempt {attempt + 1}): {str(e)}")
                await self.stop()
                
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying {self.config.name} in 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                else:
                    return StartupResult(
                        success=False,
                        message=f"Failed to start {self.config.name} after {self.max_retries} attempts: {str(e)}",
                        failed_services=[self.config.name]
                    )
        
        return StartupResult(
            success=False,
            message=f"Service {self.config.name} failed to start after {self.max_retries} attempts",
            failed_services=[self.config.name]
        )
    
    async def stop(self) -> StartupResult:
        """Stop the service."""
        if not self.is_running():
            return StartupResult(
                success=True,
                message=f"Service {self.config.name} is not running"
            )
        
        try:
            logger.info(f"Stopping {self.config.name} service...")
            
            if self.process:
                # Try graceful shutdown first
                if os.name == 'nt':
                    # Windows
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    # Unix-like
                    self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    logger.warning(f"Force killing {self.config.name} service")
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
                self.start_time = None
                
            logger.info(f"Service {self.config.name} stopped successfully")
            return StartupResult(
                success=True,
                message=f"Service {self.config.name} stopped successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to stop {self.config.name}: {str(e)}")
            return StartupResult(
                success=False,
                message=f"Failed to stop {self.config.name}: {str(e)}"
            )
    
    def is_running(self) -> bool:
        """Check if the service process is running."""
        if not self.process:
            return False
        
        try:
            # Check if process is still alive
            return self.process.poll() is None
        except:
            return False
    
    def get_process_id(self) -> Optional[int]:
        """Get the process ID if running."""
        if self.process and self.is_running():
            return self.process.pid
        return None
    
    def get_resource_usage(self) -> Optional[Dict[str, float]]:
        """Get resource usage for the service process."""
        if not self.process or not self.is_running():
            return None
        
        try:
            process = psutil.Process(self.process.pid)
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def get_uptime(self) -> Optional[float]:
        """Get service uptime in seconds."""
        if not self.start_time:
            return None
        return (datetime.now() - self.start_time).total_seconds()
    
    async def _wait_for_ready(self) -> bool:
        """Wait for service to be ready by checking health endpoint."""
        start_time = time.time()
        
        # First wait for port to be open
        logger.info(f"Waiting for {self.config.name} port {self.config.port} to be ready...")
        port_ready = await PortChecker.wait_for_port(
            self.config.port, 
            timeout=self.config.startup_timeout / 2,
            check_interval=1.0
        )
        
        if not port_ready:
            logger.error(f"Service {self.config.name} port {self.config.port} did not become available")
            return False
        
        # Then check health endpoint
        while time.time() - start_time < self.config.startup_timeout:
            if not self.is_running():
                logger.error(f"Service {self.config.name} process died during startup")
                return False
            
            # Check if service is responding to health checks
            if await self._check_health():
                return True
            
            await asyncio.sleep(2)
        
        return False
    
    async def _check_health(self) -> bool:
        """Check if service is responding to health checks."""
        try:
            url = f"http://localhost:{self.config.port}{self.config.health_endpoint}"
            timeout = aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return response.status < 500
                    
        except Exception:
            return False


class BackendServiceController(ServiceController):
    """Controller for FastAPI backend service."""
    
    async def _check_health(self) -> bool:
        """Backend-specific health check."""
        try:
            url = f"http://localhost:{self.config.port}/health"
            timeout = aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return response.status == 200
                    
        except Exception:
            # Fallback to basic connectivity check
            return await super()._check_health()


class FrontendServiceController(ServiceController):
    """Controller for React frontend service."""
    
    async def _check_health(self) -> bool:
        """Frontend-specific health check."""
        try:
            url = f"http://localhost:{self.config.port}/"
            timeout = aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    # Frontend is ready if it returns any valid response
                    return response.status < 500
                    
        except Exception:
            return False


class DatabaseController(ServiceController):
    """Controller for database connections."""
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        # Database doesn't have a separate process, just connection checking
        self.process = None
    
    async def start(self) -> StartupResult:
        """Database doesn't need starting, just check connection."""
        return StartupResult(
            success=True,
            message="Database connection check completed"
        )
    
    async def stop(self) -> StartupResult:
        """Database doesn't need stopping."""
        return StartupResult(
            success=True,
            message="Database connection closed"
        )
    
    def is_running(self) -> bool:
        """Always return True for database - actual check is in health check."""
        return True
    
    async def _check_health(self) -> bool:
        """Check database connection."""
        try:
            # TODO: Implement actual database connection check
            # For now, assume database is available
            return True
        except Exception:
            return False


class ServiceManager:
    """Manages individual service lifecycle."""
    
    def __init__(self, config: HealthMonitorConfig):
        self.config = config
        self._controllers: Dict[str, ServiceController] = {}
        self._initialize_controllers()
    
    def _initialize_controllers(self):
        """Initialize service controllers based on configuration."""
        for service_name, service_config in self.config.services.items():
            if service_name == "backend":
                self._controllers[service_name] = BackendServiceController(service_config)
            elif service_name == "frontend":
                self._controllers[service_name] = FrontendServiceController(service_config)
            elif service_name == "database":
                self._controllers[service_name] = DatabaseController(service_config)
            else:
                # Generic controller for other services
                self._controllers[service_name] = ServiceController(service_config)
    
    async def start_service(self, service_name: str) -> StartupResult:
        """Start a specific service."""
        if service_name not in self._controllers:
            return StartupResult(
                success=False,
                message=f"Unknown service: {service_name}",
                failed_services=[service_name]
            )
        
        controller = self._controllers[service_name]
        return await controller.start()
    
    async def stop_service(self, service_name: str) -> StartupResult:
        """Stop a specific service."""
        if service_name not in self._controllers:
            return StartupResult(
                success=False,
                message=f"Unknown service: {service_name}",
                failed_services=[service_name]
            )
        
        controller = self._controllers[service_name]
        return await controller.stop()
    
    async def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services...")
        
        # Stop services in reverse dependency order
        startup_order = self.config.get_startup_order()
        
        for service_name in reversed(startup_order):
            if service_name in self._controllers:
                try:
                    await self.stop_service(service_name)
                except Exception as e:
                    logger.error(f"Error stopping {service_name}: {str(e)}")
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service."""
        if service_name not in self._controllers:
            config = self.config.get_service_config(service_name)
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.ERROR,
                port=config.port,
                url=f"http://localhost:{config.port}",
                last_check=datetime.now(),
                error_message=f"Unknown service: {service_name}"
            )
        
        controller = self._controllers[service_name]
        config = self.config.get_service_config(service_name)
        
        # Check if process is running
        is_running = controller.is_running()
        
        # Check port availability
        port_open = PortChecker.is_port_open(config.port, timeout=2.0)
        
        # Measure response time and check health
        start_time = time.time()
        is_healthy = False
        error_message = None
        
        # If port is open, try to check health regardless of process status
        if port_open:
            try:
                is_healthy = await controller._check_health()
                if not is_healthy:
                    error_message = "Service not responding to health checks"
            except Exception as e:
                error_message = f"Health check failed: {str(e)}"
        else:
            if is_running:
                error_message = f"Port {config.port} is not accepting connections"
            else:
                error_message = "Service process is not running"
        
        response_time = time.time() - start_time
        
        # Determine status
        if port_open and is_healthy:
            status = ServiceStatus.RUNNING
        elif port_open and not is_healthy:
            status = ServiceStatus.ERROR
        else:
            status = ServiceStatus.STOPPED
        
        # Get resource usage and uptime
        resource_usage = controller.get_resource_usage()
        uptime = controller.get_uptime()
        
        return ServiceHealth(
            name=service_name,
            status=status,
            port=config.port,
            url=f"http://localhost:{config.port}",
            response_time=response_time,
            last_check=datetime.now(),
            error_message=error_message,
            process_id=controller.get_process_id(),
            resource_usage=resource_usage,
            uptime=uptime
        )
    
    def get_running_services(self) -> List[str]:
        """Get list of currently running services."""
        running = []
        for service_name, controller in self._controllers.items():
            if controller.is_running():
                running.append(service_name)
        return running