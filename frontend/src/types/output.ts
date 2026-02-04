// 输出内容与诊断类型定义

export interface OutputArtifact {
  artifact_id: string;
  book_id: string;
  speaker_persona_id?: string | null;
  audience_persona_id?: string | null;
  task_type: string;
  title?: string | null;
  stage_outputs?: Record<string, string>;
  final_text?: string | null;
  content_format?: string;
  metrics?: Record<string, number>;
  created_at?: string;
}

export interface DiagnosticReport {
  report_id: string;
  artifact_id: string;
  book_id: string;
  speaker_persona_id?: string | null;
  audience_persona_id?: string | null;
  metrics: Record<string, number>;
  issues: string[];
  suggestions?: string | null;
  created_at?: string;
}
