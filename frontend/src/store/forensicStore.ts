import { create } from 'zustand';
import { spectreApi } from '../api/spectreApi';
import type { AnalysisResult, AnalysisJob, Domain, Finding } from '../types/forensic';

interface ForensicState {
  job: AnalysisJob | null;
  setJob: (job: AnalysisJob | null) => void;
  updateJobProgress: (progress: number, status?: AnalysisJob['status']) => void;
  resetAnalysis: () => void;

  selectedDomain: Domain;
  setSelectedDomain: (domain: Domain) => void;

  result: AnalysisResult | null;
  setResult: (result: AnalysisResult | null) => void;

  selectedFindingId: string | null;
  setSelectedFindingId: (id: string | null) => void;
  adversarialMode: boolean;
  setAdversarialMode: (enabled: boolean) => Promise<void>;

  previewUrl: string | null;
  setPreviewUrl: (url: string | null) => void;

  analyzeFile: (file: File) => Promise<void>;
  exportReport: () => void;
}

const pollIntervalMs = 900;
const maxPollAttempts = 60;

export const useForensicStore = create<ForensicState>((set, get) => ({
  job: null,
  setJob: (job) => set({ job }),

  updateJobProgress: (progress, status) =>
    set((state) => ({
      job: state.job
        ? {
            ...state.job,
            progress,
            status: status !== undefined ? status : state.job.status,
          }
        : null,
    })),

  resetAnalysis: () => {
    get().setPreviewUrl(null);
    set({
      job: null,
      result: null,
      selectedFindingId: null,
      adversarialMode: false,
    });
  },

  selectedDomain: 'medical',
  setSelectedDomain: (domain) => set({ selectedDomain: domain }),

  result: null,
  setResult: (result) => set({ result }),

  selectedFindingId: null,
  setSelectedFindingId: (id) => set({ selectedFindingId: id }),

  adversarialMode: false,
  setAdversarialMode: async (enabled) => {
    set({ adversarialMode: enabled });

    const { job, result } = get();
    if (!enabled || !job || job.status !== 'completed' || !result) {
      return;
    }

    try {
      const attackedFindings = await spectreApi.runAdversarial(job.id, 'gaussian_noise');
      set((state) =>
        state.result
          ? {
              result: {
                ...state.result,
                findings: attackedFindings as Finding[],
              },
            }
          : {}
      );
    } catch (error) {
      console.error('Adversarial run failed', error);
    }
  },

  previewUrl: null,
  setPreviewUrl: (url) => {
    const previousUrl = get().previewUrl;
    if (previousUrl && previousUrl !== url) {
      window.URL.revokeObjectURL(previousUrl);
    }
    set({ previewUrl: url });
  },

  analyzeFile: async (file) => {
    const isSupported = file.type === 'application/pdf' || file.type.startsWith('image/');
    if (!isSupported) {
      set({
        result: null,
        selectedFindingId: null,
        job: {
          id: 'job_' + Date.now(),
          status: 'error',
          filename: file.name,
          domain: get().selectedDomain,
          progress: 0,
          startTime: new Date(),
          endTime: new Date(),
        },
      });
      return;
    }

    const previousUrl = get().previewUrl;
    if (previousUrl) {
      window.URL.revokeObjectURL(previousUrl);
    }

    const previewUrl = window.URL.createObjectURL(file);
    set({
      previewUrl,
      result: null,
      selectedFindingId: null,
      adversarialMode: false,
      job: {
        id: 'pending_' + Date.now(),
        status: 'uploading',
        filename: file.name,
        domain: get().selectedDomain,
        progress: 5,
        startTime: new Date(),
      },
    });

    try {
      const analyzeResp = await spectreApi.analyze(file, get().selectedDomain);
      set((state) => ({
        job: state.job
          ? {
              ...state.job,
              id: analyzeResp.jobId,
              status: 'processing',
              progress: 20,
            }
          : null,
      }));

      let attempt = 0;
      let completed = false;
      while (attempt < maxPollAttempts && !completed) {
        attempt += 1;
        const progress = Math.min(95, 20 + Math.floor((attempt / maxPollAttempts) * 70));
        set((state) => ({
          job: state.job
            ? {
                ...state.job,
                status: 'processing',
                progress,
              }
            : null,
        }));

        const mapped = await spectreApi.getMappedResult(analyzeResp.jobId);
        if (mapped) {
          set((state) => ({
            result: mapped,
            job: state.job
              ? {
                  ...state.job,
                  status: 'completed',
                  progress: 100,
                  endTime: new Date(),
                }
              : null,
          }));
          completed = true;
          break;
        }

        await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
      }

      if (!completed) {
        set((state) => ({
          job: state.job
            ? {
                ...state.job,
                status: 'error',
                endTime: new Date(),
              }
            : null,
        }));
      }
    } catch (error) {
      console.error('Analyze failed', error);
      set((state) => ({
        job: state.job
          ? {
              ...state.job,
              status: 'error',
              endTime: new Date(),
            }
          : null,
      }));
    }
  },

  exportReport: () => {
    const job = get().job;
    if (!job || job.status !== 'completed') {
      return;
    }
    const url = spectreApi.reportUrl(job.id);
    window.open(url, '_blank', 'noopener,noreferrer');
  },
}));
