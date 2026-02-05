// 受众Persona类型定义

export interface AudiencePersona {
  audience_id: string;
  label: string;
  book_id?: string | null;

  education_stage: string;
  prior_knowledge: string;
  cognitive_preference: string;
  language_preference: string;
  tone_preference: string;

  term_density: number;
  sentence_length: number;
  abstraction_level: number;
  example_complexity: number;
  proof_depth: number;

  constraints: string[];
  created_at?: string;
}

export interface AudienceConstraints {
  education_stage: string;
  prior_knowledge: string;
  cognitive_preference: string;
  language_preference: string;
  tone_preference: string;
  term_density: {
    level: number;
    label: string;
    target_ratio: number;
  };
  sentence_length: {
    level: number;
    label: string;
    target_chars: number;
  };
  abstraction_level: {
    level: number;
    label: string;
  };
  example_complexity: {
    level: number;
    label: string;
  };
  proof_depth: {
    level: number;
    label: string;
  };
  constraints: string[];
}
