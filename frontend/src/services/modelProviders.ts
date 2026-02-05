// 模型提供方 API服务
import apiClient from './api';
import type { ProviderType } from '../types/provider';

export interface ModelProviderRequest {
  name: string;
  provider_type: ProviderType;
  base_url?: string;
  api_key?: string;
  api_version?: string;
  model: string;
  extra_headers?: Record<string, string>;
  is_active?: boolean;
}

export const modelProvidersApi = {
  listProviders: async () => {
    return apiClient.get('/model-providers');
  },
  createProvider: async (payload: ModelProviderRequest) => {
    return apiClient.post('/model-providers', payload);
  },
  updateProvider: async (providerId: string, payload: Partial<ModelProviderRequest>) => {
    return apiClient.patch(`/model-providers/${providerId}`, payload);
  },
  deleteProvider: async (providerId: string) => {
    return apiClient.delete(`/model-providers/${providerId}`);
  },
  getActive: async () => {
    return apiClient.get('/model-providers/active');
  },
};
