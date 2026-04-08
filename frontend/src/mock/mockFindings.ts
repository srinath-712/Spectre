import type { AnalysisResult, Finding, TimelineStep } from '../types/forensic';

// Sample findings for a tampered medical record
const medicalFindings: Finding[] = [
  {
    id: 'f_001',
    bbox: { x: 350, y: 150, w: 200, h: 40 },
    type: 'ai_edit',
    confidence: 0.98,
    severity: 'high',
    signals: [
      'Local ELA compression mismatch',
      'Inter-character kerning deviation (sub-pixel level)'
    ],
    description: 'Patient name appears to be fully replaced using an AI generation model.'
  },
  {
    id: 'f_002',
    bbox: { x: 420, y: 550, w: 120, h: 30 },
    type: 'overwrite',
    confidence: 0.91,
    severity: 'high',
    signals: [
      'Double ink density anomaly detected',
      'Stroke texture analysis indicates broken background grain'
    ],
    description: 'Diagnosis code overwritten on top of erased existing text.'
  },
  {
    id: 'f_003',
    bbox: { x: 100, y: 800, w: 250, h: 80 },
    type: 'copy_paste',
    confidence: 0.95,
    severity: 'high',
    signals: [
      'SIFT keypoint match found elsewhere on document',
      'DCT coefficient block duplication'
    ],
    description: "Doctor's signature block copied from an external or previous document."
  },
  {
    id: 'f_004',
    bbox: { x: 600, y: 800, w: 150, h: 150 },
    type: 'added_content',
    confidence: 0.88,
    severity: 'medium',
    signals: [
      'Edge artifact detection (Laplacian of Gaussian)',
      'Resolution mismatch with native DPI'
    ],
    description: 'Hospital stamp added later; lacks natural scanning noise profile.'
  }
];

const medicalTimeline: TimelineStep[] = [
  {
    id: 't_001',
    order: 1,
    description: 'Original document created and scanned. Baseline noise profile established.',
    timestampOffset: 'T+0s'
  },
  {
    id: 't_002',
    order: 2,
    description: 'Original diagnosis code erased (low local variance detected in target region).',
    timestampOffset: 'T+?'
  },
  {
    id: 't_003',
    order: 3,
    description: 'Diagnosis overwritten with new darker ink (ink density anomaly found on top of smoothed area).',
    timestampOffset: 'T+?'
  },
  {
    id: 't_004',
    order: 4,
    description: 'AI model used to replace Patient Name (compression mismatch overlays earlier edits).',
    timestampOffset: 'T+?'
  },
  {
    id: 't_005',
    order: 5,
    description: 'Signature and stamp copy-pasted onto resulting document image before final JPEG re-compression.',
    timestampOffset: 'T+?'
  }
];

export const mockMedicalResult: AnalysisResult = {
  jobId: 'job_test_001',
  verdict: 'Tampered',
  overallConfidence: 0.96,
  findings: medicalFindings,
  timeline: medicalTimeline,
  dna: {
    id: 'DNA-MDC-9921',
    hash: '8f4c2e119b3d0a77',
    scannerProfile: 'Epson WorkForce Pro / Generic Halftone',
    matchedKnown: false
  }
};
