import axios from 'axios';
import type { AnalysisResult, DocumentDNA, Domain, Finding, TimelineStep } from '../types/forensic';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

type ApiFinding = {
  region_id: string;
  bbox: { x: number; y: number; w: number; h: number };
  type: Finding['type'];
  confidence: number;
  signals: string[];
  severity: Finding['severity'];
  description: string;
};

type ApiResultResponse = {
  status: 'uploading' | 'processing' | 'completed' | 'error';
  findings: ApiFinding[];
  heatmap_url?: string | null;
  verdict?: AnalysisResult['verdict'] | null;
  overall_confidence?: number | null;
  timeline?: Array<{ id: string; order: number; description: string; timestamp_offset?: string | null }>;
  dna?: { dna_id: string; hash: string; scanner_profile: string; matched_known: boolean } | null;
};

const mapFinding = (finding: ApiFinding): Finding => ({
  id: finding.region_id,
  regionId: finding.region_id,
  bbox: finding.bbox,
  type: finding.type,
  confidence: finding.confidence,
  signals: finding.signals,
  severity: finding.severity,
  description: finding.description,
});

const mapTimeline = (
  timeline: ApiResultResponse['timeline'] | undefined,
): TimelineStep[] => (timeline ?? []).map((step) => ({
  id: step.id,
  order: step.order,
  description: step.description,
  timestampOffset: step.timestamp_offset ?? undefined,
}));

const mapDna = (dna: ApiResultResponse['dna']): DocumentDNA => ({
  id: dna?.dna_id ?? 'DNA-UNKNOWN',
  hash: dna?.hash ?? '',
  scannerProfile: dna?.scanner_profile ?? 'unknown',
  matchedKnown: dna?.matched_known ?? false,
});

export const spectreApi = {
  analyze: async (file: File, domain: Domain): Promise<{ jobId: string; status: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);

    const response = await apiClient.post<{ job_id: string; status: string }>('/analyze', formData);
    return {
      jobId: response.data.job_id,
      status: response.data.status,
    };
  },

  getResult: async (jobId: string): Promise<ApiResultResponse> => {
    const response = await apiClient.get<ApiResultResponse>(`/result/${jobId}`);
    return response.data;
  },

  getMappedResult: async (jobId: string): Promise<AnalysisResult | null> => {
    const raw = await spectreApi.getResult(jobId);
    if (raw.status !== 'completed') {
      return null;
    }

    return {
      jobId,
      findings: raw.findings.map(mapFinding),
      heatmapUrl: raw.heatmap_url ?? undefined,
      verdict: raw.verdict ?? 'Suspicious',
      overallConfidence: raw.overall_confidence ?? 0.5,
      timeline: mapTimeline(raw.timeline),
      dna: mapDna(raw.dna),
    };
  },

  runAdversarial: async (
    jobId: string,
    attackType: 'jpeg_recompress' | 'gaussian_noise' | 'geometric_warp' | 'downsample_upsample' | 'color_jitter',
  ): Promise<Finding[]> => {
    const response = await apiClient.post<{ findings_after_attack: ApiFinding[] }>('/adversarial', {
      job_id: jobId,
      attack_type: attackType,
    });
    return response.data.findings_after_attack.map(mapFinding);
  },

  getFingerprint: async (file: File): Promise<{ dnaId: string; hash: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ dna_id: string; hash: string }>('/fingerprint', formData);
    return {
      dnaId: response.data.dna_id,
      hash: response.data.hash,
    };
  },

  reportUrl: (jobId: string): string => `${API_BASE_URL}/report/${jobId}`,
};
