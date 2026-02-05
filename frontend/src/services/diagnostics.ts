// 诊断指标 API服务
import apiClient from './api';

export const diagnosticsApi = {
  getReport: async (reportId: string) => {
    return apiClient.get(`/diagnostics/${reportId}`);
  },
};
