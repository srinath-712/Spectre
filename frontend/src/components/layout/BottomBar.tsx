import React from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { FileText, ShieldAlert, Code2, Clock } from 'lucide-react';
const BACKEND_DOCS_URL = (import.meta.env.VITE_BACKEND_DOCS_URL ?? 'http://localhost:8000/docs');

export const BottomBar: React.FC = () => {
  const result = useForensicStore((state) => state.result);
  const adversarialMode = useForensicStore((state) => state.adversarialMode);
  const setAdversarialMode = useForensicStore((state) => state.setAdversarialMode);
  const exportReport = useForensicStore((state) => state.exportReport);
  const job = useForensicStore((state) => state.job);

  return (
    <div className="absolute inset-x-0 bottom-0 z-30 min-h-14 border-t border-spectre-border bg-spectre-bg/95 px-3 py-2 backdrop-blur-md md:px-6">
      <div className="flex flex-col items-start justify-between gap-2 md:flex-row md:items-center">
      
      {/* Time & Processing Info */}
      <div className="flex items-center gap-4">
        {job?.status === 'completed' && job.endTime && job.startTime ? (
          <div className="flex items-center gap-2 text-xs text-spectre-textDim font-mono">
            <Clock size={12} />
            <span>Analyzed in {((job.endTime.getTime() - job.startTime.getTime()) / 1000).toFixed(2)}s</span>
          </div>
        ) : (
          <div /> // placeholder to keep spacing
        )}
      </div>

      {/* Primary Actions */}
      <div className="flex w-full flex-wrap items-center justify-end gap-3 md:w-auto md:gap-4">
        
        {/* Adversarial Toggle */}
        <div className="flex items-center gap-2 border-r border-spectre-border pr-3 md:pr-4">
          <label className="text-xs font-heading font-medium text-spectre-textMuted cursor-pointer flex items-center gap-2">
            <ShieldAlert size={14} className={adversarialMode ? 'text-spectre-warning' : 'text-spectre-textDim'}/>
            Adversarial Test Mode
            <div className={`relative inline-block w-8 h-4 rounded-full transition-colors ${adversarialMode ? 'bg-spectre-warning' : 'bg-spectre-surface border border-spectre-border'} ml-2`}>
              <input 
                type="checkbox" 
                className="opacity-0 w-0 h-0" 
                checked={adversarialMode}
                onChange={(e) => {
                  void setAdversarialMode(e.target.checked);
                }}
                disabled={!result}
              />
              <span className={`absolute top-0.5 left-0.5 w-3 h-3 rounded-full bg-white transition-transform ${adversarialMode ? 'transform translate-x-4' : ''}`} />
            </div>
          </label>
        </div>

        {/* Action Buttons */}
        <button
          className="text-xs flex items-center gap-1.5 text-spectre-textMuted hover:text-spectre-text transition-colors"
          onClick={() => window.open(BACKEND_DOCS_URL, '_blank', 'noopener,noreferrer')}
        >
          <Code2 size={14} />
          API Docs
        </button>

        <button 
          className={`spectre-btn-primary flex items-center gap-2 py-1.5 ${!result ? 'opacity-50 cursor-not-allowed saturate-0 pointer-events-none' : ''}`}
          disabled={!result}
          onClick={exportReport}
        >
          <FileText size={14} />
          Export Report
        </button>
      </div>
      </div>

    </div>
  );
};
