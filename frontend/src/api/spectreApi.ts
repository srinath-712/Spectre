import axios from 'axios';
import type { AnalysisJob, AnalysisResult, DocumentDNA } from '../types/forensic';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

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
    // const response = await apiClient.get(`/result/${jobId}`);
    // return response.data;
    throw new Error('Not implemented. Using Zustand mock store for now.');
  },

  getFingerprint: async (file: File): Promise<DocumentDNA> => {
    // const formData = new FormData();
    // formData.append('file', file);
    // const response = await apiClient.post('/fingerprint', formData);
    // return response.data;
    throw new Error('Not implemented.');
  }
};
