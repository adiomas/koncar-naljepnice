# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
# - poppler-utils for pdf2image
# - WeasyPrint dependencies (cairo, pango, gobject, etc.)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application using shell form (NOT exec form) for proper variable expansion
# Railway sets PORT environment variable automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
