// Persona API服务
import apiClient from './api';
import type { AuthorPersona, PersonaCardSummary, PersonaDiffResult } from '../types/persona';

export interface CreatePersonaRequest {
  book_id: string;
}

export interface CreatePersonaResponse {
  persona_id: string;
  book_id: string;
  author_name: string;
  status: string;
}

export interface GeneratePromptResponse {
  system_prompt: string;
}

export interface ImportPersonaResponse {
  persona_id: string;
  version: string;
}

export interface CreatePersonaVersionResponse {
  persona_id: string;
  version: string;
}

export interface ListPersonasResponse {
  items: AuthorPersona[];
  total: number;
  skip: number;
  limit: number;
}

export const personasApi = {
  // 创建Persona（设置更长的超时时间，因为需要调用GPT-4）
  createPersona: async (bookId: string) => {
    return apiClient.post<any, CreatePersonaResponse>('/personas', {
      book_id: bookId,
    }, {
      timeout: 180000, // 3分钟超时
    });
  },

  // 获取Persona详情
  getPersona: async (personaId: string) => {
    return apiClient.get<any, AuthorPersona>(`/personas/${personaId}`);
  },

  // 生成System Prompt
  generateSystemPrompt: async (personaId: string, force: boolean = false) => {
    const query = force ? '?force=true' : '';
    return apiClient.post<any, GeneratePromptResponse>(
      `/personas/${personaId}/generate-prompt${query}`
    );
  },

  // 获取Persona列表
  listPersonas: async (skip: number = 0, limit: number = 100) => {
    return apiClient.get<any, ListPersonasResponse>('/personas', {
      skip,
      limit,
    });
  },

  getPersonaCard: async (personaId: string) => {
    return apiClient.get<any, PersonaCardSummary>(`/personas/${personaId}/card`);
  },

  diffPersonas: async (sourceId: string, targetId: string) => {
    return apiClient.post<any, PersonaDiffResult>('/personas/diff', {
      source_id: sourceId,
      target_id: targetId,
    });
  },

  importPersona: async (payload: Record<string, any>, mode: 'new' | 'new_version' | 'overwrite' = 'new_version') => {
    return apiClient.post<any, ImportPersonaResponse>('/personas/import', {
      mode,
      persona: payload,
    });
  },

  createPersonaVersion: async (personaId: string, version?: string) => {
    return apiClient.post<any, CreatePersonaVersionResponse>(`/personas/${personaId}/versions`, {
      version,
    });
  },
};
