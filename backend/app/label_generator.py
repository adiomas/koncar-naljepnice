import io
import zipfile
from datetime import datetime
from typing import List, Literal

import pdf2image
from PIL import Image
from weasyprint import HTML

from .models import LabelData


def calculate_font_size(text: str, max_chars: int, base_font_pt: float = 9.0, min_font_pt: float = 5.0) -> float:
    """
    Calculate the appropriate font size to fit text in a single line.
    
    Args:
        text: The text content
        max_chars: Maximum characters that fit at base font size
        base_font_pt: Base font size in points (default: 9pt)
        min_font_pt: Minimum font size in points (default: 5pt)
    
    Returns:
        Calculated font size in points
    """
    if not text:
        return base_font_pt
    
    text_len = len(text)
    if text_len <= max_chars:
        return base_font_pt
    
    # Scale font size proportionally
    ratio = max_chars / text_len
    new_size = base_font_pt * ratio
    
    # Don't go below minimum
    return max(new_size, min_font_pt)


def get_dynamic_style(text: str, max_chars: int, base_font_pt: float = 9.0) -> str:
    """
    Get inline style for dynamic font sizing.
    
    Args:
        text: The text content
        max_chars: Maximum characters that fit at base font size
        base_font_pt: Base font size in points
    
    Returns:
        Inline style string
    """
    font_size = calculate_font_size(text, max_chars, base_font_pt)
    if font_size < base_font_pt:
        return f'style="font-size: {font_size:.1f}pt;"'
    return ''


def generate_label_html(label: LabelData) -> str:
    """Generate HTML for a single label."""
    # Calculate dynamic font sizes for each field
    # Available width for full-span value cell: ~72mm, which fits ~40 chars at 9pt
    # Available width for half-span value cell: ~32mm, which fits ~18 chars at 9pt
    
    naziv_style = get_dynamic_style(label.naziv, 40, 9.0)
    novi_broj_style = get_dynamic_style(label.novi_broj_dijela, 18, 9.0)
    stari_broj_style = get_dynamic_style(label.stari_broj_dijela, 10, 8.0)
    kolicina_style = get_dynamic_style(label.kolicina, 40, 9.0)
    narudzba_style = get_dynamic_style(label.narudzba, 18, 9.0)
    account_style = get_dynamic_style(label.account_category, 8, 8.0)
    naziv_objekta_style = get_dynamic_style(label.naziv_objekta, 40, 9.0)
    wbs_style = get_dynamic_style(label.wbs, 40, 9.0)
    datum_style = get_dynamic_style(label.datum, 18, 9.0)
    
    return f'''
    <div class="label">
        <div class="header">
            <div class="header-left">
                <div class="company-name">Končar</div>
                <div class="company-subtitle">Energetski transformatori d.o.o.</div>
            </div>
            <div class="header-right">
                <div class="qa-title">QA IDENT KARTA</div>
                <div class="qa-subtitle">- Dobavni dijelovi -</div>
            </div>
        </div>
        
        <table class="content-table">
            <tr>
                <td class="label-cell">Naziv</td>
                <td class="value-cell" colspan="3" {naziv_style}>{label.naziv}</td>
            </tr>
            <tr>
                <td class="label-cell">Novi broj<br>dijela</td>
                <td class="value-cell" {novi_broj_style}>{label.novi_broj_dijela}</td>
                <td class="label-cell small">Stari broj<br>dijela</td>
                <td class="value-cell small" {stari_broj_style}>{label.stari_broj_dijela}</td>
            </tr>
            <tr>
                <td class="label-cell">Količina</td>
                <td class="value-cell" colspan="3" {kolicina_style}>{label.kolicina}</td>
            </tr>
            <tr>
                <td class="label-cell">Narudžba</td>
                <td class="value-cell" {narudzba_style}>{label.narudzba}</td>
                <td class="label-cell small">Account<br>assign.<br>Category</td>
                <td class="value-cell small" {account_style}>{label.account_category}</td>
            </tr>
            <tr>
                <td class="label-cell">Naziv<br>objekta</td>
                <td class="value-cell" colspan="3" {naziv_objekta_style}>{label.naziv_objekta}</td>
            </tr>
            <tr>
                <td class="label-cell">WBS</td>
                <td class="value-cell" colspan="3" {wbs_style}>{label.wbs}</td>
            </tr>
            <tr>
                <td class="label-cell">Datum</td>
                <td class="value-cell" {datum_style}>{label.datum}</td>
                <td class="value-cell" colspan="2"></td>
            </tr>
        </table>
        
        <div class="footer">KPT-OI-077</div>
    </div>
    '''


LABEL_CSS = '''
@page {
    size: 100mm 100mm;
    margin: 0;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9pt;
    line-height: 1.2;
}

.label {
    width: 100mm;
    height: 100mm;
    background-color: #FFFFFF;
    padding: 4mm;
    page-break-after: always;
    position: relative;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 2mm;
    margin-bottom: 2mm;
}

.header-left {
    text-align: left;
}

.company-name {
    font-size: 16pt;
    font-weight: bold;
    line-height: 1.1;
}

.company-subtitle {
    font-size: 11pt;
    font-weight: bold;
}

.header-right {
    text-align: right;
}

.qa-title {
    font-size: 12pt;
    font-weight: bold;
}

.qa-subtitle {
    font-size: 9pt;
}

.content-table {
    width: 100%;
    border-collapse: collapse;
    border: 0.5mm solid black;
    table-layout: fixed;
}

.content-table td {
    border: 0.3mm solid black;
    vertical-align: middle;
    overflow: hidden;
}

.label-cell {
    width: 18mm;
    padding: 1.5mm 2mm;
    font-size: 8pt;
    font-weight: normal;
    background-color: #FFFFFF;
    line-height: 1.1;
}

.label-cell.small {
    width: 14mm;
    font-size: 7pt;
    padding: 1mm 1.5mm;
}

.value-cell {
    padding: 1.5mm 2mm;
    font-size: 9pt;
    font-weight: bold;
    height: 7mm;
    max-height: 7mm;
    overflow: hidden;
    white-space: nowrap;
}

.value-cell.small {
    width: 12mm;
    font-size: 8pt;
    font-weight: bold;
}

.footer {
    position: absolute;
    bottom: 3mm;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 10pt;
    font-weight: bold;
}
'''


def generate_html_content(labels: List[LabelData]) -> str:
    """Generate complete HTML document for labels."""
    return f'''
    <!DOCTYPE html>
    <html lang="hr">
    <head>
        <meta charset="UTF-8">
        <title>QA Identifikacijske Kartice - Končar</title>
        <meta name="author" content="Končar Energetski Transformatori d.o.o.">
        <meta name="generator" content="WeasyPrint">
        <meta name="keywords" content="QA, identifikacija, naljepnice, Končar">
        <meta name="description" content="QA identifikacijske kartice za {len(labels)} artikala">
        <style>{LABEL_CSS}</style>
    </head>
    <body>
        {''.join(generate_label_html(label) for label in labels)}
    </body>
    </html>
    '''


def generate_labels_pdf(labels: List[LabelData]) -> bytes:
    """
    Generate a PDF with all labels.
    
    Args:
        labels: List of label data
    
    Returns:
        PDF file as bytes (compatible with macOS Preview, Windows, and browsers)
    """
    html_content = generate_html_content(labels)
    
    pdf_buffer = io.BytesIO()
    
    # Generate PDF with compatibility options
    HTML(string=html_content).write_pdf(
        pdf_buffer,
        # Use PDF 1.7 for maximum compatibility (macOS Preview, Windows, browsers)
        pdf_version='1.7',
        # Include sRGB color profile for consistent colors
        srgb=True,
        # Optimize images for smaller file size
        optimize_images=True,
        # JPEG quality (85 is good balance)
        jpeg_quality=85,
    )
    
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()


def generate_labels_png(labels: List[LabelData], dpi: int = 300) -> bytes:
    """
    Generate PNG images of all labels as a ZIP file.
    
    Each label is rendered as a separate PNG file at 300 DPI,
    perfect for thermal label printers (100mm x 100mm = ~1181x1181 pixels at 300 DPI).
    
    Args:
        labels: List of label data
        dpi: Resolution in dots per inch (default: 300 for thermal printers)
    
    Returns:
        ZIP file containing PNG images as bytes
    """
    # First generate PDF
    pdf_bytes = generate_labels_pdf(labels)
    
    # Convert PDF pages to images at specified DPI
    # 100mm at 300 DPI = 1181 pixels
    images = pdf2image.convert_from_bytes(
        pdf_bytes,
        dpi=dpi,
        fmt='png',
        # Use exact 100mm x 100mm size
        size=(int(100 * dpi / 25.4), int(100 * dpi / 25.4))
    )
    
    # Create ZIP file with all PNG images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, image in enumerate(images, 1):
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            zip_file.writestr(f'naljepnica_{i:03d}.png', img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_single_label_png(labels: List[LabelData], index: int = 0, dpi: int = 300) -> bytes:
    """
    Generate a single PNG image of a specific label.
    
    Args:
        labels: List of label data
        index: Index of label to render (0-based)
        dpi: Resolution in dots per inch (default: 300)
    
    Returns:
        PNG image as bytes
    """
    if index >= len(labels):
        raise ValueError(f"Label index {index} out of range (0-{len(labels)-1})")
    
    # Generate HTML for single label
    single_label = [labels[index]]
    pdf_bytes = generate_labels_pdf(single_label)
    
    # Convert to PNG
    images = pdf2image.convert_from_bytes(
        pdf_bytes,
        dpi=dpi,
        fmt='png',
        size=(int(100 * dpi / 25.4), int(100 * dpi / 25.4))
    )
    
    if images:
        img_buffer = io.BytesIO()
        images[0].save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        return img_buffer.getvalue()
    
    raise ValueError("Failed to generate PNG image")
