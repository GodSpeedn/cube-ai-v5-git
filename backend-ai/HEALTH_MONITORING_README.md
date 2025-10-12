# Health Monitoring System

A comprehensive health monitoring and management system for the AI coding assistant platform. This system provides real-time monitoring of services, dependency validation, API key management, and model discovery.

## Features

### 🏥 System Health Monitoring
- **Real-time service status** - Monitor backend, frontend, and database services
- **Resource usage tracking** - CPU, memory, and process monitoring
- **Port availability checking** - Automatic port conflict detection
- **Service uptime tracking** - Monitor how long services have been running
- **Health check endpoints** - HTTP health checks for each service

### 🔧 Dependency Management
- **Python dependency validation** - Check installed packages against requirements.txt
- **Node.js dependency validation** - Verify npm packages are installed
- **Installation guidance** - Generate specific installation commands for missing dependencies
- **Troubleshooting suggestions** - Provide actionable solutions for common issues

### 🔑 API Key Management
- **Secure key storage** - Environment variable-based storage with masking
- **Real-time validation** - Test API keys with actual provider endpoints
- **Multi-provider support** - OpenAI, Anthropic, Hugging Face, Cohere
- **Validation caching** - Cache validation results to reduce API calls

### 🤖 Model Discovery
- **Automatic model discovery** - Fetch available models from all configured providers
- **Capability detection** - Identify model capabilities (chat, text generation, etc.)
- **Model information** - Context length, max tokens, descriptions
- **Search and filtering** - Find models by name, capability, or provider

### 📊 Dashboard Interface
- **Real-time status updates** - Live monitoring dashboard
- **Service management** - Start/stop services from the UI
- **API key configuration** - Add and manage API keys through the interface
- **Model browser** - Discover and view available models
- **Issue tracking** - View and resolve system issues

## Architecture

```
health_monitoring/
├── __init__.py              # Module initialization
├── models.py                # Data models and enums
├── config.py                # Configuration management
├── health_monitor.py        # Main orchestrator
├── service_manager.py       # Service lifecycle management
├── dependency_validator.py  # Dependency checking
├── api_key_manager.py       # API key management
├── model_discovery.py       # Model discovery service
├── port_checker.py          # Port availability utilities
└── api.py                   # FastAPI endpoints
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend-ai
pip install -r requirements.txt
```

### 2. Start Health Monitoring

```bash
# Option 1: Use the startup script
python start_with_health_monitoring.py

# Option 2: Use the batch file (Windows)
start_health_monitoring.bat
```

### 3. Access the Dashboard

- **Health Monitoring API**: http://localhost:8001
- **Frontend Dashboard**: Navigate to "Health Monitor" tab in the main application

## API Endpoints

### Health Status
- `GET /health` - Get current system health status
- `GET /system-status` - Get detailed system status with resource usage

### Service Management
- `POST /start-services` - Start all configured services
- `POST /stop-services` - Stop all running services
- `GET /services` - Get list of configured and running services

### Dependencies
- `GET /validate-dependencies` - Validate system dependencies

### API Keys
- `GET /api-keys` - Get current API key status
- `POST /api-keys` - Set an API key for a provider

### Models
- `GET /models` - Discover available models from all providers

## Configuration

### Service Configuration

Services are configured in `health_monitoring/config.py`:

```python
ServiceConfig(
    name="backend",
    port=8000,
    health_endpoint="/health",
    startup_command="uvicorn",
    startup_args=["main:app", "--host", "0.0.0.0", "--port", "8000"],
    working_directory="/path/to/backend",
    environment_vars={},
    dependencies=[],
    startup_timeout=45,
    health_check_timeout=10
)
```

### Environment Variables

Required environment variables for API keys:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_API_KEY=your_huggingface_key
COHERE_API_KEY=your_cohere_key
```

## Usage Examples

### Python API

```python
from health_monitoring.health_monitor import HealthMonitor

# Create health monitor
monitor = HealthMonitor()

# Check system health
health_status = await monitor.check_system_health()
print(f"Overall status: {health_status.overall_status}")

# Start services
startup_result = await monitor.start_services()
print(f"Started: {startup_result.started_services}")

# Discover models
models = await monitor.discover_models()
print(f"Found models from {len(models)} providers")

# Set API key
success = monitor.set_api_key("openai", "your-api-key")
print(f"API key set: {success}")
```

### HTTP API

```bash
# Get health status
curl http://localhost:8001/health

# Start services
curl -X POST http://localhost:8001/start-services

# Set API key
curl -X POST http://localhost:8001/api-keys \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "key": "your-api-key"}'

# Discover models
curl http://localhost:8001/models
```

## Testing

### Run Tests

```bash
# Simple test
python test_health_monitoring_simple.py

# Comprehensive test
python test_health_monitoring_comprehensive.py
```

### Test Coverage

The system includes tests for:
- Health monitoring functionality
- Service management
- Dependency validation
- API key management
- Model discovery
- Integration between components

## Troubleshooting

### Common Issues

1. **Port conflicts**: The system automatically detects port conflicts and suggests alternatives
2. **Missing dependencies**: Run the suggested installation commands
3. **API key validation failures**: Check that API keys are valid and have proper permissions
4. **Service startup failures**: Check logs for specific error messages

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check Endpoints

Each service should implement a health check endpoint:
- Backend: `GET /health`
- Frontend: `GET /` (any valid response)
- Database: Connection check

## Development

### Adding New Services

1. Add service configuration to `config.py`
2. Create service controller if needed
3. Update service manager to handle new service type

### Adding New API Providers

1. Add provider enum to `api_key_manager.py`
2. Implement validation method
3. Add model discovery logic to `model_discovery.py`

### Adding New Health Checks

1. Extend `ServiceHealth` model if needed
2. Add check logic to service controller
3. Update health monitor to include new checks

## Security Considerations

- API keys are stored in environment variables
- Keys are masked in logs and UI (only last 4 characters shown)
- Validation results are cached to reduce API calls
- No sensitive data is logged

## Performance

- Health checks are cached for 60 seconds
- Model discovery is cached for 6 hours
- API key validation is cached for 1 hour
- Background monitoring runs every 30 seconds

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Ensure all tests pass

## License

This health monitoring system is part of the AI coding assistant platform.
