import type { AnalysisResult, DocumentDNA } from '../types/forensic';

const API_BASE_URL = 'http://localhost:8000/api';

export const spectreApi = {
  analyze: async (file: File, domain: string): Promise<{ jobId: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);
    
    // const response = await apiClient.post('/analyze', formData);
    // return response.data;
    
    // Stub implementation for UI development phase
    console.log('Sending mock analyze request for', file.name, domain);
    return { jobId: 'mock_job_' + Date.now() };
  },

  getResult: async (jobId: string): Promise<AnalysisResult> => {
    console.log('Fetching mock result from', API_BASE_URL, 'for job', jobId);
    // const response = await apiClient.get(`/result/${jobId}`);
    // return response.data;
    throw new Error('Not implemented. Using Zustand mock store for now.');
  },

  getFingerprint: async (file: File): Promise<DocumentDNA> => {
    console.log('Generating mock fingerprint from', API_BASE_URL, 'for file', file.name);
    // const formData = new FormData();
    // formData.append('file', file);
    // const response = await apiClient.post('/fingerprint', formData);
    // return response.data;
    throw new Error('Not implemented.');
  }
};
