import base64
from fastapi import HTTPException, UploadFile
from PIL import Image
import io

from ..ai.image_to_prompt_generator import get_image_to_prompt_generator
from .prompt_service import prompt_service


class ImageToPromptService:
    """Service for handling image to prompt generation business logic"""
    
    def __init__(self):
        self.generator = get_image_to_prompt_generator()
        self.prompt_service = prompt_service
    
    async def generate_prompt_from_image(
        self,
        file: UploadFile,
        style: str = "photorealistic",
        detail_level: str = "detailed"
    ) -> dict:
        """
        Generate a prompt from an uploaded image
        
        Args:
            file: Uploaded image file
            style: Style for prompt generation
            detail_level: Detail level for prompt generation
            
        Returns:
            dict: Response containing prompt, thumbnail, and metadata
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            contents = await file.read()
            
            try:
                image = Image.open(io.BytesIO(contents))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
            
            prompt = await self.generator.generate_prompt_from_image(
                image=image,
                style=style,
                detail_level=detail_level
            )
            
            thumbnail_data = self.generator.generate_thumbnail(image)
            
            try:
                saved_prompt = await self.prompt_service.create_prompt(
                    prompt_text=prompt,
                    model="gemini-2.5-flash",
                    thumbnail_data=thumbnail_data,
                    source="inspire_tab"
                )
                prompt_id = saved_prompt.id
            except Exception:
                prompt_id = None
            
            return {
                "success": True,
                "prompt": prompt,
                "style": style,
                "detail_level": detail_level,
                "thumbnail": base64.b64encode(thumbnail_data).decode('utf-8'),
                "original_filename": file.filename,
                "prompt_id": prompt_id,
                "saved_to_database": prompt_id is not None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")


# Global service instance
image_to_prompt_service = ImageToPromptService()
