import io
from datetime import datetime
from typing import List

from weasyprint import HTML

from .models import LabelData


def generate_label_html(label: LabelData) -> str:
    """Generate HTML for a single label."""
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
                <td class="value-cell" colspan="3">{label.naziv}</td>
            </tr>
            <tr>
                <td class="label-cell">Novi broj<br>dijela</td>
                <td class="value-cell">{label.novi_broj_dijela}</td>
                <td class="label-cell small">Stari broj<br>dijela</td>
                <td class="value-cell small">{label.stari_broj_dijela}</td>
            </tr>
            <tr>
                <td class="label-cell">Količina</td>
                <td class="value-cell" colspan="3">{label.kolicina}</td>
            </tr>
            <tr>
                <td class="label-cell">Narudžba</td>
                <td class="value-cell">{label.narudzba}</td>
                <td class="label-cell small">Account<br>assign.<br>Category</td>
                <td class="value-cell small">{label.account_category}</td>
            </tr>
            <tr>
                <td class="label-cell">Naziv<br>objekta</td>
                <td class="value-cell" colspan="3">{label.naziv_objekta}</td>
            </tr>
            <tr>
                <td class="label-cell">WBS</td>
                <td class="value-cell" colspan="3">{label.wbs}</td>
            </tr>
            <tr>
                <td class="label-cell">Datum</td>
                <td class="value-cell">{label.datum}</td>
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
    background-color: #FFD700;
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
}

.content-table td {
    border: 0.3mm solid black;
    vertical-align: middle;
}

.label-cell {
    width: 18mm;
    padding: 1.5mm 2mm;
    font-size: 8pt;
    font-weight: normal;
    background-color: #FFD700;
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
    min-height: 7mm;
    word-break: break-word;
}

.value-cell.small {
    width: 12mm;
    font-size: 8pt;
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


def generate_labels_pdf(labels: List[LabelData]) -> bytes:
    """
    Generate a PDF with all labels.
    
    Args:
        labels: List of label data
    
    Returns:
        PDF file as bytes (compatible with macOS Preview, Windows, and browsers)
    """
    # Generate HTML with metadata for better compatibility
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f'''
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
        # Don't use PDF/A variant (can cause issues with some viewers)
        # Instead use standard PDF with proper metadata
    )
    
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()
