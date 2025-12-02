import os
import traceback

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .extraction import extract_data_from_images
from .label_generator import generate_labels_pdf
from .models import GenerateLabelsRequest, NarudzbaData
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


@app.post("/extract", response_model=NarudzbaData)
async def extract_from_pdf(file: UploadFile = File(...)):
    """
    Extract order data from a PDF file.
    
    Accepts a PDF file, converts pages to images, and uses OpenAI Vision
    to extract structured data about items in the order.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        pdf_bytes = await file.read()
        
        # Convert PDF to images
        images = convert_pdf_to_images(pdf_bytes)
        
        if not images:
            raise HTTPException(status_code=400, detail="Could not extract pages from PDF")
        
        # Extract data using OpenAI Vision
        data = extract_data_from_images(images)
        
        return data
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/generate-pdf")
async def generate_pdf(request: GenerateLabelsRequest):
    """
    Generate a PDF with labels from the provided data.
    
    Returns a PDF file with one label per page (100mm x 100mm).
    """
    try:
        if not request.labels:
            raise HTTPException(status_code=400, detail="No labels provided")
        
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
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
