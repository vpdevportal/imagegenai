"""
Grouping Service

Dedicated service for image grouping: generating an image from multiple
person images and a text prompt. Keeps grouping logic separate from
single-image prompt-to-image generation.
"""

import logging
from typing import Tuple, Optional, List

from fastapi import HTTPException, UploadFile

from ..ai.factory import ImageGeneratorFactory
from ..db.config import settings

logger = logging.getLogger(__name__)

# Instruction appended to grouping prompts so the model preserves each person's face
GROUPING_FACE_PRESERVATION_NOTE = (
    " IMPORTANT: You must preserve the exact face and appearance of each person from the "
    "uploaded reference images in the output. The first image is the first person mentioned, "
    "the second image is the second person, and so on. Each person in the generated image "
    "must look like their corresponding reference photo—do not alter or replace their faces."
)


class GroupingService:
    """Service for image grouping: multiple images + text prompt -> single image."""

    def _get_generator(self, provider: Optional[str] = None):
        """Get the image generator for the given provider (defaults to settings)."""
        provider = provider or getattr(settings, "default_ai_provider", "gemini")
        return ImageGeneratorFactory.create(provider)

    async def generate_from_images(
        self,
        prompt: str,
        images: List[UploadFile],
        provider: Optional[str] = None,
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image using multiple person images and a text prompt.

        Args:
            prompt: Text prompt for image generation.
            images: List of uploaded person image files.
            provider: AI provider to use (defaults to gemini).

        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url).

        Raises:
            HTTPException: If generation fails.
        """
        try:
            generator = self._get_generator(provider)
            reference_image_url = generator.process_reference_image(images[0])

            for image in images:
                image.file.seek(0)

            prompt_with_note = (prompt.strip() + GROUPING_FACE_PRESERVATION_NOTE).strip()
            generated_image_data, content_type = generator.generate_from_multiple_images_and_text(
                images, prompt_with_note
            )
            return generated_image_data, content_type, reference_image_url

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Grouping generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Grouping generation failed. Please try again later.",
            )


grouping_service = GroupingService()
