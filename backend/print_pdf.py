#!/usr/bin/env python3
"""
Jednostavan ispis PDF-a na Citizen CL-E321 printer.
Koristi: python3 print_pdf.py <putanja_do_pdf> [broj_stranice]
"""

import socket
import sys
import subprocess
from pathlib import Path
from PIL import Image


PRINTER_IP = "192.168.48.67"
PRINTER_PORT = 9100
DPI = 203  # Citizen CL-E321 rezolucija


def image_to_zpl(image: Image.Image) -> str:
    """Konvertiraj sliku u ZPL format."""
    img_bw = image.convert('1')
    width, height = img_bw.size
    bytes_per_row = (width + 7) // 8
    
    graphic_data = []
    for y in range(height):
        row_data = []
        for x_byte in range(bytes_per_row):
            byte_val = 0
            for bit in range(8):
                x = x_byte * 8 + bit
                if x < width:
                    pixel = img_bw.getpixel((x, y))
                    if pixel == 0:  # crna
                        byte_val |= (1 << (7 - bit))
            row_data.append(f'{byte_val:02X}')
        graphic_data.append(''.join(row_data))
    
    total_bytes = bytes_per_row * height
    data_string = ''.join(graphic_data)
    
    return f'^XA^FO0,0^GFA,{total_bytes},{total_bytes},{bytes_per_row},{data_string}^FS^XZ'


def send_to_printer(zpl: str) -> bool:
    """Pošalji ZPL na printer."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((PRINTER_IP, PRINTER_PORT))
            sock.sendall(zpl.encode('utf-8'))
        return True
    except socket.error as e:
        print(f"❌ Greška: {e}")
        return False


def pdf_to_images(pdf_path: str) -> list:
    """Konvertiraj PDF u slike koristeći pdftoppm (poppler)."""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Koristi pdftoppm za konverziju (dolazi s poppler)
        output_prefix = os.path.join(tmpdir, "page")
        
        try:
            subprocess.run([
                "pdftoppm", "-png", "-r", str(DPI),
                pdf_path, output_prefix
            ], check=True, capture_output=True)
        except FileNotFoundError:
            print("❌ pdftoppm nije instaliran. Instaliraj ga sa: brew install poppler")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Greška pri konverziji PDF-a: {e}")
            sys.exit(1)
        
        # Učitaj generirane slike
        images = []
        for f in sorted(Path(tmpdir).glob("page-*.png")):
            img = Image.open(f)
            images.append(img.copy())  # copy jer će se tmpdir obrisati
        
        return images


def print_pdf(pdf_path: str, page_index: int = None):
    """Isprintaj PDF na Citizen printer."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ Datoteka ne postoji: {pdf_path}")
        sys.exit(1)
    
    print(f"📄 Učitavam PDF: {pdf_path}")
    images = pdf_to_images(str(pdf_path))
    print(f"📊 Pronađeno {len(images)} stranica")
    
    if page_index is not None:
        if page_index >= len(images):
            print(f"❌ Stranica {page_index} ne postoji (PDF ima {len(images)} stranica)")
            sys.exit(1)
        images = [images[page_index]]
        print(f"🎯 Printam samo stranicu {page_index + 1}")
    
    # 100mm @ 203 DPI = 800 px
    target_size = int(100 * DPI / 25.4)
    
    for i, img in enumerate(images):
        print(f"🖨️  Printam stranicu {i + 1}/{len(images)}...")
        
        # Resize na točnu veličinu
        img_resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Konvertiraj u ZPL i pošalji
        zpl = image_to_zpl(img_resized)
        if send_to_printer(zpl):
            print(f"   ✅ Stranica {i + 1} poslana")
        else:
            print(f"   ❌ Greška kod stranice {i + 1}")
    
    print("🎉 Gotovo!")


def print_image(image_path: str):
    """Isprintaj sliku na Citizen printer."""
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"❌ Datoteka ne postoji: {image_path}")
        sys.exit(1)
    
    print(f"🖼️  Učitavam sliku: {image_path}")
    img = Image.open(image_path)
    
    # 100mm @ 203 DPI = 800 px
    target_size = int(100 * DPI / 25.4)
    img_resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    print(f"📐 Veličina: {target_size}x{target_size} px")
    print(f"🔌 Šaljem na {PRINTER_IP}:{PRINTER_PORT}...")
    
    zpl = image_to_zpl(img_resized)
    if send_to_printer(zpl):
        print("✅ Gotovo!")
    else:
        print("❌ Greška pri slanju")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📖 Korištenje:")
        print("   python3 print_pdf.py <datoteka.pdf>           # Printaj sve stranice")
        print("   python3 print_pdf.py <datoteka.pdf> 0         # Printaj samo prvu stranicu")
        print("   python3 print_pdf.py <slika.png>              # Printaj sliku")
        print("")
        print(f"🖨️  Printer: {PRINTER_IP}:{PRINTER_PORT}")
        sys.exit(0)
    
    file_path = sys.argv[1]
    page_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        print_pdf(file_path, page_idx)
    elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
        print_image(file_path)
    else:
        print(f"❌ Nepodržana datoteka: {ext}")
        print("   Podržano: .pdf, .png, .jpg, .jpeg, .bmp, .gif")
        sys.exit(1)

