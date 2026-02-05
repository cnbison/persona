// 受众Persona API服务
import apiClient from './api';
import type { AudiencePersona } from '../types/audience';

export interface CreateAudienceRequest {
  label: string;
  book_id?: string | null;
  education_stage: string;
  prior_knowledge: string;
  cognitive_preference: string;
  language_preference: string;
  tone_preference: string;
  term_density?: number;
  sentence_length?: number;
  abstraction_level?: number;
  example_complexity?: number;
  proof_depth?: number;
  constraints?: string[];
}

export interface UpdateAudienceRequest {
  label?: string;
  book_id?: string | null;
  education_stage?: string;
  prior_knowledge?: string;
  cognitive_preference?: string;
  language_preference?: string;
  tone_preference?: string;
  term_density?: number;
  sentence_length?: number;
  abstraction_level?: number;
  example_complexity?: number;
  proof_depth?: number;
  constraints?: string[];
}

export interface ListAudiencesResponse {
  audiences: AudiencePersona[];
  total: number;
}

export const audiencesApi = {
  createAudience: async (payload: CreateAudienceRequest) => {
    return apiClient.post('/audiences', payload);
  },

  listAudiences: async (skip = 0, limit = 100, bookId?: string) => {
    const params = new URLSearchParams();
    params.set('skip', String(skip));
    params.set('limit', String(limit));
    if (bookId) params.set('book_id', bookId);

    return apiClient.get(`/audiences?${params.toString()}`);
  },

  getAudience: async (audienceId: string) => {
    return apiClient.get(`/audiences/${audienceId}`);
  },

  getAudienceConstraints: async (audienceId: string) => {
    return apiClient.get(`/audiences/${audienceId}/constraints`);
  },

  updateAudience: async (audienceId: string, payload: UpdateAudienceRequest) => {
    return apiClient.patch(`/audiences/${audienceId}`, payload);
  },

  deleteAudience: async (audienceId: string) => {
    return apiClient.delete(`/audiences/${audienceId}`);
  },
};
