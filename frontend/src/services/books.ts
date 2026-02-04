// 著作相关API
import apiClient from './api';
import type { Book, BookDetail } from '../types/book';

export const booksApi = {
  /**
   * 获取著作列表
   */
  getBooks: async (skip = 0, limit = 10) => {
    return apiClient.get(`/books?skip=${skip}&limit=${limit}`);
  },

  /**
   * 获取著作详情
   */
  getBook: async (bookId: string) => {
    return apiClient.get(`/books/${bookId}`);
  },

  /**
   * 上传并解析著作
   */
  uploadBook: async (file: File, title?: string, author?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (author) formData.append('author', author);

    return apiClient.post('/books/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2分钟超时
    });
  },

  /**
   * 删除著作
   */
  deleteBook: async (bookId: string) => {
    return apiClient.delete(`/books/${bookId}`);
  },
};
