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

        return f"""Generate a rich, detailed description of this image that will be used WITH the reference image to create variations. Start your response with "USE THIS WITH THE REFERENCE IMAGE:" followed by the description.
                
                {style_instruction}. {detail_instruction}. Emphasize a natural, candid, handheld mobile camera look with realistic exposure, slight sensor noise, natural skin tones, and authentic ambient lighting. Avoid studio perfection.
                
                IMPORTANT: Body type, build, and proportions will be automatically preserved from the reference image - do NOT describe them. Provide comprehensive details for the following modifiable aspects:
                
                Format your response with the following labeled sections (use the exact labels shown):
                                
                FACE: [Provide detailed description of facial features to preserve: eye color and shape, nose structure, lip fullness and color, face shape, skin tone and texture, expressions, distinctive features, and identity characteristics]
                
                CLOTHING: [Provide detailed description of clothing: specific garment types, exact colors and patterns, fabric textures and materials, fit (tight/loose/fitted), how much it reveals body shapes and curves (degree of revelation), how it emphasizes silhouette and contours, accessories, and overall fashion aesthetic]
                
                POSE: [Provide detailed description of the pose: specific body positioning, arm and leg placement, head angle and tilt, camera angle (eye-level/low/high), shot framing (close-up/mid/full), and overall composition]
                
                BREAST: [Provide detailed description of the desired breast size (small/medium/large/etc.) and shape - this can be modified from the reference image]

                BACKGROUND: [Provide detailed description of the setting: indoor/outdoor, specific location type, colors and lighting, environmental elements, depth and focus, and overall atmosphere]
                
                CAMERA: [Provide detailed description of the mobile camera characteristics: lighting quality (natural/artificial/mixed), exposure level, color temperature, sharpness, any natural blur or bokeh effects]
                \
                Be thorough and specific in each section. Keep the total response under 1000 characters. Each section should be on a new line with its label."""
    
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

