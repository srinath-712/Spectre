import React, { useEffect, useRef } from 'react';
import { useForensicStore } from '../../store/forensicStore';

export const HeatmapThumbnail: React.FC = () => {
  const result = useForensicStore((state) => state.result);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!result || !canvasRef.current) return;
    
    // In a real app, this would draw the heatmap provided by the backend URL
    // For mock UI, we will draw a stylized representation using canvas
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const w = canvasRef.current.width;
    const h = canvasRef.current.height;

    // Clear
    ctx.fillStyle = '#131920'; // spectre.card
    ctx.fillRect(0, 0, w, h);

    // Draw document placeholder
    ctx.fillStyle = '#E6EDF3'; // doc color
    ctx.fillRect(20, 10, w - 40, h - 20);

    // Draw mock heatmap blobs based on findings
    result.findings.forEach(finding => {
      // Scale down bbox to thumbnail
      const scale = 0.2; 
      const cx = (finding.bbox.x + finding.bbox.w / 2) * scale;
      const cy = (finding.bbox.y + finding.bbox.h / 2) * scale;
      const radius = Math.max(finding.bbox.w, finding.bbox.h) * scale * 1.5;

      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      
      // Map confidence to color intensity
      const alpha = finding.confidence;
      gradient.addColorStop(0, `rgba(255, 68, 68, ${alpha})`); // Red center
      gradient.addColorStop(0.5, `rgba(255, 140, 0, ${alpha * 0.5})`); // Orange middle
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)'); // Transparent edge

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();
    });

  }, [result]);

  if (!result) return null;

  if (result.heatmapUrl) {
    return (
      <div className="mb-6">
        <h4 className="section-title mb-2">Forensic Heatmap</h4>
        <div className="glass-panel p-2 flex justify-center bg-black/50">
          <img
            src={result.heatmapUrl}
            alt="Forensic heatmap"
            className="rounded border border-spectre-borderLight opacity-90 shadow-glow max-h-[240px] object-contain"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6">
      <h4 className="section-title mb-2">Forensic Heatmap</h4>
      <div className="glass-panel p-2 flex justify-center bg-black/50">
        <canvas 
          ref={canvasRef} 
          width={180} 
          height={240} 
          className="rounded border border-spectre-borderLight opacity-90 shadow-glow"
        />
      </div>
    </div>
  );
};
