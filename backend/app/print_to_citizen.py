#!/usr/bin/env python3
"""
Print PDF labels directly to Citizen CL-E321 thermal printer.
Converts PDF pages to ZPL image format and sends via TCP.
"""

import socket
import sys
from pathlib import Path
from typing import Optional

import pdf2image
from PIL import Image


def image_to_zpl(image: Image.Image, label_width_mm: int = 100, label_height_mm: int = 100) -> str:
    """
    Convert PIL Image to ZPL format using ^GFA (Graphic Field ASCII).
    
    Args:
        image: PIL Image object
        label_width_mm: Label width in mm
        label_height_mm: Label height in mm
    
    Returns:
        ZPL string ready to send to printer
    """
    # Convert to 1-bit black and white
    img_bw = image.convert('1')
    
    # Get image dimensions
    width, height = img_bw.size
    
    # ZPL requires width to be multiple of 8
    bytes_per_row = (width + 7) // 8
    
    # Build graphic data
    graphic_data = []
    for y in range(height):
        row_data = []
        for x_byte in range(bytes_per_row):
            byte_val = 0
            for bit in range(8):
                x = x_byte * 8 + bit
                if x < width:
                    pixel = img_bw.getpixel((x, y))
                    # In ZPL, 1 = black, 0 = white (inverted from PIL)
                    if pixel == 0:  # PIL: 0 = black
                        byte_val |= (1 << (7 - bit))
            row_data.append(f'{byte_val:02X}')
        graphic_data.append(''.join(row_data))
    
    total_bytes = bytes_per_row * height
    data_string = ''.join(graphic_data)
    
    # Build ZPL command
    zpl = f'''
^XA
^FO0,0
^GFA,{total_bytes},{total_bytes},{bytes_per_row},
{data_string}
^FS
^XZ
'''
    return zpl


def print_pdf_to_citizen(
    pdf_path: str,
    printer_ip: str = "192.168.48.67",
    printer_port: int = 9100,
    dpi: int = 203,  # Citizen CL-E321 is 203 DPI
    page_index: Optional[int] = None
) -> int:
    """
    Print a PDF file to Citizen thermal printer.
    
    Args:
        pdf_path: Path to PDF file
        printer_ip: Printer IP address
        printer_port: Printer port (default 9100)
        dpi: Printer DPI (203 for CL-E321)
        page_index: Specific page to print (0-based), None for all pages
    
    Returns:
        Number of pages printed
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    print(f"📄 Loading PDF: {pdf_path}")
    
    # Convert PDF to images at printer DPI
    # 100mm at 203 DPI = 800 pixels
    target_size = int(100 * dpi / 25.4)
    
    images = pdf2image.convert_from_path(
        str(pdf_path),
        dpi=dpi,
        size=(target_size, target_size)
    )
    
    print(f"📊 Found {len(images)} page(s)")
    
    # Filter to specific page if requested
    if page_index is not None:
        if page_index >= len(images):
            raise ValueError(f"Page {page_index} not found (PDF has {len(images)} pages)")
        images = [images[page_index]]
        print(f"🎯 Printing only page {page_index + 1}")
    
    # Connect to printer
    print(f"🔌 Connecting to {printer_ip}:{printer_port}...")
    
    printed = 0
    for i, img in enumerate(images):
        print(f"🖨️  Printing page {i + 1}/{len(images)}...")
        
        # Convert to ZPL
        zpl = image_to_zpl(img)
        
        # Send to printer
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((printer_ip, printer_port))
                sock.sendall(zpl.encode('utf-8'))
                printed += 1
        except socket.error as e:
            print(f"❌ Error printing page {i + 1}: {e}")
            continue
    
    print(f"✅ Done! Printed {printed} page(s)")
    return printed


def print_image_to_citizen(
    image_path: str,
    printer_ip: str = "192.168.48.67",
    printer_port: int = 9100,
    dpi: int = 203
) -> bool:
    """
    Print a PNG/JPG image to Citizen thermal printer.
    
    Args:
        image_path: Path to image file
        printer_ip: Printer IP address
        printer_port: Printer port
        dpi: Printer DPI
    
    Returns:
        True if successful
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"🖼️  Loading image: {image_path}")
    
    # Load and resize image
    img = Image.open(image_path)
    target_size = int(100 * dpi / 25.4)
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    print(f"📐 Resized to {target_size}x{target_size} pixels")
    
    # Convert to ZPL
    zpl = image_to_zpl(img)
    
    # Send to printer
    print(f"🔌 Sending to {printer_ip}:{printer_port}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((printer_ip, printer_port))
            sock.sendall(zpl.encode('utf-8'))
        print("✅ Done!")
        return True
    except socket.error as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python print_to_citizen.py <file.pdf>           # Print all pages")
        print("  python print_to_citizen.py <file.pdf> 0         # Print first page only")
        print("  python print_to_citizen.py <file.png>           # Print image")
        print("")
        print("Options:")
        print("  PRINTER_IP=192.168.48.67  (default)")
        print("  PRINTER_PORT=9100         (default)")
        sys.exit(1)
    
    import os
    file_path = sys.argv[1]
    page_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    printer_ip = os.environ.get("PRINTER_IP", "192.168.48.67")
    printer_port = int(os.environ.get("PRINTER_PORT", "9100"))
    
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        print_pdf_to_citizen(file_path, printer_ip, printer_port, page_index=page_idx)
    elif ext in ('.png', '.jpg', '.jpeg'):
        print_image_to_citizen(file_path, printer_ip, printer_port)
    else:
        print(f"❌ Unsupported file type: {ext}")
        sys.exit(1)



