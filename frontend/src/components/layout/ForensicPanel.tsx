import React from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { VerdictBadge } from '../forensic/VerdictBadge';
import { HeatmapThumbnail } from '../forensic/HeatmapThumbnail';
import { FindingCard } from '../forensic/FindingCard';
import { TamperTimeline } from '../forensic/TamperTimeline';
import { DNAFingerprint } from '../forensic/DNAFingerprint';
import { FileSearch } from 'lucide-react';

export const ForensicPanel: React.FC = () => {
  const result = useForensicStore((state) => state.result);
  const selectedFindingId = useForensicStore((state) => state.selectedFindingId);

  if (!result) {
    return (
      <aside className="w-full shrink-0 border-t border-spectre-border bg-spectre-bg p-6 text-center lg:h-full lg:w-[400px] lg:border-l lg:border-t-0">
        <div className="flex h-full min-h-[180px] flex-col items-center justify-center">
        <FileSearch size={48} className="text-spectre-borderLight mb-4" />
        <h3 className="font-heading text-lg font-medium text-spectre-textMuted mb-2">Analysis Pending</h3>
        <p className="text-sm text-spectre-textDim max-w-[250px]">
          Upload a document to view forensic findings, heatmaps, and tamper timeline.
        </p>
        </div>
      </aside>
    );
  }

  // Sort findings to bring selected one to top for better UX
  const sortedFindings = [...result.findings].sort((a, b) => {
    if (a.id === selectedFindingId) return -1;
    if (b.id === selectedFindingId) return 1;
    return b.confidence - a.confidence;
  });

  return (
    <aside className="relative max-h-[44vh] w-full shrink-0 overflow-y-auto border-t border-spectre-border bg-spectre-bg p-4 pb-24 lg:h-full lg:max-h-none lg:w-[400px] lg:border-l lg:border-t-0 lg:p-6">
      <VerdictBadge />
      
      <HeatmapThumbnail />

      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="section-title">Detected Tampers</h4>
          <span className="text-xs font-mono font-bold text-spectre-accent bg-spectre-accent/10 px-2 py-0.5 rounded">
            {result.findings.length} FOUND
          </span>
        </div>
        
        <div className="space-y-3">
          {sortedFindings.map(finding => (
            <FindingCard key={finding.id} finding={finding} />
          ))}
        </div>
      </div>

      <TamperTimeline />
      
      <DNAFingerprint />
    </aside>
  );
};
