"""
Startup script that integrates health monitoring with the main application.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend-ai directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_monitoring.health_monitor import HealthMonitor
from health_monitoring.api import create_health_api
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main startup function with health monitoring."""
    logger.info("Starting application with health monitoring...")
    
    # Create health monitor
    health_monitor = HealthMonitor()
    
    # Validate dependencies first
    logger.info("Validating system dependencies...")
    validation_result = await health_monitor.validate_dependencies()
    
    if not validation_result.success:
        logger.warning(f"Dependency validation failed: {validation_result.message}")
        logger.warning("Some features may not work correctly.")
        if validation_result.installation_commands:
            logger.info("Suggested installation commands:")
            for cmd in validation_result.installation_commands:
                logger.info(f"  {cmd}")
    else:
        logger.info("All dependencies validated successfully!")
    
    # Start services
    logger.info("Starting system services...")
    startup_result = await health_monitor.start_services()
    
    if startup_result.success:
        logger.info(f"Services started successfully: {startup_result.started_services}")
    else:
        logger.error(f"Failed to start services: {startup_result.message}")
        logger.error(f"Failed services: {startup_result.failed_services}")
        return
    
    # Create and start the health monitoring API
    health_api = create_health_api()
    
    logger.info("Starting health monitoring API on port 8001...")
    logger.info("Health monitoring endpoints available at:")
    logger.info("  - http://localhost:8001/health")
    logger.info("  - http://localhost:8001/system-status")
    logger.info("  - http://localhost:8001/api-keys")
    logger.info("  - http://localhost:8001/models")
    
    # Start the health monitoring API server
    config = uvicorn.Config(
        app=health_api,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await health_monitor.stop_monitoring()
        await health_monitor.service_manager.stop_all_services()


if __name__ == "__main__":
    asyncio.run(main())
