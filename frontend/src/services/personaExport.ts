// Persona导出服务
import apiClient from './api';

export const personaExportApi = {
  exportPersona: async (personaId: string) => {
    return apiClient.get(`/personas/${personaId}/export`);
  },
};
