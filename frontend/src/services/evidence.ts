// 证据库 API服务
import apiClient from './api';

export const evidenceApi = {
  buildEvidence: async (bookId: string) => {
    return apiClient.post(`/evidence/build/${bookId}`);
  },
  searchEvidence: async (params: { keyword?: string; book_id?: string; chapter_id?: string; viewpoint_id?: string }) => {
    const query = new URLSearchParams();
    if (params.keyword) query.set('keyword', params.keyword);
    if (params.book_id) query.set('book_id', params.book_id);
    if (params.chapter_id) query.set('chapter_id', params.chapter_id);
    if (params.viewpoint_id) query.set('viewpoint_id', params.viewpoint_id);
    return apiClient.get(`/evidence/search?${query.toString()}`);
  },
  listParagraphs: async (chapterId: string) => {
    return apiClient.get(`/evidence/paragraphs?chapter_id=${chapterId}`);
  },
};
