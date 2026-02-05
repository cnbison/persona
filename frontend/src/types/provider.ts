// 模型提供方类型定义

export type ProviderType =
  | 'openai'
  | 'azure'
  | 'anthropic'
  | 'deepseek'
  | 'qwen'
  | 'ollama'
  | 'custom';

export interface ModelProvider {
  provider_id: string;
  name: string;
  provider_type: ProviderType;
  base_url?: string | null;
  api_key?: string | null;
  api_version?: string | null;
  model: string;
  extra_headers?: Record<string, string>;
  is_active: boolean;
  created_at?: string;
}
