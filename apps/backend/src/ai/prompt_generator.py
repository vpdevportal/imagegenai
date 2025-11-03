from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generator for creating prompts for various image generation tasks
    """
    
    def variation_prompt(self, prompt: Optional[str] = None) -> str:
        """
        Generate a variation prompt from an optional user prompt
        
        Args:
            prompt: Optional user-provided prompt. If provided and not empty,
                   appends to the default variation prompt. Otherwise, returns the default variation prompt.
        
        Returns:
            str: The variation prompt to use
        """
        default_prompt = "Generate a variation image keeping the same person, costume, and background, but change only the pose so that it feels like a different click of the same moment"
        
        if prompt and prompt.strip():
            return f"{default_prompt}. {prompt.strip()}"
        return default_prompt
    
    def image_to_prompt_template(self) -> str:
        """
        Get the template prompt for converting images to text prompts
        
        Returns:
            str: The template prompt text for image-to-prompt generation
        """
        style_instruction = "Focus on photorealistic details, realistic lighting and textures"
            
        detail_instruction = "Provide a detailed description including colors, composition, mood, and key elements"

        return f"""Describe this image focusing on body features and physical characteristics relevant for generating a similar picture. 
                {style_instruction}. {detail_instruction}.
                
                Focus specifically on:
                - Body type and physique
                - Breast size and shape
                - Facial features and expressions
                - Hair color, length, and style
                - Skin tone and texture
                - Clothing and styling
                - Pose and body positioning
                - Overall attractiveness and appeal
                
                Make it a concise, descriptive prompt suitable for AI image generation. Keep the response under 1000 characters."""


# Global instance
prompt_generator = PromptGenerator()

