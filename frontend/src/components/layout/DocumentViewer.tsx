import React, { useRef, useEffect, useState } from 'react';
import { useForensicStore } from '../../store/forensicStore';
import { BoundingBoxOverlay } from '../forensic/BoundingBoxOverlay';
import { ScanAnimation } from '../shared/ScanAnimation';
import { ImageIcon } from 'lucide-react';

export const DocumentViewer: React.FC = () => {
  const previewUrl = useForensicStore((state) => state.previewUrl);
  const job = useForensicStore((state) => state.job);
  const result = useForensicStore((state) => state.result);
  const adversarialMode = useForensicStore((state) => state.adversarialMode);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: 800, // mock base width for bounding boxes
        height: 1000 // mock base height
      });
    }
  }, [previewUrl]);

  const isScanning = job !== null && job.status === 'processing';

  return (
    <main className="flex-1 h-full bg-spectre-surface/50 p-8 flex flex-col items-center justify-center relative overflow-hidden">
      
      {/* Background Grid */}
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
          ref={containerRef}
          className={`relative bg-white rounded-sm shadow-card transition-all duration-500
            ${adversarialMode ? 'hue-rotate-[15deg] contrast-125 saturate-50' : ''}
          `}
          style={{ width: '800px', height: '1000px', transform: 'scale(0.75)', transformOrigin: 'center center' }}
        >
          {/* We use an image element for the mock, in reality this would be pdf.js canvas or image */}
          <div className="absolute inset-0 bg-[#F5F7FA] overflow-hidden">
            {/* Mock document content visualization */}
            <div className="p-12 text-black/80 font-serif">
              <h1 className="text-3xl font-bold mb-8 pb-4 border-b-2 border-black/20">MEDICAL DIAGNOSTIC REPORT</h1>
              
              <div className="grid grid-cols-2 gap-8 mb-12">
                <div>
                  <p className="font-bold mb-1 border-b border-black/10 inline-block">Patient Information</p>
                  <p className="text-sm">Name: <span className="font-mono bg-yellow-100 px-1">JOHN DOE</span></p>
                  <p className="text-sm">ID: 994-22-11A</p>
                  <p className="text-sm">DOB: 12/04/1985</p>
                </div>
                <div>
                  <p className="font-bold mb-1 border-b border-black/10 inline-block">Study Details</p>
                  <p className="text-sm">Date: 04/08/2026</p>
                  <p className="text-sm">Referring: Dr. Smith</p>
                  <p className="text-sm">Ref No: R-773-A</p>
                </div>
              </div>

              <div className="mb-12">
                <p className="font-bold mb-2 border-b border-black/10 inline-block">Clinical Findings</p>
                <p className="text-sm leading-relaxed mb-4">
                  Examination of the thoracic region reveals no significant abnormalities. 
                  Cardiac silhouette is within normal limits. 
                </p>
                <p className="text-sm leading-relaxed">
                  Diagnosis Code: <span className="font-bold text-lg px-2 bg-red-50">C44.9</span>
                </p>
              </div>

              <div className="absolute bottom-12 right-12 text-center">
                <div className="font-signature text-2xl mb-2 text-blue-800 -rotate-3 border border-dashed border-red-400 p-2">Dr. Alan Smith, MD</div>
                <div className="border-2 border-purple-800 text-purple-800 p-2 font-bold uppercase rounded-full rotate-12 inline-block opacity-80 backdrop-blur-sm shadow-lg">
                  APPROVED<br/>
                  <span className="text-[10px]">GENERAL HOSPITAL</span>
                </div>
                <p className="text-xs mt-4">Attending Physician</p>
              </div>
            </div>
          </div>
          
          <img 
            src={previewUrl} 
            alt="Preview" 
            className="absolute inset-0 w-full h-full object-contain opacity-0" // Hidden actual image for now
          />

          <ScanAnimation isActive={isScanning} />
          
          {result && (
            <div className="animate-fade-in">
              <BoundingBoxOverlay width={dimensions.width} height={dimensions.height} />
            </div>
          )}
        </div>
      )}
    </main>
  );
};
