import React, { useEffect, useRef } from 'react';
import { useForensicStore } from '../../store/forensicStore';

const typeColors: Record<string, string> = {
  copy_paste: '#FF4444',
  overwrite: '#F1C40F',
  added_content: '#FF8C00',
  erasure: '#3498DB',
  merged: '#E91E63',
  watermark: '#2ECC71',
  spacing: '#00BCD4',
  ai_generated: '#9B59B6',
  ai_edit: '#FF69B4',
};

interface BoundingBoxOverlayProps {
  width: number;
  height: number;
}

export const BoundingBoxOverlay: React.FC<BoundingBoxOverlayProps> = ({ width, height }) => {
  const result = useForensicStore((state) => state.result);
  const selectedFindingId = useForensicStore((state) => state.selectedFindingId);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!result || !canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    result.findings.forEach((finding) => {
      const color = typeColors[finding.type] || '#FFFFFF';
      const isSelected = selectedFindingId === finding.id;
      
      const { x, y, w, h } = finding.bbox;

      // Draw box
      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 : 2;
      
      if (isSelected) {
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.strokeRect(x, y, w, h);

      // Draw background fill if selected
      if (isSelected) {
        ctx.fillStyle = `${color}33`; // 20% opacity
        ctx.fillRect(x, y, w, h);
      }
      
      // Reset shadow
      ctx.shadowBlur = 0;
    });
  }, [result, selectedFindingId, width, height]);

  if (!result) return null;

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="absolute top-0 left-0 pointer-events-none z-10"
    />
  );
};
