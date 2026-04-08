import React from 'react';

interface ScanAnimationProps {
  isActive: boolean;
}

export const ScanAnimation: React.FC<ScanAnimationProps> = ({ isActive }) => {
  if (!isActive) return null;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-20 rounded-lg">
      <div className="w-full h-full relative">
        <div className="scan-line" />
        <div className="absolute inset-0 bg-spectre-accent/5 mix-blend-screen" />
      </div>
    </div>
  );
};
