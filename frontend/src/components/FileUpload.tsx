import { useCallback, useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export function FileUpload({ onFileSelect, isLoading }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  return (
    <div
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer
        ${isDragging 
          ? 'border-amber-400 bg-amber-50 scale-[1.02]' 
          : 'border-zinc-300 hover:border-amber-400 hover:bg-amber-50/50'
        }
        ${isLoading ? 'opacity-50 pointer-events-none' : ''}
      `}
    >
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isLoading}
      />
      
      <div className="flex flex-col items-center gap-4 text-center">
        <div className={`
          w-16 h-16 rounded-2xl flex items-center justify-center transition-colors
          ${isDragging ? 'bg-amber-400' : 'bg-zinc-100'}
        `}>
          <svg 
            className={`w-8 h-8 ${isDragging ? 'text-white' : 'text-zinc-500'}`}
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
            />
          </svg>
        </div>
        
        <div>
          <p className="text-lg font-medium text-zinc-800">
            {isLoading ? 'Obrađujem...' : 'Povucite PDF narudžbenicu ovdje'}
          </p>
          <p className="text-sm text-zinc-500 mt-1">
            ili kliknite za odabir datoteke
          </p>
        </div>
        
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Samo PDF datoteke</span>
        </div>
      </div>
    </div>
  );
}



