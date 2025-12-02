import io
from typing import List

from pdf2image import convert_from_bytes
from PIL import Image

# Increase the decompression bomb limit for large PDFs
# Default is ~89M pixels, we increase to 300M
Image.MAX_IMAGE_PIXELS = 300_000_000


def convert_pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[bytes]:
    """
    Convert PDF pages to PNG images.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        dpi: Resolution for conversion (default 150 - good balance for OCR/Vision)
             Lower DPI = smaller images = faster processing
             150 DPI is sufficient for text extraction with Vision API
    
    Returns:
        List of PNG image bytes, one per page
    """
    # Convert PDF to PIL Images
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    
    # Convert each PIL Image to PNG bytes
    result = []
    for img in images:
        # Optionally resize very large images
        max_dimension = 4096  # OpenAI Vision works well up to 4096px
        if img.width > max_dimension or img.height > max_dimension:
            ratio = min(max_dimension / img.width, max_dimension / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        result.append(buffer.getvalue())
    
    return result
