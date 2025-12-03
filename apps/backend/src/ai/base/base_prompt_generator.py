"""
Abstract base class for prompt generators (image-to-prompt)
"""

from abc import ABC, abstractmethod
from PIL import Image


class BasePromptGenerator(ABC):
    """Abstract base class for image-to-prompt generation providers"""
    
    @abstractmethod
    async def generate_prompt_from_image(self, image: Image.Image) -> str:
        """
        Generate a descriptive prompt from an image
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Generated prompt text
            
        Raises:
            Exception: If generation fails
        """
        pass

