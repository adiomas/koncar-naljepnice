import type { LabelData, NarudzbaData } from "./types";

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function extractFromPdf(file: File): Promise<NarudzbaData> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to extract data from PDF');
  }

  return response.json();
}

export async function generatePdf(labels: LabelData[]): Promise<Blob> {
  const response = await fetch(`${API_BASE}/generate-pdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ labels }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate PDF');
  }

  // Explicitly create blob with PDF MIME type to ensure macOS Preview compatibility
  const arrayBuffer = await response.arrayBuffer();
  return new Blob([arrayBuffer], { type: 'application/pdf' });
}
