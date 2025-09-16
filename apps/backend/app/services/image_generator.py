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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        
        # Initialize the model - using gemini-1.5-flash for image generation
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
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
            # Note: Gemini models don't generate images, they're text models
            # For now, we'll create a placeholder image
            # In production, you would integrate with an actual image generation service
            # like DALL-E, Midjourney API, or Stable Diffusion
            
            # Generate unique filename
            image_id = str(uuid.uuid4())
            filename = f"generated_{image_id}.png"
            output_path = self.output_dir / filename
            
            # Create a placeholder image with the prompt text
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 512x512 image
            img = Image.new('RGB', (512, 512), color='lightblue')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Wrap text and draw it
            words = prompt.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > 480:  # If line is too wide
                    if len(current_line) > 1:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw the text
            y = 50
            for line in lines[:8]:  # Limit to 8 lines
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (512 - text_width) // 2
                draw.text((x, y), line, fill='darkblue', font=font)
                y += 40
            
            # Add a note
            draw.text((10, 450), "AI Generated Placeholder", fill='gray', font=font)
            draw.text((10, 480), f"Prompt: {prompt[:50]}...", fill='gray', font=font)
            
            img.save(output_path)
            image_url = f"/generated_images/{filename}"
            
            return image_url, str(output_path)
            
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
            
            # Note: Gemini models don't generate images, they're text models
            # For now, we'll create a placeholder image that combines the reference with the prompt
            # In production, you would integrate with an actual image generation service
            
            # Generate unique filename
            image_id = str(uuid.uuid4())
            filename = f"generated_with_ref_{image_id}.png"
            output_path = self.output_dir / filename
            
            # Create a placeholder image with the prompt text
            from PIL import Image, ImageDraw, ImageFont
            
            # Resize reference image to fit in our canvas
            reference_image.thumbnail((256, 256), Image.Resampling.LANCZOS)
            
            # Create a 512x512 canvas
            canvas = Image.new('RGB', (512, 512), color='lightgray')
            draw = ImageDraw.Draw(canvas)
            
            # Paste reference image in the center
            ref_x = (512 - reference_image.width) // 2
            ref_y = 50
            canvas.paste(reference_image, (ref_x, ref_y))
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw the prompt text below the reference image
            prompt_y = ref_y + reference_image.height + 20
            draw.text((10, prompt_y), f"Reference + Prompt:", fill='black', font=font)
            draw.text((10, prompt_y + 25), f"{prompt[:60]}...", fill='darkblue', font=font)
            
            # Add a note
            draw.text((10, 450), "AI Generated Placeholder", fill='gray', font=font)
            draw.text((10, 480), "Reference image + prompt combination", fill='gray', font=font)
            
            canvas.save(output_path)
            image_url = f"/generated_images/{filename}"
            
            return image_url, str(output_path)
            
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
