// Diff API服务
import apiClient from './api';

export interface DiffByTextRequest {
  a_text: string;
  b_text: string;
}

export interface DiffByArtifactRequest {
  a_artifact_id: string;
  b_artifact_id: string;
  a_stage?: 'canonical' | 'plan' | 'final';
  b_stage?: 'canonical' | 'plan' | 'final';
}

export interface DiffResult {
  opcodes: Array<{
    tag: 'equal' | 'replace' | 'delete' | 'insert';
    a_start: number;
    a_end: number;
    b_start: number;
    b_end: number;
  }>;
  a_len: number;
  b_len: number;
}

export const diffApi = {
  diffByText: async (payload: DiffByTextRequest) => {
    return apiClient.post('/diff/text', payload);
  },
  diffByArtifacts: async (payload: DiffByArtifactRequest) => {
    return apiClient.post('/diff/artifacts', payload);
  },
};
