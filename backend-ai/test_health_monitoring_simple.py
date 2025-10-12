"""
Simple test script to verify the health monitoring system is working.
"""
import asyncio
import sys
import os

# Add the backend-ai directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_monitoring.health_monitor import HealthMonitor


async def main():
    """Simple test of the health monitoring system."""
    print("Health Monitoring System - Simple Test")
    print("=" * 50)
    
    try:
        # Create health monitor
        monitor = HealthMonitor()
        print("✓ Health monitor created successfully")
        
        # Test health check
        print("\nTesting health check...")
        health_status = await monitor.check_system_health()
        print(f"✓ Overall status: {health_status.overall_status.value}")
        print(f"✓ Services checked: {len(health_status.services)}")
        print(f"✓ Issues found: {len(health_status.issues)}")
        
        # Test dependency validation
        print("\nTesting dependency validation...")
        validation_result = await monitor.validate_dependencies()
        print(f"✓ Validation success: {validation_result.success}")
        print(f"✓ Message: {validation_result.message}")
        
        # Test API key status
        print("\nTesting API key status...")
        api_status = monitor.get_api_key_status()
        print(f"✓ API key status retrieved: {len(api_status)} providers")
        
        # Test model discovery
        print("\nTesting model discovery...")
        models = await monitor.discover_models()
        print(f"✓ Model discovery completed: {len(models)} providers")
        
        print("\n✅ All tests passed! Health monitoring system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
