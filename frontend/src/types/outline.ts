// 提纲相关类型定义

export interface HotTopicMatch {
  topic_title: string;
  topic_description: string;
  relevance_score: number;
  connection_point: string;
}

export interface EpisodeOutline {
  outline_id: string;
  series_id: string;
  book_id: string;
  episode_number: number;
  theme: string;
  target_chapters: string[];
  target_viewpoints: string[];
  discussion_points: string[];
  hot_topics: HotTopicMatch[];
  flow_design: string;
  estimated_duration: number;
}

export interface BookSeries {
  series_id: string;
  book_id: string;
  persona_id?: string;
  book_title: string;
  author_name: string;
  total_episodes: number;
  total_duration: number;
  completion_status: 'pending' | 'in_progress' | 'completed';
  outlines: EpisodeOutline[];
}
