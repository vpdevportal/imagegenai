"""
Prompt to Image Generator using Google Gemini AI
"""

import os
from typing import Optional, Tuple
from pathlib import Path
from io import BytesIO
import base64
import logging

from google import genai
from PIL import Image
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..db.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class PromptToImageGenerator:
    """Service for generating images using Google Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Prompt to Image Generator
        
        Args:
            api_key: Google AI API key. If not provided, will look for GOOGLE_AI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY') or getattr(settings, 'GOOGLE_AI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_AI_API_KEY environment variable")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash-image-preview"
        
        logger.info("Prompt to image generator initialized")
        
        # No longer creating output directory since we use in-memory processing
    
    def generate_from_image_and_text(self, image_file, prompt: str) -> Tuple[bytes, str]:
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
        try:
            # Read and process the uploaded image
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            
            # Convert to PIL Image
            reference_image = Image.open(BytesIO(image_content))
            
            # Generate the image using Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, reference_image],
            )
            
            # Process the response and return image data
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data is not None:
                            # Return the generated image data directly
                            image_data = part.inline_data.data
                            content_type = "image/png"  # Gemini typically returns PNG
                            return image_data, content_type

            raise HTTPException(
                status_code=500,
                detail="Failed to generate image from reference: No image data found in response"
            )
                
        except Exception as e:
            logger.error(f"Failed to generate image from reference: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image from reference: {str(e)}"
            )
    
    def process_reference_image(self, image_file) -> str:
        """
        Process uploaded reference image and return as data URL
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            str: Data URL of the reference image
        """
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
            logger.error(f"Failed to process reference image: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process reference image: {str(e)}"
            )


# Global instance
prompt_to_image_generator = PromptToImageGenerator()
