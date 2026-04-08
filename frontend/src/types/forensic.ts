export type TamperingType =
  | 'copy_paste'
  | 'overwrite'
  | 'added_content'
  | 'erasure'
  | 'merged'
  | 'watermark'
  | 'spacing'
  | 'ai_generated'
  | 'ai_edit';

export type Domain = 'medical' | 'financial' | 'legal' | 'id';

export type BoundingBox = {
  x: number;
  y: number;
  w: number;
  h: number;
};

export type Finding = {
  id: string;
  bbox: BoundingBox;
  type: TamperingType;
  confidence: number;
  signals: string[];
  severity: 'high' | 'medium' | 'low';
  description: string;
};

export type TimelineStep = {
  id: string;
  order: number;
  description: string;
  timestampOffset?: string; // e.g., "T+0s", "T+4m"
};

export type DocumentDNA = {
  id: string;
  hash: string;
  scannerProfile: string;
  matchedKnown: boolean;
};

export type AnalysisJob = {
  id: string;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  filename: string;
  domain: Domain;
  progress: number; // 0-100
  startTime?: Date;
  endTime?: Date;
};

export type AnalysisResult = {
  jobId: string;
  findings: Finding[];
  heatmapUrl?: string; // Data URL for the heatmap overlay
  timeline: TimelineStep[];
  dna: DocumentDNA;
  verdict: 'Authentic' | 'Suspicious' | 'Tampered';
  overallConfidence: number;
};
