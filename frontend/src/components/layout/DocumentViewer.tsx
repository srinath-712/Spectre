import React, { useRef, useEffect, useState } from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { BoundingBoxOverlay } from '../forensic/BoundingBoxOverlay';
import { ScanAnimation } from '../shared/ScanAnimation';
import { ImageIcon } from 'lucide-react';

const BASE_DOCUMENT_WIDTH = 800;
const BASE_DOCUMENT_HEIGHT = 1000;

export const DocumentViewer: React.FC = () => {
  const previewUrl = useForensicStore((state) => state.previewUrl);
  const job = useForensicStore((state) => state.job);
  const result = useForensicStore((state) => state.result);
  const adversarialMode = useForensicStore((state) => state.adversarialMode);

  const frameRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!frameRef.current) return;

    const updateSize = () => {
      if (!frameRef.current) return;
      const rect = frameRef.current.getBoundingClientRect();
      setDimensions({
        width: Math.max(1, Math.round(rect.width)),
        height: Math.max(1, Math.round(rect.height)),
      });
    };

    updateSize();

    const observer = new ResizeObserver(updateSize);
    observer.observe(frameRef.current);

    return () => observer.disconnect();
  }, [previewUrl]);

  const isScanning = job !== null && job.status === 'processing';
  const isPdf = Boolean(job?.filename.toLowerCase().endsWith('.pdf'));

  return (
    <main className="relative flex h-full flex-1 flex-col items-center justify-center overflow-hidden bg-spectre-surface/50 p-3 pb-20 md:p-6 md:pb-20 lg:p-8 lg:pb-20">
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{ backgroundImage: 'radial-gradient(#00F5D4 1px, transparent 1px)', backgroundSize: '30px 30px' }}
      />

      {!previewUrl && (
        <div className="flex flex-col items-center justify-center text-spectre-textMuted opacity-50">
          <ImageIcon size={64} className="mb-4 text-spectre-borderLight" />
          <p className="font-heading tracking-widest text-sm uppercase">No Document Loaded</p>
        </div>
      )}

      {previewUrl && (
        <div
          ref={frameRef}
          className={`relative overflow-hidden rounded-sm bg-white shadow-card transition-all duration-500 ${
            adversarialMode ? 'hue-rotate-[15deg] contrast-125 saturate-50' : ''
          }`}
          style={{ width: 'min(100%, 850px)', aspectRatio: '4 / 5' }}
        >
          {isPdf ? (
            <object data={previewUrl} type="application/pdf" className="h-full w-full">
              <div className="flex h-full w-full items-center justify-center p-6 text-center text-sm text-slate-700">
                PDF preview is not supported in this browser view. Use an image file for overlay validation.
              </div>
            </object>
          ) : (
            <img src={previewUrl} alt="Uploaded preview" className="h-full w-full object-contain" />
          )}

          <ScanAnimation isActive={isScanning} />

          {result && dimensions.width > 0 && dimensions.height > 0 && (
            <div className="animate-fade-in">
              <BoundingBoxOverlay
                width={dimensions.width}
                height={dimensions.height}
                sourceWidth={BASE_DOCUMENT_WIDTH}
                sourceHeight={BASE_DOCUMENT_HEIGHT}
              />
            </div>
          )}
        </div>
      )}
    </main>
  );
};
