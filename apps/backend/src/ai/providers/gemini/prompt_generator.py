"""
Gemini Prompt Generator - Refactored from original ImageToPromptGenerator
"""

from typing import Optional
import os
import logging
from PIL import Image
from google import genai

from ...base.base_prompt_generator import BasePromptGenerator
from ....db.config import settings
from ....constants import DEFAULT_GEMINI_MODEL
from ....ai.prompt_generator import prompt_generator

# Configure logging
logger = logging.getLogger(__name__)


class GeminiPromptGenerator(BasePromptGenerator):
    """
    Generator for creating prompts from images using Google Gemini AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Prompt Generator
        
        Args:
            api_key: Google AI API key. If not provided, will look for GOOGLE_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY') or getattr(settings, 'GOOGLE_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_AI_API_KEY environment variable")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = getattr(settings, 'gemini_model', DEFAULT_GEMINI_MODEL)
    
    async def generate_prompt_from_image(self, image: Image.Image) -> str:
        """
        Generate a descriptive prompt from an image using Gemini AI
        """
        try:
            prompt_template = prompt_generator.image_to_prompt_template()
            prompt_content = [
                image,
                prompt_template
            ]
            
            # Generate content using Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt_content,
            )
            
            # Check if response has text content
            if response.text:
                generated_prompt = response.text.strip()
            elif response.candidates and len(response.candidates) > 0:
                # Try to extract text from candidates
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text') and part.text]
                    if text_parts:
                        generated_prompt = ' '.join(text_parts).strip()
                    else:
                        raise Exception("No text content found in response")
                else:
                    raise Exception("Response candidate has no content or parts")
            else:
                raise Exception("No response content or candidates found")
            
            if not generated_prompt:
                raise Exception("Generated prompt is empty")
            
            # Validate and truncate if necessary
            if len(generated_prompt) > 2000:
                generated_prompt = generated_prompt[:2000].rsplit(' ', 1)[0]
            
            return generated_prompt
            
        except Exception as e:
            logger.error(f"Failed to generate prompt from image - error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate prompt from image: {e}")

