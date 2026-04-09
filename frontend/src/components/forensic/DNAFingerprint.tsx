import React from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { Fingerprint, Copy } from 'lucide-react';

export const DNAFingerprint: React.FC = () => {
  const result = useForensicStore((state) => state.result);

  if (!result || !result.dna) return null;

  const handleCopy = () => {
    void navigator.clipboard.writeText(result.dna.hash);
  };

  return (
    <div className="mt-6 glass-panel p-4">
      <div className="flex items-center gap-2 mb-3">
        <Fingerprint size={16} className="text-spectre-accent" />
        <h4 className="font-heading font-semibold text-sm">Document DNA</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <span className="text-xs text-spectre-textMuted block mb-1">DNA ID</span>
          <div className="text-xs font-mono text-spectre-text px-3 py-1.5 bg-spectre-surface rounded rounded-lg border border-spectre-border truncate mb-2">
            {result.dna.id}
          </div>
          <span className="text-xs text-spectre-textMuted block mb-1">Perceptual Hash Grid</span>
          <div className="flex items-center justify-between bg-spectre-surface px-3 py-2 rounded-lg border border-spectre-border">
            <code className="text-xs font-mono text-spectre-accent tracking-widest">{result.dna.hash}</code>
            <button 
              onClick={handleCopy}
              className="text-spectre-textMuted hover:text-spectre-accent transition-colors"
              title="Copy Hash"
            >
              <Copy size={14} />
            </button>
          </div>
        </div>

        <div>
           <span className="text-xs text-spectre-textMuted block mb-1">Scanner Noise Profile</span>
           <div className="text-xs font-mono text-spectre-text px-3 py-1.5 bg-spectre-surface rounded rounded-lg border border-spectre-border truncate">
             {result.dna.scannerProfile}
           </div>
        </div>
      </div>
    </div>
  );
};
