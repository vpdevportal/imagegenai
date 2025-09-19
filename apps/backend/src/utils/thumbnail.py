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
        logger.info(f"Starting thumbnail generation from file - path: {image_path}, max_size: {max_size}, quality: {quality}, format: {format}")
        
        try:
            with Image.open(image_path) as img:
                logger.debug(f"Image opened successfully - size: {img.size}, mode: {img.mode}")
                result = ThumbnailGenerator._process_image(img, max_size, quality, format)
                if result["success"]:
                    logger.info(f"Thumbnail generated successfully from file - size: {result['width']}x{result['height']}, mime: {result['mime_type']}")
                else:
                    logger.error(f"Thumbnail generation failed from file - error: {result['error']}")
                return result
        except Exception as e:
            logger.error(f"Failed to generate thumbnail from {image_path}: {e}", exc_info=True)
            return ThumbnailGenerator._error_result(str(e))
    
    @staticmethod
    def generate_thumbnail_from_bytes(
        image_data: bytes,
        max_size: int = 256,
        quality: int = 60,
        format: str = "WEBP"
    ) -> Dict[str, Any]:
        """Generate thumbnail from image bytes"""
        logger.info(f"Starting thumbnail generation from bytes - data_size: {len(image_data)} bytes, max_size: {max_size}, quality: {quality}, format: {format}")
        
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                logger.debug(f"Image opened successfully from bytes - size: {img.size}, mode: {img.mode}")
                result = ThumbnailGenerator._process_image(img, max_size, quality, format)
                if result["success"]:
                    logger.info(f"Thumbnail generated successfully from bytes - size: {result['width']}x{result['height']}, mime: {result['mime_type']}")
                else:
                    logger.error(f"Thumbnail generation failed from bytes - error: {result['error']}")
                return result
        except Exception as e:
            logger.error(f"Failed to generate thumbnail from bytes: {e}", exc_info=True)
            return ThumbnailGenerator._error_result(str(e))
    
    @staticmethod
    def _process_image(
        img: Image.Image,
        max_size: int,
        quality: int,
        format: str
    ) -> Dict[str, Any]:
        """Process image to create thumbnail"""
        logger.debug(f"Processing image - original_size: {img.size}, mode: {img.mode}, max_size: {max_size}, quality: {quality}, format: {format}")
        
        # Convert to RGB if necessary
        original_mode = img.mode
        if img.mode in ('RGBA', 'LA', 'P'):
            logger.debug(f"Converting image from {img.mode} to RGB with white background")
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            logger.debug(f"Converting image from {img.mode} to RGB")
            img = img.convert('RGB')
        
        # Generate thumbnail
        logger.debug(f"Generating thumbnail - resizing to max {max_size}x{max_size}")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        width, height = img.size
        logger.debug(f"Thumbnail resized to {width}x{height}")
        
        # Save to bytes
        logger.debug(f"Saving thumbnail as {format.upper()}")
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
            logger.error(f"Unsupported format: {format}")
            raise ValueError(f"Unsupported format: {format}")
        
        thumbnail_data = output.getvalue()
        size_bytes = len(thumbnail_data)
        logger.debug(f"Thumbnail saved - size: {size_bytes} bytes, mime_type: {mime_type}")
        
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
    def generate_thumbnail_from_pil_image(
        image: Image.Image,
        size: tuple = (150, 150),
        quality: int = 85,
        format: str = "JPEG"
    ) -> bytes:
        """Generate thumbnail from PIL Image object"""
        try:
            # Create a copy to avoid modifying the original
            img_copy = image.copy()
            
            # Resize image while maintaining aspect ratio
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img_copy.mode != 'RGB':
                img_copy = img_copy.convert('RGB')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img_copy.save(img_byte_arr, format=format, quality=quality)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            raise Exception(f"Error generating thumbnail: {str(e)}")
    
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
