import React from 'react';
import { DropZone } from '../upload/DropZone';
import { DomainSelector } from '../upload/DomainSelector';
import { Fingerprint, ScanEye, RotateCw } from 'lucide-react';
import { useForensicStore } from '../../store/forensicStore';

export const Sidebar: React.FC = () => {
  const simulateAnalysis = useForensicStore((state) => state.simulateAnalysis);
  
  // Create a fake file for demo re-analysis
  const handleReanalyze = () => {
    const fakeFile = new File([''], 'demo_document.pdf', { type: 'application/pdf' });
    simulateAnalysis(fakeFile);
  };

  return (
    <aside className="w-full shrink-0 border-b border-spectre-border bg-spectre-bg p-4 pt-5 lg:h-full lg:w-80 lg:border-b-0 lg:border-r lg:p-6 lg:pt-8">
      <div className="mb-6 flex items-center gap-3 lg:mb-10">
        <ScanEye size={32} className="text-spectre-accent animate-pulse-glow" />
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide glow-text">SPECTRE</h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-spectre-textMuted">Forensic Intelligence</p>
        </div>
      </div>

      <div className="max-h-[34vh] overflow-y-auto pr-1 lg:max-h-none lg:pr-2">
        <DropZone />
        <DomainSelector />

        {/* History Mock */}
        <div className="mt-10">
          <h4 className="section-title mb-4 flex items-center justify-between">
            Recent Analyses
            <Fingerprint size={14} className="text-spectre-textDim" />
          </h4>
          
          <div className="space-y-2">
            {[
              { id: 'MDC-9921', status: 'Tampered', time: '10 min ago', color: 'text-spectre-danger' },
              { id: 'LGL-4412', status: 'Authentic', time: '1 hour ago', color: 'text-spectre-success' },
              { id: 'FIN-0883', status: 'Suspicious', time: '2 hours ago', color: 'text-spectre-warning' }
            ].map((item) => (
              <div key={item.id} className="p-3 rounded-lg border border-spectre-border bg-spectre-surface flex items-center justify-between group">
                <div>
                  <span className="text-xs font-mono text-spectre-text block">{item.id}</span>
                  <div className="flex gap-2">
                    <span className={`text-[10px] uppercase font-bold ${item.color}`}>{item.status}</span>
                    <span className="text-[10px] text-spectre-textDim">{item.time}</span>
                  </div>
                </div>
                <button 
                  onClick={handleReanalyze}
                  className="p-1.5 rounded-md hover:bg-spectre-borderLight text-spectre-textMuted hover:text-spectre-accent transition-colors opacity-0 group-hover:opacity-100"
                  title="Re-analyze"
                >
                  <RotateCw size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
};
