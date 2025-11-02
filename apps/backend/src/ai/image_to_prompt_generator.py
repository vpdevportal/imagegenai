from PIL import Image
import io
from typing import Optional
import os
import logging
from google import genai
from ..utils.thumbnail import ThumbnailGenerator
from ..db.config import settings
from ..constants import DEFAULT_GEMINI_MODEL

# Configure logging
logger = logging.getLogger(__name__)

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
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = getattr(settings, 'gemini_model', DEFAULT_GEMINI_MODEL)
    
    async def generate_prompt_from_image(
        self, 
        image: Image.Image, 
        style: str = "artistic"
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
            
            detail_instruction = "Provide a detailed description including colors, composition, mood, and key elements"
            style_instruction = style_instructions.get(style, style_instructions["photorealistic"])
            prompt_content = [
                image,
                f"""Describe this image focusing on creating a detailed prompt that will generate a similar image. 
                {style_instruction}. {detail_instruction}.
                
                Focus specifically on:
                - DRESS AND CLOTHING (MOST IMPORTANT): Provide extremely detailed description of the dress, outfit, or clothing:
                  * Exact type of garment (dress, top, skirt, pants, etc.)
                  * Color, pattern, and fabric texture
                  * Cut, fit, and style (sleeveless, V-neck, A-line, etc.)
                  * Fabric details (silk, cotton, denim, etc.) if visible
                  * Length and silhouette of the clothing
                - WEARABLES AND ACCESSORIES (VERY IMPORTANT): Provide detailed description of all wearable items for consistency:
                  * Jewelry (necklaces, earrings, bracelets, rings, etc.) - describe type, material, color, style, and placement
                  * Accessories (belts, bags, hats, scarves, watches, etc.) - describe exactly as seen
                  * Shoes and footwear - describe type, color, style, heel height if applicable
                  * Any decorative elements or accessories on clothing
                  * Ensure all wearable items are described with enough detail to recreate them consistently
                - Body type and physique
                - Breast size and shape
                - Facial features and expressions
                - Hair color, length, and style
                - Skin tone and texture
                - Pose and body positioning
                - Overall attractiveness and appeal
                
                Prioritize detailed clothing/dress and wearable items description above all else so that when this prompt is used to generate an image, it will recreate the same dress and wearables accurately and consistently. Make it a concise, descriptive prompt suitable for AI image generation. Keep the response under 1000 characters."""
            ]
            
            # Generate content using Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=[image, prompt_content],
            )
            
            generated_prompt = response.text.strip()
            
            # Validate and truncate if necessary
            if len(generated_prompt) > 1000:
                generated_prompt = generated_prompt[:1000].rsplit(' ', 1)[0]
            
            return generated_prompt
            
        except Exception as e:
            logger.error(f"Failed to generate prompt from image - error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate prompt from image: {e}")
    


# Global instance
image_to_prompt_generator = ImageToPromptGenerator()
