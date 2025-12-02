# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies (poppler for pdf2image)
RUN apt-get update && apt-get install -y \
    poppler-utils \
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

# Run the application using shell form to expand $PORT
# Railway sets PORT environment variable automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
