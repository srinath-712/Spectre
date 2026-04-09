import React, { useEffect, useState } from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';

export const TamperTimeline: React.FC = () => {
  const result = useForensicStore((state) => state.result);
  const selectedFindingId = useForensicStore((state) => state.selectedFindingId);
  const setSelectedFindingId = useForensicStore((state) => state.setSelectedFindingId);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (selectedFindingId) {
      setIsExpanded(true);
    }
  }, [selectedFindingId]);

  if (!result || !result.timeline || result.timeline.length === 0) return null;

  const selectedStepId =
    result.timeline.find((step) =>
      selectedFindingId ? step.id.toLowerCase().includes(selectedFindingId.toLowerCase()) : false,
    )?.id ?? null;

  const selectStepFinding = (stepId: string, stepDescription: string): void => {
    const target = result.findings.find((finding) => {
      const fid = (finding.id ?? finding.regionId).toLowerCase();
      return stepId.toLowerCase().includes(fid) || stepDescription.toLowerCase().includes(fid);
    });

    if (target) {
      setSelectedFindingId(target.id ?? target.regionId);
      return;
    }

    const fallback = result.findings[0];
    if (fallback) {
      setSelectedFindingId(fallback.id ?? fallback.regionId);
    }
  };

  return (
    <div className="mt-6 glass-panel overflow-hidden">
      <div 
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-spectre-card/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-spectre-accent" />
          <h4 className="font-heading font-semibold text-sm">Tamper Timeline Inference</h4>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-spectre-accent/90">Laser Sync</span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>
      
      {isExpanded && (
        <div className="p-4 pt-0 border-t border-spectre-border bg-spectre-surface/30">
          <div className="mt-4">
            {result.timeline.map((step) => (
              <button
                key={step.id}
                type="button"
                className={`timeline-step w-full text-left transition-colors ${
                  selectedStepId === step.id ? 'rounded-md bg-spectre-accent/10' : 'hover:bg-spectre-card/50'
                }`}
                onClick={() => selectStepFinding(step.id, step.description)}
              >
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-spectre-accent">Step {step.order}</span>
                  {step.timestampOffset && (
                    <span className="text-[10px] font-mono text-spectre-textMuted bg-spectre-bg px-1 rounded">
                      {step.timestampOffset}
                    </span>
                  )}
                </div>
                <p className="text-xs text-spectre-textDim">{step.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
