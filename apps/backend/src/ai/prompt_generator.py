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
        
        This prompt will be used to edit a user's input image. The generated prompt describes
        elements from the reference image, but when applied, facial features will come from
        the input image being edited.
        
        Returns:
            str: The template prompt text for image-to-prompt generation
        """
        return f"""Generate a detailed description of this reference image. This description will be used to edit a user's input image. Start your response with "USE THIS WITH THE REFERENCE IMAGE:" followed by the description.
                
                CRITICAL INSTRUCTIONS:
                - When this prompt is used to edit a user's input image, the FACE (skin tone, texture, eye color, nose structure, lip color, face shape, all facial features) will come from the INPUT IMAGE being edited, NOT from this reference image. Do NOT describe facial features from the reference - they will be automatically preserved from the input image.
                - The camera is ALWAYS a mobile camera with low quality - describe it as such.
                - Focus on describing modifiable elements: clothing, pose, background, composition, lighting, and style.
                
                Format your response with the following labeled sections (use the exact labels shown):
                                
                FACE: [DO NOT describe facial features from the reference image. State: "Preserve all facial features from the input image - skin tone, texture, eye color, nose structure, lip color, face shape, and all facial characteristics must remain exactly as in the input image being edited"]
                
                CLOTHING: [Describe the clothing from the reference image: specific garment types, exact colors and patterns, fabric textures and materials, fit (tight/loose/fitted), how it reveals body shapes and curves, how it emphasizes silhouette and contours, accessories, and overall fashion aesthetic]
                
                POSE: [Describe the pose from the reference image: specific body positioning, arm and leg placement, head angle and tilt, camera angle (eye-level/low/high), shot framing (close-up/mid/full), and overall composition]
                
                BREAST: [ALWAYS describe as: large or medium breast size with natural shape and proportions]

                BACKGROUND: [Describe the setting from the reference image: indoor/outdoor, specific location type, colors and lighting, environmental elements, depth and focus, and overall atmosphere]
                
                CAMERA: [ALWAYS describe as: mobile camera, low quality, handheld, natural lighting, slight sensor noise, realistic exposure, authentic ambient lighting, casual mobile phone photography style]
                
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

