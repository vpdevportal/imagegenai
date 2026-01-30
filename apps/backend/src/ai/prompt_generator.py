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
                
                BREAST: [ALWAYS describe as: large breast size with natural shape and proportions. If cleavage is exposed, describe how much is exposed and how it is exposed (e.g., partially visible, fully visible, deep cleavage, subtle cleavage)]

                BACKGROUND: [Describe the setting from the reference image: indoor/outdoor, specific location type, colors and lighting, environmental elements, depth and focus, and overall atmosphere]

                CAMERA: [ALWAYS describe as: mobile camera, low quality, handheld, natural lighting, slight sensor noise, realistic exposure, authentic ambient lighting, casual mobile phone photography style]
                
                Be thorough and specific in each section. Keep the total response under 2000 characters. Each section should be on a new line with its label."""
    
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
        return """You are given TWO images. Your task is to place the person from the FIRST image into the location shown in the SECOND image so the result looks like a real, natural photograph taken in that place.

STEP 1 — ANALYSE THE FIRST IMAGE (the person):
Identify and remember the person: their face (facial structure, skin tone, eyes, nose, mouth), hair (style, color, length), body type, clothing (garments, colors, patterns, fit), and accessories. Preserve this identity in the final image. You do NOT need to keep their pose, angle, or framing from the first image.

STEP 2 — ANALYSE THE SECOND IMAGE (the location):
Analyse the location: type of place, composition, perspective, depth, light direction and mood, shadows, time of day, colors, and scale of the environment. Understand how a real photo of someone in this place would look.

STEP 3 — COMBINE FOR A REAL PHOTO:
Place the person (same face, same clothes, same identity) into the location so it looks like one real photograph taken there. You MAY and SHOULD change anything that makes it look natural: adjust the person’s pose so it fits the scene, change viewing angle or camera viewpoint, change distance or size of the person in frame, reframe the shot (close-up, wide, etc.)—whatever makes the image look like an authentic, candid photo of that person in that location. Match lighting, shadows, and color to the location. The goal is a single image that looks like a real photo, not a cut-paste; the person should feel naturally part of the scene."""


# Global instance
prompt_generator = PromptGenerator()

