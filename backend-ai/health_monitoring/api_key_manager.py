"""
API key management system for secure storage and validation.
"""
import os
import hashlib
import base64
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    MISTRAL = "mistral"
    GEMINI = "gemini"


@dataclass
class APIKeyInfo:
    """Information about an API key."""
    provider: APIProvider
    key_hash: str  # Hashed version for storage
    masked_key: str  # Last 4 characters for display
    is_valid: bool
    last_validated: Optional[datetime] = None
    validation_error: Optional[str] = None


class APIKeyManager:
    """Manages API keys with secure storage and validation."""
    
    def __init__(self):
        self.keys: Dict[APIProvider, APIKeyInfo] = {}
        self.validation_cache: Dict[APIProvider, Tuple[bool, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)  # Cache validation results for 1 hour
        
        # Load existing keys from environment
        self._load_keys_from_env()
    
    def _load_keys_from_env(self):
        """Load API keys from keys.txt file."""
        key_mappings = {
            APIProvider.OPENAI: "OPENAI_API_KEY",
            APIProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            APIProvider.HUGGINGFACE: "HUGGINGFACE_API_KEY",
            APIProvider.COHERE: "COHERE_API_KEY",
            APIProvider.MISTRAL: "MISTRAL_API_KEY",
            APIProvider.GEMINI: "GEMINI_API_KEY",
        }
        
        # First try to load from keys.txt file
        keys_file = os.path.join(os.path.dirname(__file__), "..", "keys.txt")
        if os.path.exists(keys_file):
            try:
                with open(keys_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Find matching provider
                            for provider, env_var in key_mappings.items():
                                if key == env_var:
                                    self._store_key(provider, value)
                                    break
            except Exception as e:
                logger.error(f"Error loading keys from file: {str(e)}")
        
        # Fallback to environment variables
        for provider, env_var in key_mappings.items():
            key_value = os.getenv(env_var)
            if key_value:
                self._store_key(provider, key_value)
    
    def _hash_key(self, key: str) -> str:
        """Create a secure hash of the API key."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _mask_key(self, key: str) -> str:
        """Create a masked version of the key for display."""
        if len(key) <= 4:
            return "*" * len(key)
        return "*" * (len(key) - 4) + key[-4:]
    
    def _store_key(self, provider: APIProvider, key: str):
        """Store an API key securely."""
        key_hash = self._hash_key(key)
        masked_key = self._mask_key(key)
        
        self.keys[provider] = APIKeyInfo(
            provider=provider,
            key_hash=key_hash,
            masked_key=masked_key,
            is_valid=False  # Will be validated later
        )
        
        # Store the actual key in environment for immediate use
        env_var = f"{provider.value.upper()}_API_KEY"
        os.environ[env_var] = key
        
        # Also store the actual key in a separate dictionary for retrieval
        if not hasattr(self, '_actual_keys'):
            self._actual_keys = {}
        self._actual_keys[provider] = key
        
        # Save to keys.txt file
        self._save_key_to_file(provider, key)
        
        logger.info(f"Stored API key for {provider.value}")
    
    def _save_key_to_file(self, provider: APIProvider, key: str):
        """Save API key to keys.txt file."""
        try:
            keys_file = os.path.join(os.path.dirname(__file__), "..", "keys.txt")
            env_var = f"{provider.value.upper()}_API_KEY"
            
            # Read existing file
            lines = []
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    lines = f.readlines()
            
            # Update or add the key
            key_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{env_var}="):
                    lines[i] = f"{env_var}={key}\n"
                    key_found = True
                    break
            
            if not key_found:
                lines.append(f"{env_var}={key}\n")
            
            # Write back to file
            with open(keys_file, 'w') as f:
                f.writelines(lines)
                
        except Exception as e:
            logger.error(f"Error saving key to file: {str(e)}")
    
    def set_key(self, provider: str | APIProvider, key: str) -> bool:
        """Set an API key for a provider."""
        try:
            # Convert string to enum if needed
            if isinstance(provider, str):
                try:
                    provider = APIProvider(provider.lower())
                except ValueError:
                    logger.error(f"Invalid provider: {provider}")
                    return False
            
            self._store_key(provider, key)
            return True
        except Exception as e:
            provider_str = provider.value if hasattr(provider, 'value') else str(provider)
            logger.error(f"Failed to set key for {provider_str}: {str(e)}")
            return False
    
    def get_key(self, provider: str | APIProvider) -> Optional[str]:
        """Get the actual API key for a provider."""
        if isinstance(provider, str):
            try:
                provider = APIProvider(provider.lower())
            except ValueError:
                return None
        
        # First try environment variable
        env_var = f"{provider.value.upper()}_API_KEY"
        env_key = os.getenv(env_var)
        if env_key:
            return env_key
        
        # If not in environment, check if we have it stored in memory
        if hasattr(self, '_actual_keys') and provider in self._actual_keys:
            return self._actual_keys[provider]
        
        return None
    
    def get_key_info(self, provider: str | APIProvider) -> Optional[APIKeyInfo]:
        """Get key information (without the actual key)."""
        if isinstance(provider, str):
            try:
                provider = APIProvider(provider.lower())
            except ValueError:
                return None
        return self.keys.get(provider)
    
    def get_masked_key(self, provider: str | APIProvider) -> Optional[str]:
        """Get the masked version of an API key."""
        key_info = self.get_key_info(provider)
        return key_info.masked_key if key_info else None
    
    def get_all_key_info(self) -> Dict[APIProvider, APIKeyInfo]:
        """Get information for all stored keys."""
        return self.keys.copy()
    
    def remove_key(self, provider: APIProvider) -> bool:
        """Remove an API key."""
        try:
            if provider in self.keys:
                del self.keys[provider]
            
            # Remove from environment
            env_var = f"{provider.value.upper()}_API_KEY"
            if env_var in os.environ:
                del os.environ[env_var]
            
            logger.info(f"Removed API key for {provider.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove key for {provider.value}: {str(e)}")
            return False
    
    async def validate_key(self, provider: APIProvider) -> bool:
        """Validate an API key by making a test request."""
        logger.info(f"Starting validation for {provider.value}")
        
        # Check cache first
        if provider in self.validation_cache:
            is_valid, cached_time = self.validation_cache[provider]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Using cached validation result for {provider.value}: {is_valid}")
                return is_valid
        
        key = self.get_key(provider)
        logger.info(f"Retrieved key for {provider.value}: {'Yes' if key else 'No'}")
        if not key:
            logger.warning(f"No key found for {provider.value}")
            return False
        
        try:
            logger.info(f"Testing API key for {provider.value}")
            is_valid = await self._test_api_key(provider, key)
            logger.info(f"API key test result for {provider.value}: {is_valid}")
            
            # Update cache
            self.validation_cache[provider] = (is_valid, datetime.now())
            
            # Update key info
            if provider in self.keys:
                self.keys[provider].is_valid = is_valid
                self.keys[provider].last_validated = datetime.now()
                if not is_valid:
                    self.keys[provider].validation_error = "API key validation failed"
                logger.info(f"Updated key info for {provider.value}: is_valid={is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating key for {provider.value}: {str(e)}")
            if provider in self.keys:
                self.keys[provider].is_valid = False
                self.keys[provider].last_validated = datetime.now()
                self.keys[provider].validation_error = str(e)
            return False
    
    async def validate_all_keys(self) -> Dict[APIProvider, bool]:
        """Validate all stored API keys."""
        logger.info(f"Validating all keys. Found {len(self.keys)} providers: {list(self.keys.keys())}")
        results = {}
        
        for provider in self.keys.keys():
            logger.info(f"Validating key for {provider.value}")
            results[provider] = await self.validate_key(provider)
        
        logger.info(f"Validation results: {results}")
        return results
    
    async def _test_api_key(self, provider: APIProvider, key: str) -> bool:
        """Test an API key by making a real API call."""
        # Skip validation for test keys (for development/testing)
        if self._is_test_key(key):
            logger.info(f"Skipping validation for test key: {provider.value}")
            return True
        
        try:
            if provider == APIProvider.OPENAI:
                return await self._test_openai_key(key)
            elif provider == APIProvider.ANTHROPIC:
                return await self._test_anthropic_key(key)
            elif provider == APIProvider.HUGGINGFACE:
                return await self._test_huggingface_key(key)
            elif provider == APIProvider.COHERE:
                return await self._test_cohere_key(key)
            elif provider == APIProvider.MISTRAL:
                return await self._test_mistral_key(key)
            elif provider == APIProvider.GEMINI:
                return await self._test_gemini_key(key)
            else:
                return False
        except Exception as e:
            logger.error(f"Error testing {provider.value} key: {str(e)}")
            return False
    
    def _is_test_key(self, key: str) -> bool:
        """Check if a key is a test key (for development)."""
        test_patterns = [
            "sk-test",
            "test-",
            "demo-",
            "sample-",
            "fake-",
            "mock-"
        ]
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in test_patterns)
    
    async def _test_openai_key(self, key: str) -> bool:
        """Test OpenAI API key."""
        try:
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    # 200 = valid key, 401 = invalid key, 429 = rate limited but key is valid
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    elif response.status == 429:
                        return True  # Rate limited but key is valid
                    else:
                        # For other status codes, check if we get a proper error response
                        try:
                            data = await response.json()
                            if "error" in data and data["error"].get("type") == "invalid_api_key":
                                return False
                        except:
                            pass
                        return False
        except Exception as e:
            logger.debug(f"OpenAI key validation error: {str(e)}")
            return False
    
    async def _test_anthropic_key(self, key: str) -> bool:
        """Test Anthropic API key."""
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 400:
                        # Check if it's an auth error or just invalid request
                        try:
                            data = await response.json()
                            if "error" in data and "authentication" in data["error"].get("type", "").lower():
                                return False
                        except:
                            pass
                        return True  # Invalid request but auth worked
                    elif response.status == 401:
                        return False
                    else:
                        return False
        except Exception as e:
            logger.debug(f"Anthropic key validation error: {str(e)}")
            return False
    
    async def _test_huggingface_key(self, key: str) -> bool:
        """Test Hugging Face API key."""
        try:
            url = "https://huggingface.co/api/whoami"
            headers = {"Authorization": f"Bearer {key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    else:
                        return False
        except Exception as e:
            logger.debug(f"Hugging Face key validation error: {str(e)}")
            return False
    
    async def _test_cohere_key(self, key: str) -> bool:
        """Test Cohere API key."""
        try:
            url = "https://api.cohere.ai/v1/models"
            headers = {"Authorization": f"Bearer {key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    else:
                        return False
        except Exception as e:
            logger.debug(f"Cohere key validation error: {str(e)}")
            return False

    async def _test_mistral_key(self, key: str) -> bool:
        """Test Mistral API key."""
        try:
            url = "https://api.mistral.ai/v1/models"
            headers = {"Authorization": f"Bearer {key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False
                    else:
                        return False
        except Exception as e:
            logger.debug(f"Mistral key validation error: {str(e)}")
            return False

    async def _test_gemini_key(self, key: str) -> bool:
        """Test Google Gemini API key."""
        try:
            # Public models endpoint requires key as query param
            url = f"https://generativelanguage.googleapis.com/v1/models?key={key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 400:
                        # Check if it's an auth error
                        try:
                            data = await response.json()
                            if "error" in data and data["error"].get("status") == "INVALID_ARGUMENT":
                                return False
                        except:
                            pass
                        return False
                    else:
                        return False
        except Exception as e:
            logger.debug(f"Gemini key validation error: {str(e)}")
            return False
    
    def get_validation_status(self) -> Dict[str, any]:
        """Get current validation status of all keys."""
        status = {}
        
        for provider, key_info in self.keys.items():
            status[provider.value] = {
                "has_key": True,
                "is_valid": key_info.is_valid,
                "masked_key": key_info.masked_key,
                "last_validated": key_info.last_validated.isoformat() if key_info.last_validated else None,
                "validation_error": key_info.validation_error
            }
        
        return status
