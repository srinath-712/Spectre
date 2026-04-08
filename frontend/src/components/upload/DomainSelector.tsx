import React from 'react';
import type { Domain } from '../../types/forensic';
import { useForensicStore } from '../../store/forensicStore';
import { Activity, Landmark, Scale, Fingerprint } from 'lucide-react';

const domainOptions: { id: Domain; label: string; icon: React.ReactNode }[] = [
  { id: 'medical', label: 'Medical', icon: <Activity size={14} /> },
  { id: 'financial', label: 'Financial', icon: <Landmark size={14} /> },
  { id: 'legal', label: 'Legal', icon: <Scale size={14} /> },
  { id: 'id', label: 'ID Cards', icon: <Fingerprint size={14} /> },
];

export const DomainSelector: React.FC = () => {
  const selectedDomain = useForensicStore((state) => state.selectedDomain);
  const setSelectedDomain = useForensicStore((state) => state.setSelectedDomain);
  const job = useForensicStore((state) => state.job);

  const disabled = job !== null && job.status !== 'error';

  return (
    <div className="mt-6">
      <h4 className="section-title mb-3">Analysis Domain</h4>
      <div className="grid grid-cols-2 gap-2">
        {domainOptions.map((opt) => {
          const isSelected = selectedDomain === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => setSelectedDomain(opt.id)}
              disabled={disabled}
              className={`flex items-center gap-2 p-2 rounded-lg text-sm transition-all duration-200
                ${isSelected 
                  ? 'bg-spectre-accent/20 border border-spectre-accent text-spectre-accent shadow-glow' 
                  : 'bg-spectre-surface border border-spectre-border text-spectre-textMuted hover:bg-spectre-borderLight'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed hidden-pointer-events' : ''}
              `}
            >
              <div className={isSelected ? 'text-spectre-accent' : 'text-spectre-textDim'}>
                {opt.icon}
              </div>
              <span className="font-medium">{opt.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
