"""
Abstract base class for image generators
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException


class BaseImageGenerator(ABC):
    """Abstract base class for all image generation providers"""
    
    @abstractmethod
    async def generate_from_image_and_text(
        self, 
        image_file: UploadFile, 
        prompt: str
    ) -> Tuple[bytes, str]:
        """
        Generate an image using a reference image and text prompt
        
        Args:
            image_file: Uploaded image file (mandatory)
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using only text prompt (no reference image)
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_from_multiple_images_and_text(
        self, 
        image_files: list, 
        prompt: str
    ) -> Tuple[bytes, str]:
        """
        Generate an image using multiple reference images and text prompt
        
        Args:
            image_files: List of uploaded image files (mandatory)
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        pass
    
    def process_reference_image(self, image_file: UploadFile) -> str:
        """
        Process uploaded reference image and return as data URL
        This is a common utility method that can be overridden if needed
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            str: Data URL of the reference image
        """
        from pathlib import Path
        import base64
        
        try:
            # Read image content
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Determine content type from file extension
            original_filename = image_file.filename or "reference"
            file_extension = Path(original_filename).suffix.lower()
            
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_type_map.get(file_extension, 'image/jpeg')
            
            # Convert to base64 data URL
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            data_url = f"data:{content_type};base64,{image_base64}"
            
            return data_url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process reference image: {str(e)}"
            )

