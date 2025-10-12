"""
Test script for service manager functionality.
"""
import asyncio
import sys
import os

# Add the backend-ai directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_monitoring.service_manager import ServiceManager
from health_monitoring.config import HealthMonitorConfig
from health_monitoring.models import ServiceStatus


async def test_service_manager():
    """Test service manager functionality."""
    print("Testing Service Manager...")
    
    # Create service manager
    config = HealthMonitorConfig()
    manager = ServiceManager(config)
    print("✓ ServiceManager instance created")
    
    # Test service health checking (without starting services)
    print("\nTesting service health checks...")
    for service_name in config.get_all_services():
        health = await manager.check_service_health(service_name)
        print(f"✓ {service_name}: {health.status.value} (port {health.port})")
        if health.error_message:
            print(f"  Error: {health.error_message}")
    
    # Test getting running services
    running = manager.get_running_services()
    print(f"\n✓ Currently running services: {running}")
    
    print("\n✅ Service Manager test completed!")
    print("Note: Services are not actually started in this test")


if __name__ == "__main__":
    asyncio.run(test_service_manager())