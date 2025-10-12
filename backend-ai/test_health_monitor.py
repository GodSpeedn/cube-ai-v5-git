"""
Simple test script to verify health monitoring infrastructure.
"""
import asyncio
import sys
import os

# Add the backend-ai directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_monitoring.health_monitor import HealthMonitor
from health_monitoring.models import OverallStatus


async def test_health_monitor():
    """Test basic health monitor functionality."""
    print("Testing Health Monitor Infrastructure...")
    
    # Create health monitor instance
    monitor = HealthMonitor()
    print("✓ HealthMonitor instance created")
    
    # Test configuration
    services = monitor.config.get_all_services()
    print(f"✓ Configured services: {services}")
    
    startup_order = monitor.config.get_startup_order()
    print(f"✓ Startup order: {startup_order}")
    
    # Test health check (will show placeholder results)
    print("\nTesting health check...")
    health_status = await monitor.check_system_health()
    print(f"✓ Overall status: {health_status.overall_status.value}")
    print(f"✓ Services checked: {list(health_status.services.keys())}")
    print(f"✓ Issues found: {len(health_status.issues)}")
    
    # Test system status
    print("\nTesting system status...")
    system_status = await monitor.get_system_status()
    print(f"✓ System status retrieved")
    print(f"✓ Health status: {system_status.health.overall_status.value}")
    
    print("\n✅ Basic health monitoring infrastructure test completed!")
    print("Note: ServiceManager and DependencyValidator are placeholder implementations")


if __name__ == "__main__":
    asyncio.run(test_health_monitor())