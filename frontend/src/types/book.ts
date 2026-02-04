// 著作相关类型定义

export interface Book {
  book_id: string;
  title: string;
  author: string;
  language: string;
  file_type: string;
  total_words?: number;  // 可选字段，后端可能不返回
  total_chapters: number;
  total_viewpoints: number;
  created_at: string;
}

export interface Chapter {
  chapter_id: string;
  book_id: string;
  chapter_number: number;
  title: string;
  content: string;
  word_count: number;
}

export interface CoreViewpoint {
  viewpoint_id: string;
  book_id: string;
  content: string;
  keywords: string[];
  related_chapter: string;
}

export interface BookDetail extends Book {
  chapters: Chapter[];
  viewpoints: CoreViewpoint[];
}
