import tempfile
import os
from typing import Tuple
from fastapi import HTTPException, UploadFile

from ..ai.prompt_to_image_generator import get_prompt_to_image_generator
from .prompt_service import prompt_service


class PromptToImageService:
    """Service for handling prompt to image generation business logic"""
    
    def __init__(self):
        self.generator = get_prompt_to_image_generator()
        self.prompt_service = prompt_service
    
    async def generate_image_from_prompt(
        self, 
        prompt: str, 
        reference_image: UploadFile
    ) -> Tuple[bytes, str, str]:
        """
        Generate an image from a text prompt and reference image
        
        Args:
            prompt: Text prompt for image generation
            reference_image: Uploaded reference image file
            
        Returns:
            Tuple[bytes, str, str]: (image_data, content_type, reference_image_url)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            reference_image_url = self.generator.process_reference_image(reference_image)
            generated_image_data, content_type = self.generator.generate_from_image_and_text(
                reference_image, prompt
            )
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(generated_image_data)
                    temp_file_path = temp_file.name
                
                self.prompt_service.create_or_update_prompt(
                    prompt_text=prompt,
                    model="gemini-2.5-flash-image-preview",
                    image_path=temp_file_path
                )
                
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
            except Exception:
                pass
            
            return generated_image_data, content_type, reference_image_url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )


# Global service instance
prompt_to_image_service = PromptToImageService()
