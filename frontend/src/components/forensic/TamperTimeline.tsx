import React, { useState } from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';

export const TamperTimeline: React.FC = () => {
  const result = useForensicStore((state) => state.result);
  const [isExpanded, setIsExpanded] = useState(false);

  if (!result || !result.timeline || result.timeline.length === 0) return null;

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
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>
      
      {isExpanded && (
        <div className="p-4 pt-0 border-t border-spectre-border bg-spectre-surface/30">
          <div className="mt-4">
            {result.timeline.map((step) => (
              <div key={step.id} className="timeline-step">
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-spectre-accent">Step {step.order}</span>
                  {step.timestampOffset && (
                    <span className="text-[10px] font-mono text-spectre-textMuted bg-spectre-bg px-1 rounded">
                      {step.timestampOffset}
                    </span>
                  )}
                </div>
                <p className="text-xs text-spectre-textDim">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
