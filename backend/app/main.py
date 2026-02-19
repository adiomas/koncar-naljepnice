import os
import traceback

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .extraction import extract_data_from_images
from .label_generator import generate_labels_pdf, generate_labels_png
from .models import GenerateLabelsRequest, NarudzbaData, OutputFormat
from .pdf_processor import convert_pdf_to_images

app = FastAPI(
    title="Končar Naljepnice API",
    description="API za ekstrakciju podataka iz narudžbenica i generiranje QA naljepnica",
    version="1.0.0"
)

# CORS middleware - allow frontend origins
# In production, set FRONTEND_URL environment variable
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
if frontend_url:
    allowed_origins.append(frontend_url)
    # Also allow www version and without trailing slash
    if frontend_url.startswith("https://"):
        allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)


@app.get("/")
async def root():
    return {"message": "Končar Naljepnice API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


MAX_FILE_SIZE = 30 * 1024 * 1024  # 30MB
MAX_LABELS = 100


@app.post("/extract", response_model=NarudzbaData)
async def extract_from_pdf(file: UploadFile = File(...)):
    """
    Extract order data from a PDF file.

    Accepts a PDF file, converts pages to images, and uses OpenAI Vision
    to extract structured data about items in the order.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Samo PDF datoteke su podržane")

    try:
        # Read PDF content
        pdf_bytes = await file.read()

        if len(pdf_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Datoteka je prevelika ({len(pdf_bytes) // (1024*1024)}MB). Maksimum je 30MB."
            )

        # Convert PDF to images
        images = convert_pdf_to_images(pdf_bytes)

        if not images:
            raise HTTPException(status_code=400, detail="Nije moguće ekstrahirati stranice iz PDF-a")

        # Extract data using OpenAI Vision
        data = extract_data_from_images(images)

        return data

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Greška pri obradi PDF-a: {str(e)}")


@app.post("/generate-pdf")
async def generate_labels(request: GenerateLabelsRequest):
    """
    Generate labels in the specified format.
    
    Supports:
    - PDF: Single PDF file with one label per page (100mm x 100mm)
    - PNG: ZIP file containing PNG images at 300 DPI (optimized for thermal label printers)
    """
    try:
        if not request.labels:
            raise HTTPException(status_code=400, detail="Nema naljepnica za generiranje")

        if len(request.labels) > MAX_LABELS:
            raise HTTPException(
                status_code=400,
                detail=f"Previše naljepnica ({len(request.labels)}). Maksimum je {MAX_LABELS}."
            )

        if request.format == OutputFormat.PNG:
            # Generate PNG ZIP for label printers
            zip_bytes = generate_labels_png(request.labels, dpi=300)
            return Response(
                content=zip_bytes,
                media_type="application/zip",
                headers={
                    "Content-Disposition": 'attachment; filename="naljepnice.zip"',
                    "Content-Length": str(len(zip_bytes)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
        else:
            # Generate PDF (default)
            pdf_bytes = generate_labels_pdf(request.labels)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": 'attachment; filename="naljepnice.pdf"',
                    "Content-Length": str(len(pdf_bytes)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Greška pri generiranju naljepnica: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
