// 提纲API服务
import apiClient from './api';
import type { BookSeries, EpisodeOutline } from '../types/outline';

export interface CreateOutlineRequest {
  book_id: string;
  persona_id?: string;
  title?: string;
  description?: string;
}

export interface GenerateOutlineResponse {
  outline_id: string;
  series_id: string;
  status: string;
}

export const outlinesApi = {
  // 获取提纲列表（分页）
  listOutlines: async (skip: number = 0, limit: number = 10) => {
    return apiClient.get<any, { items: BookSeries[]; total: number; skip: number; limit: number }>('/outlines', {
      skip,
      limit,
    });
  },

  // 获取提纲列表（旧方法，保持兼容）
  getOutlines: async () => {
    return apiClient.get<any, { outlines: BookSeries[]; total: number }>('/outlines');
  },

  // 生成提纲（设置更长的超时时间，因为需要调用GPT-4）
  generateOutline: async (data: CreateOutlineRequest) => {
    return apiClient.post<any, GenerateOutlineResponse>('/outlines/generate', data, {
      timeout: 180000, // 3分钟超时
    });
  },

  // 获取提纲详情
  getOutline: async (outlineId: string) => {
    return apiClient.get<any, BookSeries>(`/outlines/${outlineId}`);
  },

  // 删除提纲
  deleteOutline: async (outlineId: string) => {
    return apiClient.delete<any, { deleted_episodes: number }>(`/outlines/${outlineId}`);
  },

  // 更新单集提纲
  updateEpisode: async (outlineId: string, episodeNumber: number, data: Partial<EpisodeOutline>) => {
    return apiClient.put<any, EpisodeOutline>(`/outlines/${outlineId}/episodes/${episodeNumber}`, data);
  },
};
