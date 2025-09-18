from PIL import Image
import io
import base64
from typing import Optional
import os
from google import genai
from ..utils.thumbnail import ThumbnailGenerator
from ..db.config import settings

class ImageToPromptGenerator:
    """
    Generator for creating prompts from images using Google Gemini AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image to Prompt Generator
        
        Args:
            api_key: Google AI API key. If not provided, will look for GOOGLE_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY') or getattr(settings, 'GOOGLE_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_AI_API_KEY environment variable")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"
    
    
    async def generate_prompt_from_image(
        self, 
        image: Image.Image, 
        style: str = "photorealistic",
        detail_level: str = "detailed"
    ) -> str:
        """
        Generate a descriptive prompt from an image using Gemini AI
        """
        try:
            style_instructions = {
                "photorealistic": "Focus on photorealistic details, high resolution, sharp focus, realistic lighting and textures",
                "artistic": "Describe in an artistic way, focus on creative interpretation, expressive style, artistic elements",
                "minimalist": "Keep it minimal and clean, focus on essential elements, simple composition, elegant design",
                "vintage": "Describe with vintage aesthetic, retro style, nostalgic elements, film photography feel",
                "modern": "Focus on contemporary design, sleek and clean, modern aesthetic, current trends",
                "abstract": "Describe abstract elements, non-representational aspects, creative interpretation, artistic abstraction"
            }
            
            detail_instructions = {
                "simple": "Keep the description concise and simple, focus on main elements only",
                "detailed": "Provide a detailed description including colors, composition, mood, and key elements",
                "comprehensive": "Give a comprehensive description with intricate details, complex composition, professional quality"
            }
            
            style_instruction = style_instructions.get(style, style_instructions["photorealistic"])
            detail_instruction = detail_instructions.get(detail_level, detail_instructions["detailed"])
            
            prompt_content = [
                image,
                f"""Describe this image in detail, focusing on elements relevant for generating a similar picture. 
                {style_instruction}. {detail_instruction}.
                
                Include:
                - Main subjects and objects
                - Colors and lighting
                - Composition and framing
                - Style and mood
                - Textures and materials
                - Background and setting
                
                Make it a concise, descriptive prompt suitable for AI image generation."""
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[image, prompt_content],
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate prompt from image: {e}")
    
    def generate_thumbnail(self, image: Image.Image, size: tuple = (150, 150)) -> bytes:
        """
        Generate a thumbnail from the image using the utility function
        """
        return ThumbnailGenerator.generate_thumbnail_from_pil_image(image, size)


# Global instance - will be created when first imported
image_to_prompt_generator = None

def get_image_to_prompt_generator():
    """Get or create the global image to prompt generator instance"""
    global image_to_prompt_generator
    if image_to_prompt_generator is None:
        image_to_prompt_generator = ImageToPromptGenerator()
    return image_to_prompt_generator
