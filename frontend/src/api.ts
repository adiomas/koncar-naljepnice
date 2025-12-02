import type { LabelData, NarudzbaData } from "./types";

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export type OutputFormat = 'pdf' | 'png';

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

export interface GenerateLabelsResult {
  blob: Blob;
  filename: string;
  mimeType: string;
}

export async function generateLabels(
  labels: LabelData[], 
  format: OutputFormat = 'pdf'
): Promise<GenerateLabelsResult> {
  const response = await fetch(`${API_BASE}/generate-pdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ labels, format }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate labels');
  }

  const arrayBuffer = await response.arrayBuffer();
  
  if (format === 'png') {
    // PNG format returns a ZIP file
    return {
      blob: new Blob([arrayBuffer], { type: 'application/zip' }),
      filename: 'naljepnice.zip',
      mimeType: 'application/zip'
    };
  } else {
    // PDF format
    return {
      blob: new Blob([arrayBuffer], { type: 'application/pdf' }),
      filename: 'naljepnice.pdf',
      mimeType: 'application/pdf'
    };
  }
}

// Legacy function for backwards compatibility
export async function generatePdf(labels: LabelData[]): Promise<Blob> {
  const result = await generateLabels(labels, 'pdf');
  return result.blob;
}
