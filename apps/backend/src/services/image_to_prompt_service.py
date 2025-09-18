from PIL import Image
import io
import base64
from typing import Dict, Any
import json
import os
import google.generativeai as genai

class ImageToPromptService:
    """
    Service for generating prompts from images using Google Gemini AI
    """
    
    def __init__(self):
        # Configure Gemini AI using existing GOOGLE_AI_API_KEY
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.model_loaded = True
    
    async def generate_prompt_from_image(
        self, 
        image: Image.Image, 
        style: str = "photorealistic",
        detail_level: str = "detailed"
    ) -> str:
        """
        Generate a descriptive prompt from an image using Gemini AI
        """
        try:
            # Create the prompt for the model based on style and detail level
            style_instructions = {
                "photorealistic": "Focus on photorealistic details, high resolution, sharp focus, realistic lighting and textures",
                "artistic": "Describe in an artistic way, focus on creative interpretation, expressive style, artistic elements",
                "minimalist": "Keep it minimal and clean, focus on essential elements, simple composition, elegant design",
                "vintage": "Describe with vintage aesthetic, retro style, nostalgic elements, film photography feel",
                "modern": "Focus on contemporary design, sleek and clean, modern aesthetic, current trends",
                "abstract": "Describe abstract elements, non-representational aspects, creative interpretation, artistic abstraction"
            }
            
            detail_instructions = {
                "simple": "Keep the description concise and simple, focus on main elements only",
                "detailed": "Provide a detailed description including colors, composition, mood, and key elements",
                "comprehensive": "Give a comprehensive description with intricate details, complex composition, professional quality"
            }
            
            style_instruction = style_instructions.get(style, style_instructions["photorealistic"])
            detail_instruction = detail_instructions.get(detail_level, detail_instructions["detailed"])
            
            # Create the prompt for Gemini
            prompt_content = [
                image,
                f"""Describe this image in detail, focusing on elements relevant for generating a similar picture. 
                {style_instruction}. {detail_instruction}.
                
                Include:
                - Main subjects and objects
                - Colors and lighting
                - Composition and framing
                - Style and mood
                - Textures and materials
                - Background and setting
                
                Make it a concise, descriptive prompt suitable for AI image generation."""
            ]
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt_content)
            
            if response and response.candidates:
                generated_description = response.candidates[0].content.parts[0].text
                return generated_description.strip()
            else:
                # Fallback to basic analysis if Gemini fails
                return self._generate_fallback_prompt(image, style, detail_level)
            
        except Exception as e:
            # Fallback to basic analysis if Gemini fails
            print(f"Gemini API error: {e}")
            return self._generate_fallback_prompt(image, style, detail_level)
    
    def _generate_fallback_prompt(self, image: Image.Image, style: str, detail_level: str) -> str:
        """
        Fallback method using basic image analysis
        """
        try:
            width, height = image.size
            colors = self._analyze_colors(image)
            composition = self._analyze_composition(width, height)
            
            # Generate style-specific prompt
            base_description = f"A {composition} image with {colors} color palette"
            
            if style == "photorealistic":
                prompt = f"Photorealistic {base_description}, high resolution, detailed, sharp focus"
            elif style == "artistic":
                prompt = f"Artistic interpretation of {base_description}, creative, expressive, stylized"
            elif style == "minimalist":
                prompt = f"Minimalist {base_description}, clean lines, simple composition, elegant"
            elif style == "vintage":
                prompt = f"Vintage {base_description}, retro style, aged, nostalgic, film photography"
            elif style == "modern":
                prompt = f"Modern {base_description}, contemporary, sleek, clean design"
            elif style == "abstract":
                prompt = f"Abstract {base_description}, non-representational, creative, artistic"
            else:
                prompt = base_description
            
            # Add detail level modifiers
            if detail_level == "simple":
                prompt = prompt.split(',')[0]  # Take only the first part
            elif detail_level == "comprehensive":
                prompt += ", intricate details, complex composition, professional quality"
            
            return prompt
            
        except Exception as e:
            return f"An image with {style} style"
    
    def generate_thumbnail(self, image: Image.Image, size: tuple = (150, 150)) -> bytes:
        """
        Generate a thumbnail from the image
        """
        try:
            # Resize image while maintaining aspect ratio
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr
            
        except Exception as e:
            raise Exception(f"Error generating thumbnail: {str(e)}")
    
    def _analyze_colors(self, image: Image.Image) -> str:
        """
        Analyze the dominant colors in the image
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get color palette
            colors = image.getcolors(maxcolors=256*256*256)
            if not colors:
                return "neutral"
            
            # Sort by frequency
            colors.sort(key=lambda x: x[0], reverse=True)
            
            # Get top 3 colors
            top_colors = colors[:3]
            color_names = []
            
            for count, (r, g, b) in top_colors:
                # Simple color classification
                if r > 200 and g > 200 and b > 200:
                    color_names.append("bright")
                elif r < 50 and g < 50 and b < 50:
                    color_names.append("dark")
                elif r > g and r > b:
                    color_names.append("warm")
                elif g > r and g > b:
                    color_names.append("cool")
                else:
                    color_names.append("neutral")
            
            # Return unique color descriptions
            unique_colors = list(set(color_names))
            if len(unique_colors) == 1:
                return unique_colors[0]
            else:
                return f"{unique_colors[0]} and {unique_colors[1]}" if len(unique_colors) >= 2 else unique_colors[0]
                
        except Exception:
            return "neutral"
    
    def _analyze_composition(self, width: int, height: int) -> str:
        """
        Analyze the composition based on aspect ratio
        """
        ratio = width / height
        
        if ratio > 1.5:
            return "wide landscape"
        elif ratio < 0.67:
            return "portrait"
        elif 0.8 <= ratio <= 1.2:
            return "square"
        else:
            return "landscape"
