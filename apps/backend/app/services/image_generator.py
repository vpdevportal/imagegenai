"""
Image Generation Service using Google Gemini AI
"""

import os
import uuid
from typing import Optional, Union, Tuple
from pathlib import Path
from io import BytesIO
import base64

import google.generativeai as genai
from PIL import Image
from fastapi import HTTPException

from ..config import settings


class ImageGenerationService:
    """Service for generating images using Google Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Generation Service
        
        Args:
            api_key: Google AI API key. If not provided, will look for GOOGLE_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY') or getattr(settings, 'GOOGLE_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_AI_API_KEY environment variable")
        
        # Configure the Gemini client
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create output directory for generated images
        self.output_dir = Path('generated_images')
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_from_text(self, prompt: str) -> Tuple[str, str]:
        """
        Generate an image from text prompt only
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[str, str]: (image_url, image_path)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Generate image using Gemini
            response = self.model.generate_content(prompt)
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Save the generated image
                            generated_image = Image.open(BytesIO(part.inline_data.data))
                            
                            # Generate unique filename
                            image_id = str(uuid.uuid4())
                            filename = f"generated_{image_id}.png"
                            output_path = self.output_dir / filename
                            
                            generated_image.save(output_path)
                            image_url = f"/generated_images/{filename}"
                            
                            return image_url, str(output_path)
            
            raise Exception("No image data found in response")
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image from text: {str(e)}"
            )
    
    def generate_from_image_and_text(self, image_file, prompt: str) -> Tuple[str, str]:
        """
        Generate an image using a reference image and text prompt
        
        Args:
            image_file: Uploaded image file
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[str, str]: (image_url, image_path)
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Read and process the uploaded image
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Convert to PIL Image
            reference_image = Image.open(BytesIO(image_content))
            
            # Generate image using Gemini with reference image
            response = self.model.generate_content([prompt, reference_image])
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Save the generated image
                            generated_image = Image.open(BytesIO(part.inline_data.data))
                            
                            # Generate unique filename
                            image_id = str(uuid.uuid4())
                            filename = f"generated_with_ref_{image_id}.png"
                            output_path = self.output_dir / filename
                            
                            generated_image.save(output_path)
                            image_url = f"/generated_images/{filename}"
                            
                            return image_url, str(output_path)
            
            raise Exception("No image data found in response")
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image from reference: {str(e)}"
            )
    
    def save_reference_image(self, image_file) -> str:
        """
        Save uploaded reference image and return its URL
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            str: URL of the saved reference image
        """
        try:
            # Read image content
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Generate unique filename
            image_id = str(uuid.uuid4())
            original_filename = image_file.filename or "reference"
            file_extension = Path(original_filename).suffix or ".jpg"
            filename = f"reference_{image_id}{file_extension}"
            
            # Save reference image
            reference_path = self.output_dir / filename
            with open(reference_path, 'wb') as f:
                f.write(image_content)
            
            return f"/generated_images/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save reference image: {str(e)}"
            )


# Global instance
image_generator = ImageGenerationService()
