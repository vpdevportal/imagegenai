"""
Thumbnail generation utilities
"""
import io
import logging
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Utility for generating thumbnails"""
    
    @staticmethod
    def generate_thumbnail(
        image_path: str,
        max_size: int = 256,
        quality: int = 60,
        format: str = "WEBP"
    ) -> Dict[str, Any]:
        """Generate thumbnail from image file"""
        try:
            with Image.open(image_path) as img:
                return ThumbnailGenerator._process_image(img, max_size, quality, format)
        except Exception as e:
            logger.error(f"Failed to generate thumbnail from {image_path}: {e}")
            return ThumbnailGenerator._error_result(str(e))
    
    @staticmethod
    def generate_thumbnail_from_bytes(
        image_data: bytes,
        max_size: int = 256,
        quality: int = 60,
        format: str = "WEBP"
    ) -> Dict[str, Any]:
        """Generate thumbnail from image bytes"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return ThumbnailGenerator._process_image(img, max_size, quality, format)
        except Exception as e:
            logger.error(f"Failed to generate thumbnail from bytes: {e}")
            return ThumbnailGenerator._error_result(str(e))
    
    @staticmethod
    def _process_image(
        img: Image.Image,
        max_size: int,
        quality: int,
        format: str
    ) -> Dict[str, Any]:
        """Process image to create thumbnail"""
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Generate thumbnail
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        width, height = img.size
        
        # Save to bytes
        output = io.BytesIO()
        
        if format.upper() == "WEBP":
            img.save(output, format="WEBP", quality=quality, method=6)
            mime_type = "image/webp"
        elif format.upper() == "JPEG":
            img.save(output, format="JPEG", quality=quality, optimize=True)
            mime_type = "image/jpeg"
        elif format.upper() == "PNG":
            img.save(output, format="PNG", optimize=True)
            mime_type = "image/png"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        thumbnail_data = output.getvalue()
        size_bytes = len(thumbnail_data)
        
        return {
            "success": True,
            "thumbnail_data": thumbnail_data,
            "mime_type": mime_type,
            "width": width,
            "height": height,
            "size_bytes": size_bytes,
            "error": None
        }
    
    @staticmethod
    def _error_result(error: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            "success": False,
            "thumbnail_data": None,
            "mime_type": None,
            "width": None,
            "height": None,
            "size_bytes": None,
            "error": error
        }
