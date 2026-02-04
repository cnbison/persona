// 脚本相关类型定义

export interface DialogueLine {
  speaker: 'author' | 'host';
  content: string;
  duration_minutes: number;
  original_text_reference?: string;
  hot_topic_reference?: string;
}

export interface ScriptSection {
  section_type: 'opening' | 'book_discussion' | 'hot_topic' | 'deep_dive' | 'closing';
  title: string;
  duration_minutes: number;
  dialogues: DialogueLine[];
}

export interface EpisodeScript {
  script_id: string;
  outline_id: string;
  series_id: string;
  episode_number: number;
  sections: ScriptSection[];
  total_duration_minutes: number;
  total_word_count: number;
  author_speaking_ratio: number;
  host_speaking_ratio: number;
  generation_status: 'pending' | 'generating' | 'completed' | 'failed';
}

export interface ScriptGenerationProgress {
  script_id: string;
  status: 'generating' | 'completed' | 'failed';
  current_section?: string;
  progress_percentage: number;
  current_step: string;
  extra_data?: {
    generated_script_ids?: string[];
  };
}
