import React from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export const VerdictBadge: React.FC = () => {
  const result = useForensicStore((state) => state.result);

  if (!result) return null;

  const { verdict, overallConfidence } = result;
  
  let config = {
    color: 'text-spectre-success',
    bg: 'bg-spectre-success/10',
    border: 'border-spectre-success',
    icon: <ShieldCheck size={28} className="text-spectre-success" />
  };

  if (verdict === 'Suspicious') {
    config = {
      color: 'text-spectre-warning',
      bg: 'bg-spectre-warning/10',
      border: 'border-spectre-warning',
      icon: <AlertTriangle size={28} className="text-spectre-warning" />
    };
  } else if (verdict === 'Tampered') {
    config = {
      color: 'text-spectre-danger',
      bg: 'bg-spectre-danger/10',
      border: 'border-spectre-danger',
      icon: <ShieldAlert size={28} className="text-spectre-danger" />
    };
  }

  return (
    <div className={`flex items-center gap-4 p-4 rounded-xl border ${config.border} ${config.bg} mb-6`}>
      <div className="flex-shrink-0">
        {config.icon}
      </div>
      <div>
        <div className="flex items-baseline gap-2">
          <h3 className={`font-heading font-bold text-xl uppercase tracking-widest ${config.color}`}>
            {verdict}
          </h3>
          <span className="text-xs font-mono text-spectre-textMuted">
            {Math.round(overallConfidence * 100)}% CONFIDENCE
          </span>
        </div>
        <p className="text-xs text-spectre-text mt-1">
          {verdict === 'Tampered' 
            ? 'Forensic analysis indicates clear evidence of document manipulation.' 
            : verdict === 'Suspicious'
            ? 'Anomalies detected. Manual review recommended.'
            : 'No signs of digital tampering detected by the current module suite.'}
        </p>
      </div>
    </div>
  );
};
