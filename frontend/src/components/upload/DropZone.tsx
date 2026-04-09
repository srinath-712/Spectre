import React, { useCallback, useState } from 'react';
import { UploadCloud, FileType } from 'lucide-react';
import { useForensicStore } from '../../store/forensicStore';

export const DropZone: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const analyzeFile = useForensicStore((state) => state.analyzeFile);
  const job = useForensicStore((state) => state.job);
  const resetAnalysis = useForensicStore((state) => state.resetAnalysis);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      void analyzeFile(e.dataTransfer.files[0]);
    }
  }, [analyzeFile]);

  const onFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      void analyzeFile(e.target.files[0]);
    }
  }, [analyzeFile]);

  if (job && job.status !== 'error') {
    const canStartNew = job.status !== 'processing' && job.status !== 'uploading';

    return (
      <div className="glass-panel p-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <FileType className="text-spectre-accent" size={24} />
          <div>
            <p className="text-sm font-medium text-spectre-text truncate max-w-[150px]">
              {job.filename}
            </p>
            <p className="text-xs text-spectre-textMuted capitalize">
              {job.status === 'completed' ? 'Completed. Ready for next upload.' : `${job.status}...`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {job.status === 'processing' && (
            <div className="text-right">
              <span className="text-xs font-mono text-spectre-accent">{job.progress}%</span>
            </div>
          )}

          <button
            type="button"
            className={`text-xs rounded-md border border-spectre-border px-2.5 py-1.5 transition-colors ${
              canStartNew
                ? 'text-spectre-text hover:bg-spectre-surface hover:border-spectre-textDim'
                : 'text-spectre-textDim opacity-50 cursor-not-allowed'
            }`}
            onClick={resetAnalysis}
            disabled={!canStartNew}
            title={canStartNew ? 'Clear current analysis and upload a new file' : 'Wait until current analysis finishes'}
          >
            New Analysis
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`upload-zone p-8 flex flex-col items-center justify-center text-center ${isDragging ? 'dragging' : ''}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <input 
        type="file" 
        className="hidden" 
        id="file-upload" 
        accept=".pdf,image/*"
        onChange={onFileInput}
      />
      <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
        <div className="w-12 h-12 rounded-full bg-spectre-accent/10 flex items-center justify-center mb-4">
          <UploadCloud className="text-spectre-accent" size={24} />
        </div>
        <h3 className="font-heading font-medium text-spectre-text mb-1">Upload Document</h3>
        <p className="text-xs text-spectre-textMuted max-w-[200px]">
          Drag and drop your PDF or image here, or click to browse.
        </p>
      </label>
    </div>
  );
};
