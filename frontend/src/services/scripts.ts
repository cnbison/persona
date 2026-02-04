// 脚本API服务
import apiClient from './api';
import type {
  EpisodeScript,
  ScriptGenerationProgress,
  ScriptSection,
} from '../types/script';

export interface GenerateScriptRequest {
  series_id: string;
  episode_start: number;
  episode_end: number;
}

export interface GenerateScriptResponse {
  script_id: string;
  status: string;
}

export interface ScriptListResponse {
  scripts: EpisodeScript[];
  total: number;
}

export const scriptsApi = {
  // 生成脚本
  generateScript: async (data: GenerateScriptRequest) => {
    return apiClient.post<any, GenerateScriptResponse>('/scripts/generate', data);
  },

  // 获取脚本列表
  getScripts: async () => {
    return apiClient.get<any, ScriptListResponse>('/scripts');
  },

  // 获取脚本详情
  getScript: async (scriptId: string) => {
    return apiClient.get<any, EpisodeScript>(`/scripts/${scriptId}`);
  },

  // 获取生成进度
  getProgress: async (scriptId: string) => {
    return apiClient.get<any, ScriptGenerationProgress>(
      `/scripts/${scriptId}/progress`
    );
  },

  // 导出脚本
  exportScript: async (scriptId: string, format: 'txt' | 'md' | 'json') => {
    return apiClient.get<any, { download_url: string; filename: string }>(
      `/scripts/${scriptId}/export?format=${format}`
    );
  },

  // TODO: 添加删除脚本API
  // deleteScript: async (scriptId: string) => {
  //   return apiClient.delete(`/scripts/${scriptId}`);
  // },
};
