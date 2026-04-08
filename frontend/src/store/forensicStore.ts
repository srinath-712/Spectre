import { create } from 'zustand';
import type { AnalysisResult, AnalysisJob, Domain } from '../types/forensic';
import { mockMedicalResult } from '../mock/mockFindings';

interface ForensicState {
  // Current job
  job: AnalysisJob | null;
  setJob: (job: AnalysisJob | null) => void;
  updateJobProgress: (progress: number, status?: AnalysisJob['status']) => void;

  // Selected domain
  selectedDomain: Domain;
  setSelectedDomain: (domain: Domain) => void;

  // Analysis Result
  result: AnalysisResult | null;
  setResult: (result: AnalysisResult | null) => void;

  // UI State
  selectedFindingId: string | null;
  setSelectedFindingId: (id: string | null) => void;
  adversarialMode: boolean;
  setAdversarialMode: (enabled: boolean) => void;

  // Mock Action (simulating file upload)
  simulateAnalysis: (file: File) => void;
  
  // App wide
  previewUrl: string | null;
  setPreviewUrl: (url: string | null) => void;
}

export const useForensicStore = create<ForensicState>((set) => ({
  job: null,
  setJob: (job) => set({ job }),
  
  updateJobProgress: (progress, status) => set((state) => ({
    job: state.job ? { 
      ...state.job, 
      progress, 
      status: status !== undefined ? status : state.job.status 
    } : null
  })),

  selectedDomain: 'medical',
  setSelectedDomain: (domain) => set({ selectedDomain: domain }),

  result: null,
  setResult: (result) => set({ result }),

  selectedFindingId: null,
  setSelectedFindingId: (id) => set({ selectedFindingId: id }),

  adversarialMode: false,
  setAdversarialMode: (enabled) => set({ adversarialMode: enabled }),

  previewUrl: null,
  setPreviewUrl: (url) => {
    const previousUrl = useForensicStore.getState().previewUrl;
    if (previousUrl && previousUrl !== url) {
      window.URL.revokeObjectURL(previousUrl);
    }
    set({ previewUrl: url });
  },

  simulateAnalysis: (file) => {
    const isSupported = file.type === 'application/pdf' || file.type.startsWith('image/');
    if (!isSupported) {
      set({
        result: null,
        selectedFindingId: null,
        job: {
          id: 'job_' + Date.now(),
          status: 'error',
          filename: file.name,
          domain: useForensicStore.getState().selectedDomain,
          progress: 0,
          startTime: new Date(),
          endTime: new Date(),
        },
      });
      return;
    }

    // Determine a fake job ID
    const jobId = 'job_' + Date.now();
    
    const previousUrl = useForensicStore.getState().previewUrl;
    if (previousUrl) {
      window.URL.revokeObjectURL(previousUrl);
    }

    // Create local object URL for preview
    const previewUrl = window.URL.createObjectURL(file);
    set({ previewUrl });
    
    set({
      result: null,
      selectedFindingId: null,
      job: {
        id: jobId,
        status: 'uploading',
        filename: file.name,
        domain: useForensicStore.getState().selectedDomain,
        progress: 0,
        startTime: new Date()
      }
    });

    // Simulate upload
    setTimeout(() => {
      set((state) => ({
        job: state.job ? { ...state.job, status: 'processing', progress: 20 } : null
      }));

      // Simulate processing ticks
      let progress = 20;
      const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 15) + 5;
        if (progress >= 100) {
          clearInterval(interval);
          set((state) => ({
            job: state.job ? { ...state.job, status: 'completed', progress: 100, endTime: new Date() } : null,
            result: mockMedicalResult // Populate mock findings
          }));
        } else {
          set((state) => ({
            job: state.job ? { ...state.job, progress } : null
          }));
        }
      }, 500);

    }, 1000);
  }
}));
