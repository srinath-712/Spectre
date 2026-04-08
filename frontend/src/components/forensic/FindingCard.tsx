import React from 'react';
import type { Finding } from '../../types/forensic';
import { useForensicStore } from '../../store/forensicStore';
import { ConfidenceBar } from '../shared/ConfidenceBar';
import { AlertCircle, FileSearch, Edit3, ImagePlus, Eraser, Layers, Droplets, Maximize, Cpu, Sparkles } from 'lucide-react';

const typeConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  copy_paste: { label: 'Copy & Paste', icon: <Layers size={14} />, color: 'border-spectre-danger text-spectre-danger' },
  overwrite: { label: 'Overwrite', icon: <Edit3 size={14} />, color: 'border-[#F1C40F] text-[#F1C40F]' },
  added_content: { label: 'Added Content', icon: <ImagePlus size={14} />, color: 'border-[#FF8C00] text-[#FF8C00]' },
  erasure: { label: 'Erasure', icon: <Eraser size={14} />, color: 'border-[#3498DB] text-[#3498DB]' },
  merged: { label: 'Merged Document', icon: <FileSearch size={14} />, color: 'border-[#E91E63] text-[#E91E63]' },
  watermark: { label: 'Watermark Removed', icon: <Droplets size={14} />, color: 'border-[#2ECC71] text-[#2ECC71]' },
  spacing: { label: 'Irregular Spacing', icon: <Maximize size={14} />, color: 'border-[#00BCD4] text-[#00BCD4]' },
  ai_generated: { label: 'Fully AI Generated', icon: <Cpu size={14} />, color: 'border-[#9B59B6] text-[#9B59B6]' },
  ai_edit: { label: 'Partial AI Edit', icon: <Sparkles size={14} />, color: 'border-[#FF69B4] text-[#FF69B4]' },
};

interface FindingCardProps {
  finding: Finding;
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding }) => {
  const selectedFindingId = useForensicStore((state) => state.selectedFindingId);
  const setSelectedFindingId = useForensicStore((state) => state.setSelectedFindingId);

  const isActive = selectedFindingId === finding.id;
  const config = typeConfig[finding.type] || { label: finding.type, icon: <AlertCircle size={14} />, color: 'border-spectre-text text-spectre-text' };

  return (
    <div 
      className={`finding-card ${isActive ? 'active' : ''} mb-3`}
      onClick={() => setSelectedFindingId(isActive ? null : finding.id)}
    >
      <div className="flex justify-between items-start mb-2">
        <div className={`spectre-chip ${config.color} bg-opacity-10`}>
          {config.icon}
          {config.label}
        </div>
        <ConfidenceBar confidence={finding.confidence} />
      </div>
      
      <p className="text-sm font-medium text-spectre-text mb-2 line-clamp-2">
        {finding.description}
      </p>

      {isActive && (
        <div className="mt-3 pt-3 border-t border-spectre-borderLight animate-fade-in">
          <span className="text-[10px] uppercase font-bold text-spectre-textMuted tracking-wider mb-1 block">
            Triggering Signals
          </span>
          <ul className="space-y-1">
            {finding.signals.map((signal, idx) => (
              <li key={idx} className="text-xs text-spectre-textDim flex items-start gap-1.5">
                <span className="text-spectre-accent mt-0.5">•</span>
                {signal}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
