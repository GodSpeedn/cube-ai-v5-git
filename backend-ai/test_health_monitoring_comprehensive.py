"""
Comprehensive test script for the health monitoring system.
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend-ai directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_monitoring.health_monitor import HealthMonitor
from health_monitoring.api_key_manager import APIKeyManager, APIProvider
from health_monitoring.model_discovery import ModelDiscoveryService, ModelCapability
from health_monitoring.dependency_validator import DependencyValidator
from health_monitoring.service_manager import ServiceManager
from health_monitoring.config import HealthMonitorConfig


async def test_health_monitor():
    """Test the main health monitor functionality."""
    print("=" * 60)
    print("TESTING HEALTH MONITOR")
    print("=" * 60)
    
    monitor = HealthMonitor()
    
    # Test health check
    print("\n1. Testing system health check...")
    health_status = await monitor.check_system_health()
    print(f"   ✓ Overall status: {health_status.overall_status.value}")
    print(f"   ✓ Services checked: {len(health_status.services)}")
    print(f"   ✓ Issues found: {len(health_status.issues)}")
    
    # Test system status
    print("\n2. Testing system status...")
    system_status = await monitor.get_system_status()
    print(f"   ✓ System status retrieved")
    print(f"   ✓ Uptime: {system_status.uptime}")
    print(f"   ✓ Resource usage: {system_status.resource_usage}")
    
    # Test dependency validation
    print("\n3. Testing dependency validation...")
    validation_result = await monitor.validate_dependencies()
    print(f"   ✓ Validation success: {validation_result.success}")
    print(f"   ✓ Message: {validation_result.message}")
    if validation_result.missing_dependencies:
        print(f"   ✓ Missing dependencies: {validation_result.missing_dependencies}")
    
    print("\n✅ Health Monitor tests completed!")


async def test_api_key_manager():
    """Test API key management functionality."""
    print("\n" + "=" * 60)
    print("TESTING API KEY MANAGER")
    print("=" * 60)
    
    manager = APIKeyManager()
    
    # Test setting a key
    print("\n1. Testing API key management...")
    test_key = "test-key-12345"
    success = manager.set_key(APIProvider.OPENAI, test_key)
    print(f"   ✓ Set OpenAI key: {success}")
    
    # Test getting key info
    key_info = manager.get_key_info(APIProvider.OPENAI)
    if key_info:
        print(f"   ✓ Key info retrieved: {key_info.masked_key}")
        print(f"   ✓ Provider: {key_info.provider.value}")
    
    # Test validation status
    print("\n2. Testing validation status...")
    status = manager.get_validation_status()
    print(f"   ✓ Validation status: {json.dumps(status, indent=2)}")
    
    # Test key validation (this will fail with test key, but that's expected)
    print("\n3. Testing key validation...")
    is_valid = await manager.validate_key(APIProvider.OPENAI)
    print(f"   ✓ Key validation result: {is_valid}")
    
    print("\n✅ API Key Manager tests completed!")


async def test_model_discovery():
    """Test model discovery functionality."""
    print("\n" + "=" * 60)
    print("TESTING MODEL DISCOVERY")
    print("=" * 60)
    
    api_manager = APIKeyManager()
    discovery = ModelDiscoveryService(api_manager)
    
    # Test model discovery
    print("\n1. Testing model discovery...")
    models = await discovery.discover_all_models()
    print(f"   ✓ Discovered models from {len(models)} providers")
    
    for provider, model_list in models.items():
        print(f"   ✓ {provider}: {len(model_list)} models")
        if model_list:
            first_model = model_list[0]
            print(f"     - Example: {first_model.name} ({first_model.id})")
            print(f"     - Capabilities: {[cap.value for cap in first_model.capabilities]}")
    
    # Test model search
    print("\n2. Testing model search...")
    search_results = discovery.search_models("claude")
    print(f"   ✓ Found {len(search_results)} models matching 'claude'")
    
    # Test capability filtering
    print("\n3. Testing capability filtering...")
    chat_models = discovery.get_models_by_capability(ModelCapability.CHAT)
    print(f"   ✓ Found {len(chat_models)} models with chat capability")
    
    print("\n✅ Model Discovery tests completed!")


async def test_dependency_validator():
    """Test dependency validation functionality."""
    print("\n" + "=" * 60)
    print("TESTING DEPENDENCY VALIDATOR")
    print("=" * 60)
    
    validator = DependencyValidator()
    
    # Test Python dependencies
    print("\n1. Testing Python dependency validation...")
    python_status = await validator.check_python_deps()
    print(f"   ✓ Python deps OK: {python_status.python_deps_ok}")
    if python_status.missing_python_deps:
        print(f"   ✓ Missing Python deps: {python_status.missing_python_deps}")
    
    # Test Node.js dependencies
    print("\n2. Testing Node.js dependency validation...")
    node_status = await validator.check_node_deps()
    print(f"   ✓ Node deps OK: {node_status.node_deps_ok}")
    if node_status.missing_node_deps:
        print(f"   ✓ Missing Node deps: {node_status.missing_node_deps}")
    
    # Test API key validation
    print("\n3. Testing API key validation...")
    api_status = await validator.check_api_keys()
    print(f"   ✓ API keys configured: {api_status.api_keys_configured}")
    if api_status.missing_api_keys:
        print(f"   ✓ Missing API keys: {api_status.missing_api_keys}")
    
    # Test overall validation
    print("\n4. Testing overall validation...")
    overall_result = await validator.validate_all_dependencies()
    print(f"   ✓ Overall validation success: {overall_result.success}")
    print(f"   ✓ Message: {overall_result.message}")
    if overall_result.installation_commands:
        print(f"   ✓ Installation commands: {overall_result.installation_commands}")
    
    print("\n✅ Dependency Validator tests completed!")


async def test_service_manager():
    """Test service management functionality."""
    print("\n" + "=" * 60)
    print("TESTING SERVICE MANAGER")
    print("=" * 60)
    
    config = HealthMonitorConfig()
    manager = ServiceManager(config)
    
    # Test service health checking
    print("\n1. Testing service health checks...")
    for service_name in config.get_all_services():
        health = await manager.check_service_health(service_name)
        print(f"   ✓ {service_name}: {health.status.value} (port {health.port})")
        if health.error_message:
            print(f"     Error: {health.error_message}")
        if health.resource_usage:
            print(f"     Resource usage: {health.resource_usage}")
    
    # Test running services
    print("\n2. Testing running services detection...")
    running = manager.get_running_services()
    print(f"   ✓ Currently running services: {running}")
    
    print("\n✅ Service Manager tests completed!")


async def test_integration():
    """Test integration between components."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION")
    print("=" * 60)
    
    monitor = HealthMonitor()
    
    # Test model discovery through health monitor
    print("\n1. Testing model discovery integration...")
    models = await monitor.discover_models()
    print(f"   ✓ Discovered models: {json.dumps(models, indent=2)}")
    
    # Test API key management through health monitor
    print("\n2. Testing API key management integration...")
    api_status = monitor.get_api_key_status()
    print(f"   ✓ API key status: {json.dumps(api_status, indent=2)}")
    
    # Test setting API key through health monitor
    print("\n3. Testing API key setting...")
    success = monitor.set_api_key("openai", "test-key-integration")
    print(f"   ✓ Set API key: {success}")
    
    print("\n✅ Integration tests completed!")


async def main():
    """Run all tests."""
    print("HEALTH MONITORING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        await test_health_monitor()
        await test_api_key_manager()
        await test_model_discovery()
        await test_dependency_validator()
        await test_service_manager()
        await test_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
