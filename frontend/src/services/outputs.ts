// 输出内容与诊断 API服务
import apiClient from './api';
import type { OutputArtifact, DiagnosticReport } from '../types/output';

export interface CreateOutputRequest {
  book_id: string;
  speaker_persona_id?: string | null;
  audience_persona_id?: string | null;
  task_type: string;
  title?: string;
  locked_facts?: string[];
  stage_outputs?: Record<string, string>;
  final_text?: string;
  content_format?: string;
  metrics?: Record<string, number>;
}

export interface GenerateOutputRequest {
  book_id: string;
  source_text: string;
  task_type: string;
  title?: string;
  content_format?: string;
  speaker_persona_id?: string | null;
  audience_persona_id?: string | null;
  locked_facts?: string[];
  create_report?: boolean;
}

export interface CreateDiagnosticRequest {
  speaker_persona_id?: string | null;
  audience_persona_id?: string | null;
  metrics?: Record<string, number>;
  issues?: string[];
  suggestions?: string;
}

export const outputsApi = {
  createOutput: async (payload: CreateOutputRequest) => {
    return apiClient.post('/outputs', payload);
  },

  generateOutput: async (payload: GenerateOutputRequest) => {
    return apiClient.post('/outputs/generate', payload, {
      timeout: 180000,
    });
  },

  listOutputs: async (
    skip = 0,
    limit = 50,
    filters?: {
      book_id?: string;
      speaker_persona_id?: string;
      audience_persona_id?: string;
      task_type?: string;
    }
  ) => {
    const params = new URLSearchParams();
    params.set('skip', String(skip));
    params.set('limit', String(limit));
    if (filters?.book_id) params.set('book_id', filters.book_id);
    if (filters?.speaker_persona_id) params.set('speaker_persona_id', filters.speaker_persona_id);
    if (filters?.audience_persona_id) params.set('audience_persona_id', filters.audience_persona_id);
    if (filters?.task_type) params.set('task_type', filters.task_type);

    return apiClient.get(`/outputs?${params.toString()}`);
  },

  getOutput: async (artifactId: string) => {
    return apiClient.get(`/outputs/${artifactId}`);
  },

  deleteOutput: async (artifactId: string) => {
    return apiClient.delete(`/outputs/${artifactId}`);
  },

  createDiagnostic: async (artifactId: string, payload: CreateDiagnosticRequest) => {
    return apiClient.post(`/outputs/${artifactId}/diagnostics`, payload);
  },

  listDiagnostics: async (artifactId: string) => {
    return apiClient.get(`/outputs/${artifactId}/diagnostics`);
  },

  getDiagnostic: async (reportId: string) => {
    return apiClient.get(`/outputs/diagnostics/${reportId}`);
  },
};
