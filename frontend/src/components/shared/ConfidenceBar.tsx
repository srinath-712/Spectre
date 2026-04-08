import React from 'react';

interface ConfidenceBarProps {
  confidence: number; // 0.0 to 1.0
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ confidence }) => {
  const percentage = Math.round(confidence * 100);
  
  let colorClass = 'bg-spectre-success';
  if (percentage < 70) colorClass = 'bg-spectre-warning';
  if (percentage < 40) colorClass = 'bg-spectre-danger';

  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-spectre-borderLight rounded-full overflow-hidden">
        <div 
          className={`h-full ${colorClass} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs font-mono text-spectre-textMuted w-8">{percentage}%</span>
    </div>
  );
};
