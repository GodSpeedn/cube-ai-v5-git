"""
Model discovery service for discovering available AI models from various providers.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .api_key_manager import APIKeyManager, APIProvider

logger = logging.getLogger(__name__)


class ModelCapability(Enum):
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


@dataclass
class ModelInfo:
    """Information about a discovered model."""
    id: str
    name: str
    provider: APIProvider
    capabilities: List[ModelCapability]
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
    is_available: bool = True
    last_checked: Optional[datetime] = None
    description: Optional[str] = None
    cost_per_token: Optional[float] = None


class ModelDiscoveryService:
    """Discovers and manages information about available AI models."""
    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.discovered_models: Dict[APIProvider, List[ModelInfo]] = {}
        self.cache_ttl = timedelta(hours=6)  # Cache model info for 6 hours
        self.last_discovery: Dict[APIProvider, datetime] = {}
    
    async def discover_all_models(self) -> Dict[APIProvider, List[ModelInfo]]:
        """Discover models from all available providers."""
        logger.info("Starting model discovery for all providers")
        
        # Get all providers with valid API keys
        validation_results = await self.api_key_manager.validate_all_keys()
        available_providers = [p for p, is_valid in validation_results.items() if is_valid]
        
        if not available_providers:
            logger.warning("No providers with valid API keys found")
            return {}
        
        # Discover models from each provider
        discovery_tasks = []
        for provider in available_providers:
            task = asyncio.create_task(self._discover_provider_models(provider))
            discovery_tasks.append(task)
        
        # Wait for all discoveries to complete
        results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            provider = available_providers[i]
            if isinstance(result, Exception):
                logger.error(f"Error discovering models for {provider.value}: {str(result)}")
                self.discovered_models[provider] = []
            else:
                self.discovered_models[provider] = result
                self.last_discovery[provider] = datetime.now()
        
        return self.discovered_models
    
    async def discover_models_for_provider(self, provider: APIProvider) -> List[ModelInfo]:
        """Discover models for a specific provider."""
        logger.info(f"Discovering models for {provider.value}")
        
        # Check if we have a valid API key
        is_valid = await self.api_key_manager.validate_key(provider)
        if not is_valid:
            logger.warning(f"No valid API key for {provider.value}")
            return []
        
        # Check cache
        if (provider in self.last_discovery and 
            datetime.now() - self.last_discovery[provider] < self.cache_ttl and
            provider in self.discovered_models):
            logger.info(f"Using cached model data for {provider.value}")
            return self.discovered_models[provider]
        
        # Discover fresh data
        models = await self._discover_provider_models(provider)
        self.discovered_models[provider] = models
        self.last_discovery[provider] = datetime.now()
        
        return models
    
    async def _discover_provider_models(self, provider: APIProvider) -> List[ModelInfo]:
        """Discover models for a specific provider."""
        try:
            if provider == APIProvider.OPENAI:
                return await self._discover_openai_models()
            elif provider == APIProvider.ANTHROPIC:
                return await self._discover_anthropic_models()
            elif provider == APIProvider.HUGGINGFACE:
                return await self._discover_huggingface_models()
            elif provider == APIProvider.COHERE:
                return await self._discover_cohere_models()
            elif provider == APIProvider.MISTRAL:
                return await self._discover_mistral_models()
            elif provider == APIProvider.GEMINI:
                return await self._discover_gemini_models()
            else:
                logger.warning(f"Model discovery not implemented for {provider.value}")
                return []
        except Exception as e:
            logger.error(f"Error discovering models for {provider.value}: {str(e)}")
            return []
    
    async def _discover_openai_models(self) -> List[ModelInfo]:
        """Discover OpenAI models."""
        try:
            api_key = self.api_key_manager.get_key(APIProvider.OPENAI)
            if not api_key:
                return []
            
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"OpenAI API returned status {response.status}")
                        return []
                    
                    data = await response.json()
                    models = []
                    
                    for model_data in data.get("data", []):
                        model_id = model_data.get("id", "")
                        if not model_id:
                            continue
                        
                        # Determine capabilities based on model ID
                        capabilities = self._get_openai_capabilities(model_id)
                        
                        # Get model details
                        max_tokens = self._get_openai_max_tokens(model_id)
                        context_length = self._get_openai_context_length(model_id)
                        
                        model_info = ModelInfo(
                            id=model_id,
                            name=model_data.get("id", ""),
                            provider=APIProvider.OPENAI,
                            capabilities=capabilities,
                            max_tokens=max_tokens,
                            context_length=context_length,
                            is_available=True,
                            last_checked=datetime.now(),
                            description=model_data.get("description", "")
                        )
                        models.append(model_info)
                    
                    return models
                    
        except Exception as e:
            logger.error(f"Error discovering OpenAI models: {str(e)}")
            return []
    
    async def _discover_anthropic_models(self) -> List[ModelInfo]:
        """Discover Anthropic models."""
        # Anthropic doesn't have a public models endpoint, so we'll use known models
        known_models = [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "capabilities": [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                "max_tokens": 8192,
                "context_length": 200000,
                "description": "Most powerful Claude model for complex tasks"
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "capabilities": [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                "max_tokens": 8192,
                "context_length": 200000,
                "description": "Fast and efficient Claude model"
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "capabilities": [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Most capable Claude 3 model"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "capabilities": [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Balanced Claude 3 model"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "capabilities": [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Fast Claude 3 model"
            }
        ]
        
        models = []
        for model_data in known_models:
            model_info = ModelInfo(
                id=model_data["id"],
                name=model_data["name"],
                provider=APIProvider.ANTHROPIC,
                capabilities=model_data["capabilities"],
                max_tokens=model_data["max_tokens"],
                context_length=model_data["context_length"],
                is_available=True,
                last_checked=datetime.now(),
                description=model_data["description"]
            )
            models.append(model_info)
        
        return models
    
    async def _discover_huggingface_models(self) -> List[ModelInfo]:
        """Discover Hugging Face models."""
        try:
            api_key = self.api_key_manager.get_key(APIProvider.HUGGINGFACE)
            if not api_key:
                return []
            
            # Get popular models from Hugging Face
            url = "https://huggingface.co/api/models"
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            params = {
                "limit": 50,
                "sort": "downloads",
                "direction": -1,
                "filter": "text-generation,text2text-generation,conversational"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"Hugging Face API returned status {response.status}")
                        return []
                    
                    data = await response.json()
                    models = []
                    
                    for model_data in data:
                        model_id = model_data.get("id", "")
                        if not model_id:
                            continue
                        
                        # Determine capabilities based on tags
                        capabilities = self._get_huggingface_capabilities(model_data.get("tags", []))
                        
                        model_info = ModelInfo(
                            id=model_id,
                            name=model_data.get("id", ""),
                            provider=APIProvider.HUGGINGFACE,
                            capabilities=capabilities,
                            is_available=True,
                            last_checked=datetime.now(),
                            description=model_data.get("description", "")
                        )
                        models.append(model_info)
                    
                    return models
                    
        except Exception as e:
            logger.error(f"Error discovering Hugging Face models: {str(e)}")
            return []
    
    async def _discover_cohere_models(self) -> List[ModelInfo]:
        """Discover Cohere models."""
        try:
            api_key = self.api_key_manager.get_key(APIProvider.COHERE)
            if not api_key:
                return []
            
            url = "https://api.cohere.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"Cohere API returned status {response.status}")
                        return []
                    
                    data = await response.json()
                    models = []
                    
                    for model_data in data.get("models", []):
                        model_id = model_data.get("name", "")
                        if not model_id:
                            continue
                        
                        capabilities = self._get_cohere_capabilities(model_data)
                        
                        model_info = ModelInfo(
                            id=model_id,
                            name=model_data.get("display_name", model_id),
                            provider=APIProvider.COHERE,
                            capabilities=capabilities,
                            is_available=True,
                            last_checked=datetime.now(),
                            description=model_data.get("description", "")
                        )
                        models.append(model_info)
                    
                    return models
                    
        except Exception as e:
            logger.error(f"Error discovering Cohere models: {str(e)}")
            return []
    
    def _get_openai_capabilities(self, model_id: str) -> List[ModelCapability]:
        """Determine capabilities for OpenAI models."""
        capabilities = [ModelCapability.TEXT_GENERATION]
        
        if "gpt" in model_id.lower():
            capabilities.append(ModelCapability.CHAT)
            capabilities.append(ModelCapability.CODE_GENERATION)
        
        if "dall-e" in model_id.lower():
            capabilities.append(ModelCapability.IMAGE_GENERATION)
        
        if "embedding" in model_id.lower() or "ada" in model_id.lower():
            capabilities.append(ModelCapability.EMBEDDINGS)
        
        return capabilities
    
    def _get_anthropic_capabilities(self, model_id: str) -> List[ModelCapability]:
        """Determine capabilities for Anthropic models."""
        return [ModelCapability.CHAT, ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION]
    
    def _get_huggingface_capabilities(self, tags: List[str]) -> List[ModelCapability]:
        """Determine capabilities for Hugging Face models."""
        capabilities = []
        
        if any(tag in ["text-generation", "text2text-generation"] for tag in tags):
            capabilities.append(ModelCapability.TEXT_GENERATION)
        
        if "conversational" in tags:
            capabilities.append(ModelCapability.CHAT)
        
        if "code" in tags:
            capabilities.append(ModelCapability.CODE_GENERATION)
        
        if "summarization" in tags:
            capabilities.append(ModelCapability.SUMMARIZATION)
        
        if "translation" in tags:
            capabilities.append(ModelCapability.TRANSLATION)
        
        return capabilities
    
    def _get_cohere_capabilities(self, model_data: Dict) -> List[ModelCapability]:
        """Determine capabilities for Cohere models."""
        capabilities = [ModelCapability.TEXT_GENERATION]
        
        # Cohere models typically support chat and other text tasks
        capabilities.extend([
            ModelCapability.CHAT,
            ModelCapability.SUMMARIZATION,
            ModelCapability.TRANSLATION
        ])
        
        return capabilities
    
    def _get_openai_max_tokens(self, model_id: str) -> Optional[int]:
        """Get max tokens for OpenAI models."""
        if "gpt-4" in model_id:
            return 8192
        elif "gpt-3.5" in model_id:
            return 4096
        return None
    
    def _get_openai_context_length(self, model_id: str) -> Optional[int]:
        """Get context length for OpenAI models."""
        if "gpt-4" in model_id:
            return 128000
        elif "gpt-3.5" in model_id:
            return 16385
        return None
    
    def get_models_by_capability(self, capability: ModelCapability) -> List[ModelInfo]:
        """Get all models that support a specific capability."""
        models = []
        for provider_models in self.discovered_models.values():
            for model in provider_models:
                if capability in model.capabilities:
                    models.append(model)
        return models
    
    def get_models_by_provider(self, provider: APIProvider) -> List[ModelInfo]:
        """Get all models from a specific provider."""
        return self.discovered_models.get(provider, [])
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """Search models by name or description."""
        query_lower = query.lower()
        matching_models = []
        
        for provider_models in self.discovered_models.values():
            for model in provider_models:
                if (query_lower in model.name.lower() or 
                    (model.description and query_lower in model.description.lower())):
                    matching_models.append(model)
        
        return matching_models
    
    async def _discover_mistral_models(self) -> List[ModelInfo]:
        """Discover Mistral models."""
        try:
            api_key = self.api_key_manager.get_key(APIProvider.MISTRAL)
            if not api_key:
                return []
            
            url = "https://api.mistral.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        
                        for model_data in data.get("data", []):
                            model_info = ModelInfo(
                                id=model_data["id"],
                                name=model_data.get("name", model_data["id"]),
                                provider=APIProvider.MISTRAL,
                                capabilities=self._get_mistral_capabilities(model_data),
                                max_tokens=model_data.get("max_tokens"),
                                context_length=model_data.get("context_length"),
                                is_available=True,
                                last_checked=datetime.now(),
                                description=model_data.get("description")
                            )
                            models.append(model_info)
                        
                        return models
                    else:
                        logger.warning(f"Mistral API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error discovering Mistral models: {str(e)}")
            return []
    
    async def _discover_gemini_models(self) -> List[ModelInfo]:
        """Discover Google Gemini models."""
        try:
            api_key = self.api_key_manager.get_key(APIProvider.GEMINI)
            if not api_key:
                return []
            
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        
                        for model_data in data.get("models", []):
                            model_info = ModelInfo(
                                id=model_data["name"].split("/")[-1],  # Extract model name from full path
                                name=model_data.get("displayName", model_data["name"]),
                                provider=APIProvider.GEMINI,
                                capabilities=self._get_gemini_capabilities(model_data),
                                max_tokens=model_data.get("inputTokenLimit"),
                                context_length=model_data.get("inputTokenLimit"),
                                is_available=True,
                                last_checked=datetime.now(),
                                description=model_data.get("description")
                            )
                            models.append(model_info)
                        
                        return models
                    else:
                        logger.warning(f"Gemini API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error discovering Gemini models: {str(e)}")
            return []
    
    def _get_mistral_capabilities(self, model_data: Dict) -> List[ModelCapability]:
        """Determine capabilities for Mistral models."""
        capabilities = [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]
        
        # Add specific capabilities based on model type
        model_id = model_data.get("id", "").lower()
        if "code" in model_id:
            capabilities.append(ModelCapability.CODE_GENERATION)
        if "embed" in model_id:
            capabilities.append(ModelCapability.EMBEDDINGS)
        
        return capabilities
    
    def _get_gemini_capabilities(self, model_data: Dict) -> List[ModelCapability]:
        """Determine capabilities for Gemini models."""
        capabilities = [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]
        
        # Add specific capabilities based on model type
        model_name = model_data.get("name", "").lower()
        if "code" in model_name:
            capabilities.append(ModelCapability.CODE_GENERATION)
        if "embed" in model_name:
            capabilities.append(ModelCapability.EMBEDDINGS)
        if "vision" in model_name or "multimodal" in model_name:
            capabilities.append(ModelCapability.IMAGE_GENERATION)
        
        return capabilities
