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
