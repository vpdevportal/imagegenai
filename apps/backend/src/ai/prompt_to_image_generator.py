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
from ..constants import DEFAULT_GEMINI_MODEL

# Configure logging
logger = logging.getLogger(__name__)


def log_error_reason(response):
    """Log detailed error reasons when response candidates are empty and return error details"""
    if len(response.candidates) == 0:
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
            block_reason = response.prompt_feedback.block_reason
            safety_ratings = getattr(response.prompt_feedback, 'safety_ratings', None)
            
            logger.error(f"Response was blocked. Block reason: {block_reason}")
            
            error_details = [f"Block reason: {block_reason}"]
            
            if safety_ratings:
                for rating in safety_ratings:
                    category = getattr(rating, 'category', 'Unknown')
                    probability = getattr(rating, 'probability', 'Unknown')
                    logger.error(f"  - Category: {category}, Probability: {probability}")
                    error_details.append(f"Category: {category}, Probability: {probability}")
            
            return True, "; ".join(error_details)
        else:
            logger.error("Response has no candidates but no block reason found")
            return True, "Response has no candidates but no block reason found"
    return False, None


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
        self.model = getattr(settings, 'gemini_model', DEFAULT_GEMINI_MODEL)
        
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
        logger.info(f"Starting AI image generation - prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}', model: {self.model}")
        
        # Read and process the uploaded image
        logger.info("Reading uploaded image content")
        image_content = image_file.file.read()
        image_file.file.seek(0)  # Reset file pointer
        logger.info(f"Image content read - size: {len(image_content)} bytes")
        
        # Convert to PIL Image
        logger.debug("Converting image content to PIL Image")
        reference_image = Image.open(BytesIO(image_content))
        logger.info(f"PIL Image created - size: {reference_image.size}, mode: {reference_image.mode}")
        
        # Generate the image using Gemini
        logger.info(f"Calling Gemini API - model: {self.model}")
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, reference_image],
        )
        logger.info(f"Gemini API response received - has_candidates: {bool(response.candidates)}")
        logger.info(f"Gemini API response received - has_candidates: {len(response.candidates)}")

        # Process the response and return image data
        if bool(response.candidates) and len(response.candidates) > 0:
            logger.info(f"Processing response - candidates_count: {len(response.candidates)}")
            candidate = response.candidates[0]
            logger.info(f"Processing candidate - has_content: {bool(candidate.content)}, has_parts: {bool(candidate.content.parts) if candidate.content else False}")
            
            if candidate.content and candidate.content.parts:
                logger.info(f"Processing parts - parts_count: {len(candidate.content.parts)}")
                for i, part in enumerate(candidate.content.parts):
                    logger.info(f"Processing part {i} - has_inline_data: {bool(part.inline_data)}")
                    if part.inline_data is not None:
                        # Return the generated image data directly
                        image_data = part.inline_data.data
                        content_type = "image/png"  # Gemini typically returns PNG
                        logger.info(f"Image generation successful - data_size: {len(image_data)} bytes, content_type: {content_type}")
                        return image_data, content_type
                    else:
                        logger.info(f"Part {i} has no inline data")
            else:
                logger.warning("Candidate has no content or parts")
        else:
            # Log detailed error reasons when candidates are empty
            is_blocked, error_details = log_error_reason(response)
            logger.warning(f"Gemini response error details: is_blocked={is_blocked}, error_details={error_details}")
            
            if is_blocked:
                detail_message = f"Image generation was blocked due to content policy violations: {error_details}"
                raise HTTPException(
                    status_code=400,
                    detail=detail_message
                )
            else:
                logger.warning("Response has no candidates")

        logger.error("No image data found in Gemini response")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image from reference: No image data found in response"
        )
    
    def generate_from_text(self, prompt: str) -> Tuple[bytes, str]:
        """
        Generate an image using only text prompt (no reference image)
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            Tuple[bytes, str]: (image_data, content_type)
            
        Raises:
            HTTPException: If generation fails
        """
        logger.info(f"Starting AI image generation from text only - prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}', model: {self.model}")
        
        try:
            # Generate the image using Gemini with text only
            logger.info(f"Calling Gemini API with text only - model: {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
            )
            logger.info(f"Gemini API response received - has_candidates: {bool(response.candidates)}")
            
            # Process the response and return image data
            if response.candidates and len(response.candidates) > 0:
                logger.info(f"Processing response - candidates_count: {len(response.candidates)}")
                candidate = response.candidates[0]
                logger.info(f"Processing candidate - has_content: {bool(candidate.content)}, has_parts: {bool(candidate.content.parts) if candidate.content else False}")
                
                if candidate.content and candidate.content.parts:
                    logger.info(f"Processing parts - parts_count: {len(candidate.content.parts)}")
                    for i, part in enumerate(candidate.content.parts):
                        logger.info(f"Processing part {i} - has_inline_data: {bool(part.inline_data)}")
                        if part.inline_data is not None:
                            # Return the generated image data directly
                            image_data = part.inline_data.data
                            content_type = "image/png"  # Gemini typically returns PNG
                            logger.info(f"Image generation successful - data_size: {len(image_data)} bytes, content_type: {content_type}")
                            return image_data, content_type
                        else:
                            logger.info(f"Part {i} has no inline data")
                else:
                    logger.warning("Candidate has no content or parts")
            else:
                # Log detailed error reasons when candidates are empty
                is_blocked, error_details = log_error_reason(response)
                logger.error(f"### log_error_reason: is_blocked={is_blocked}, error_details={error_details}")
                if is_blocked:
                    detail_message = f"Image generation was blocked due to content policy violations: {error_details}"
                    raise HTTPException(
                        status_code=400,
                        detail=detail_message
                    )
                else:
                    logger.warning("Response has no candidates")

            logger.error("No image data found in Gemini response")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate image from text: No image data found in response"
            )
                
        except Exception as e:
            logger.error(f"Failed to generate image from text: {str(e)}", exc_info=True)
            # Extract clean error message from Google API errors
            error_message = "Image generation failed. Please try again later."
            if hasattr(e, 'details') and isinstance(e.details, dict):
                if 'message' in e.details:
                    error_message = e.details['message']
            elif hasattr(e, 'message'):
                error_message = e.message
            elif str(e).startswith('503'):
                error_message = "The service is currently unavailable."
            elif str(e).startswith('400'):
                error_message = "Invalid request. Please check your input."
            elif str(e).startswith('401'):
                error_message = "Authentication failed. Please check your API key."
            elif str(e).startswith('429'):
                error_message = "Rate limit exceeded. Please try again later."
            
            raise HTTPException(
                status_code=500,
                detail=error_message
            )
    
    def process_reference_image(self, image_file) -> str:
        """
        Process uploaded reference image and return as data URL
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            str: Data URL of the reference image
        """
        logger.info(f"Processing reference image - filename: {image_file.filename}")
        
        try:
            # Read image content
            logger.info("Reading reference image content")
            image_content = image_file.file.read()
            image_file.file.seek(0)  # Reset file pointer
            logger.info(f"Reference image content read - size: {len(image_content)} bytes")
            
            # Determine content type from file extension
            original_filename = image_file.filename or "reference"
            file_extension = Path(original_filename).suffix.lower()
            logger.info(f"Determining content type - filename: {original_filename}, extension: {file_extension}")
            
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = content_type_map.get(file_extension, 'image/jpeg')
            logger.info(f"Content type determined: {content_type}")
            
            # Convert to base64 data URL
            logger.info("Converting image to base64")
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            data_url = f"data:{content_type};base64,{image_base64}"
            logger.info(f"Reference image processed successfully - data_url_length: {len(data_url)}")
            
            return data_url
            
        except Exception as e:
            logger.error(f"Failed to process reference image: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process reference image: {str(e)}"
            )


# Global instance
prompt_to_image_generator = PromptToImageGenerator()
