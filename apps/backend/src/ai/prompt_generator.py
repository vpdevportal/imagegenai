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
        style_instruction = "Focus on photorealistic details, high resolution, sharp focus, realistic lighting and textures"
        return f"""Generate a detailed AI image generation prompt from this image. {style_instruction}. Prioritize clothing and wearables for consistency.

PRIORITY 1 - CLOTHING: Exact garment type, precise colors (primary, secondary, accent colors, gradients, patterns), color shades/tints, pattern details, fabric (silk/cotton/denim), cut/fit/style (sleeveless/V-neck/A-line), length, silhouette. Include neckline details and how it reveals or covers the chest area. Describe all colors accurately and in detail.
PRIORITY 2 - CLEAVAGE & BREAST DETAILS: Describe cleavage visibility (visible/partially visible/covered), amount shown, breast size and shape, how the dress/clothing frames or reveals the chest area, exact positioning and prominence.
PRIORITY 3 - WEARABLES: Jewelry (type, material, color, style, placement), accessories (belts/bags/hats/scarves/watches), shoes (type, color, style, heel height), decorative elements.
PRIORITY 4 - MOOD & CONTEXT: Exact mood (sensual/elegant/casual/professional/playful/romantic), context/setting (indoor/outdoor/location), lighting atmosphere, emotional tone, interaction/activity, overall vibe and feeling.
PRIORITY 5 - FACE PRESERVATION: Describe facial features in extreme detail to preserve the original face - face shape, eye shape/color, eyebrow shape/thickness, nose shape, lip shape/size, chin/jawline, cheekbones, facial structure, unique facial characteristics. Do not include makeup details. The face must look like the original person with only necessary adjustments to match the overall image style and mood. Capture all distinctive facial features that make the person recognizable.
ALSO INCLUDE: Body type/physique, hair (color/length/style), skin tone/texture, pose/positioning, overall appeal.

Output a single concise prompt under 1000 characters suitable for AI image generation. Ensure clothing, cleavage/breast details, mood, context, and especially facial features are described accurately for faithful recreation. The generated image must preserve the original face appearance."""


# Global instance
prompt_generator = PromptGenerator()

