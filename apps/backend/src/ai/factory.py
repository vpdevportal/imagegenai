"""
Factory for creating AI provider instances
"""

import logging
from typing import Optional

from .base.base_image_generator import BaseImageGenerator
from .base.base_prompt_generator import BasePromptGenerator

# Import providers
from .providers.gemini import GeminiImageGenerator, GeminiPromptGenerator
from .providers.replicate import ReplicateImageGenerator
from .providers.stability import StabilityImageGenerator
from .providers.huggingface import HuggingFaceImageGenerator

logger = logging.getLogger(__name__)


class ImageGeneratorFactory:
    """Factory class for creating image generator instances"""
    
    _providers = {
        "gemini": GeminiImageGenerator,
        "replicate": ReplicateImageGenerator,
        "stability": StabilityImageGenerator,
        "huggingface": HuggingFaceImageGenerator,
    }
    
    @classmethod
    def create(cls, provider: str, api_key: Optional[str] = None) -> BaseImageGenerator:
        """
        Create an image generator instance for the specified provider
        
        Args:
            provider: Provider name ("gemini", "replicate", "stability", "huggingface")
            api_key: Optional API key (if not provided, will use environment variables)
            
        Returns:
            BaseImageGenerator: Instance of the requested provider
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower().strip()
        
        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported provider: {provider}. Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_lower]
        logger.info(f"Creating {provider_lower} image generator")
        
        try:
            return provider_class(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to create {provider_lower} generator: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())


class PromptGeneratorFactory:
    """Factory class for creating prompt generator instances"""
    
    _providers = {
        "gemini": GeminiPromptGenerator,
    }
    
    @classmethod
    def create(cls, provider: str, api_key: Optional[str] = None) -> BasePromptGenerator:
        """
        Create a prompt generator instance for the specified provider
        
        Args:
            provider: Provider name (currently only "gemini" is supported)
            api_key: Optional API key (if not provided, will use environment variables)
            
        Returns:
            BasePromptGenerator: Instance of the requested provider
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower().strip()
        
        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported provider for prompt generation: {provider}. Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_lower]
        logger.info(f"Creating {provider_lower} prompt generator")
        
        try:
            return provider_class(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to create {provider_lower} prompt generator: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())

