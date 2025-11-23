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

        return f"""Describe this image focusing on physical characteristics relevant for generating a similar realistic mobile photo. 
                {style_instruction}. {detail_instruction}. Emphasize a natural, candid, handheld mobile camera look with realistic exposure, slight sensor noise, natural skin tones, and authentic ambient lighting. Avoid studio perfection.
                
                Focus specifically on:
                - Body type and physique
                - Breast size and shape
                - Facial features and expressions (preserve identity)
                - Clothing and styling (colors, fabric, fit)
                - Pose, body positioning, and framing
                - Overall realism and natural appeal (mobile camera quality)
                
                Make it a concise, descriptive prompt suitable for AI image generation. Keep the response under 1000 characters."""
    
    def fusion_prompt(self) -> str:
        """
        Generate a prompt for fusing two people together into a natural, casual photo
        
        Returns:
            str: The fusion prompt to use
        """
        return "You are given TWO separate images, each containing ONE person. Your task is to create a NEW image that shows BOTH people together in the same photo. IMPORTANT: You must combine both people from the two images into a single scene - do NOT just return one of the original images. Create a casual, natural photo showing both people together in a realistic moment. The image should look like it was taken with a mobile camera, showing them in a relaxed, authentic pose together. CRITICAL: Preserve the exact faces from BOTH images with maximum accuracy - keep all facial features, expressions, skin tone, hair, and distinctive characteristics exactly as they appear in the original images. Both people must appear together in the final image, merged naturally into one scene that feels like a candid moment. The photo should have natural lighting, casual composition, and feel like a spontaneous mobile camera capture with realistic quality and atmosphere. Make sure BOTH people are visible together in the final result."

    def teleport_prompt(self) -> str:
        """
        Generate a prompt for teleporting a person into a new background scene
        
        Returns:
            str: The teleport prompt to use
        """
        return "Replace the background of the person in the first image with the background from the second image. CRITICAL: Preserve the person's exact face, facial features, body type, clothing, and pose from the first image without any changes. The person should remain in sharp focus with clear details. Crop and adjust the background from the second image to match the aspect ratio, framing, and composition style of the first image - if the person is in a close-up shot, zoom in on the background; if it's a wide shot, keep the background wide. The background framing should complement the person's shot type (portrait, mid-shot, full-body, etc.). Ensure realistic proportions and scale - the person's size should match the perspective and depth of the new background. Apply consistent lighting, shadows, and color grading so the person appears to be lit by the same light sources as the background. The final result should be a seamless, photorealistic image where the person from the first image looks like they were originally photographed in the background location from the second image, with matching framing and composition."


# Global instance
prompt_generator = PromptGenerator()

