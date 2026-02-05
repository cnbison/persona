// Persona相关类型定义

export type ThinkingStyle =
  | 'inductive'
  | 'deductive'
  | 'dialectical'
  | 'analytical'
  | 'intuitive';

export interface AuthorPersona {
  persona_id: string;
  book_id: string;
  author_name: string;

  // 思维方式
  thinking_style?: ThinkingStyle;
  logic_pattern?: string;
  reasoning_framework?: string;

  // 哲学体系
  core_philosophy?: string;
  theoretical_framework?: string;
  key_concepts?: Record<string, string>;

  // 叙事风格
  narrative_style?: string;
  language_rhythm?: string;
  sentence_structure?: string;
  rhetorical_devices?: string[];

  // 价值观
  value_orientation?: string;
  value_judgment_framework?: string;
  core_positions?: string[];
  opposed_positions?: string[];

  // 语气和性格
  tone?: string;
  emotion_tendency?: string;
  expressiveness?: string;
  personality_traits?: string[];
  communication_style?: string;
  attitude_toward_audience?: string;

  // 元数据
  era?: string;
  identity?: string;
  version?: string;
  evidence_links?: string[];
  created_at?: string;
}

export interface PersonaCardSummary {
  persona_id: string;
  author_name: string;
  version: string;
  one_liner: string;
  style_summary: string;
  boundary_tip: string;
  core_positions: string[];
  key_concepts: string[];
  evidence_links: string[];
}

export interface PersonaDiffChange {
  field: string;
  source: any;
  target: any;
}

export interface PersonaDiffResult {
  source_id: string;
  target_id: string;
  total_changes: number;
  changes: PersonaDiffChange[];
}
