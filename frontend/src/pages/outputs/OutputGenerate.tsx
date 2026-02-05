// 输出内容生成页面
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { outputsApi } from '../../services/outputs';
import { audiencesApi } from '../../services/audiences';
import type { AudienceConstraints, AudiencePersona } from '../../types/audience';

const defaultForm = {
  book_id: '',
  task_type: 'rewrite',
  title: '',
  source_text: '',
  speaker_persona_id: '',
  audience_persona_id: '',
  locked_facts: '',
  mix_structure: 70,
  mix_perception: 55,
  mix_meaning: 50,
  mix_distribution: 35,
  skin_sentence_length: 55,
  skin_abstraction: 45,
  skin_emotion: 30,
  task_content_type: 'general',
  task_primary_goal: 'clarity',
  task_audience: 55,
  custom_prompt: '',
  create_report: true,
};

export default function OutputGenerate() {
  const navigate = useNavigate();
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultId, setResultId] = useState<string | null>(null);
  const [audiences, setAudiences] = useState<AudiencePersona[]>([]);
  const [audiencesLoading, setAudiencesLoading] = useState(false);
  const [constraints, setConstraints] = useState<AudienceConstraints | null>(null);
  const [constraintsLoading, setConstraintsLoading] = useState(false);
  const [constraintsError, setConstraintsError] = useState<string | null>(null);

  useEffect(() => {
    const loadAudiences = async () => {
      try {
        setAudiencesLoading(true);
        const response = await audiencesApi.listAudiences();
        setAudiences(response?.data?.audiences || []);
      } catch (err: any) {
        console.error('加载受众Persona失败', err);
      } finally {
        setAudiencesLoading(false);
      }
    };

    loadAudiences();
  }, []);

  const loadConstraints = async (audienceId: string) => {
    if (!audienceId) {
      setConstraints(null);
      setConstraintsError(null);
      return;
    }
    try {
      setConstraintsLoading(true);
      setConstraintsError(null);
      const response = await audiencesApi.getAudienceConstraints(audienceId);
      setConstraints(response?.data?.constraints || null);
    } catch (err: any) {
      setConstraintsError(err.message || '加载约束失败');
      setConstraints(null);
    } finally {
      setConstraintsLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      setResultId(null);

      if (!form.book_id || !form.source_text) {
        setError('请填写著作ID与源文本');
        setLoading(false);
        return;
      }

      const payload = {
        book_id: form.book_id,
        task_type: form.task_type,
        title: form.title || undefined,
        source_text: form.source_text,
        speaker_persona_id: form.speaker_persona_id || undefined,
        audience_persona_id: form.audience_persona_id || undefined,
        locked_facts: form.locked_facts
          ? form.locked_facts.split(',').map((item) => item.trim()).filter(Boolean)
          : [],
        style_config: {
          mix: {
            structure: form.mix_structure,
            perception: form.mix_perception,
            meaning: form.mix_meaning,
            distribution: form.mix_distribution,
          },
          skin: {
            sentenceLength: form.skin_sentence_length,
            abstraction: form.skin_abstraction,
            emotion: form.skin_emotion,
          },
          task: {
            contentType: form.task_content_type,
            primaryGoal: form.task_primary_goal,
            audience: form.task_audience,
          },
          customPrompt: form.custom_prompt,
        },
        create_report: form.create_report,
      };

      const response = await outputsApi.generateOutput(payload);
      const artifactId = response?.data?.artifact_id;
      setResultId(artifactId || null);
    } catch (err: any) {
      setError(err.message || '生成失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">生成输出</h1>
        <p className="mt-1 text-sm text-gray-600">
          生成 canonical / plan / final，并可选生成诊断报告
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {resultId && (
        <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">
          生成成功，输出ID: {resultId}
          <button
            onClick={() => navigate(`/outputs/${resultId}`)}
            className="ml-3 text-blue-600 hover:text-blue-800"
          >
            查看详情
          </button>
        </div>
      )}

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="text-sm text-gray-600">
            著作ID
            <input
              value={form.book_id}
              onChange={(e) => setForm({ ...form, book_id: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            任务类型
            <select
              value={form.task_type}
              onChange={(e) => setForm({ ...form, task_type: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            >
              <option value="outline">outline</option>
              <option value="dialogue">dialogue</option>
              <option value="rewrite">rewrite</option>
              <option value="explain">explain</option>
            </select>
          </label>
          <label className="text-sm text-gray-600">
            标题（可选）
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            说者Persona ID（可选）
            <input
              value={form.speaker_persona_id}
              onChange={(e) => setForm({ ...form, speaker_persona_id: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            受众Persona（可选）
            <select
              value={form.audience_persona_id}
              onChange={(e) => {
                const value = e.target.value;
                setForm({ ...form, audience_persona_id: value });
                loadConstraints(value);
              }}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            >
              <option value="">未选择</option>
              {audiences.map((audience) => (
                <option key={audience.audience_id} value={audience.audience_id}>
                  {audience.label} ({audience.audience_id})
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-400">
              {audiencesLoading ? '加载受众列表中...' : '如需手动填写ID，可直接在下方输入'}
            </p>
            <div className="mt-2 flex items-center gap-2">
              <input
                value={form.audience_persona_id}
                onChange={(e) => setForm({ ...form, audience_persona_id: e.target.value })}
                placeholder="手动输入受众Persona ID"
                className="w-full rounded-md border-gray-200 text-sm"
              />
              <button
                type="button"
                onClick={() => loadConstraints(form.audience_persona_id)}
                disabled={constraintsLoading || !form.audience_persona_id}
                className="inline-flex items-center rounded-md border border-gray-200 px-3 py-2 text-xs text-gray-700 hover:bg-gray-50 disabled:opacity-60"
              >
                {constraintsLoading ? '加载中...' : '加载约束'}
              </button>
            </div>
          </label>
          <label className="text-sm text-gray-600 md:col-span-2">
            锁定概念/事实（逗号分隔）
            <input
              value={form.locked_facts}
              onChange={(e) => setForm({ ...form, locked_facts: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600 flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.create_report}
              onChange={(e) => setForm({ ...form, create_report: e.target.checked })}
            />
            自动生成诊断报告
          </label>
        </div>

        <div className="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">受众适配约束</h3>
            {constraints && (
              <span className="text-xs text-gray-500">已加载受众约束</span>
            )}
          </div>

          {constraintsError && (
            <div className="mt-2 text-xs text-red-600">{constraintsError}</div>
          )}

          {!constraints && !constraintsLoading && (
            <div className="mt-2 text-xs text-gray-500">
              选择受众Persona后可查看自动生成的表达约束与目标。
            </div>
          )}

          {constraintsLoading && (
            <div className="mt-2 text-xs text-gray-500">约束加载中...</div>
          )}

          {constraints && (
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-700">
              <div>教育阶段：{constraints.education_stage}</div>
              <div>先验知识：{constraints.prior_knowledge}</div>
              <div>认知偏好：{constraints.cognitive_preference}</div>
              <div>语言风格：{constraints.language_preference}</div>
              <div>语气偏好：{constraints.tone_preference}</div>
              <div>
                术语密度：{constraints.term_density.label} (目标 {Math.round(constraints.term_density.target_ratio * 100)}%)
              </div>
              <div>
                句长：{constraints.sentence_length.label} (约 {constraints.sentence_length.target_chars} 字)
              </div>
              <div>抽象程度：{constraints.abstraction_level.label}</div>
              <div>案例复杂度：{constraints.example_complexity.label}</div>
              <div>论证深度：{constraints.proof_depth.label}</div>
              <div className="md:col-span-2">
                硬性限制：{constraints.constraints.length > 0 ? constraints.constraints.join('、') : '无'}
              </div>
            </div>
          )}
        </div>

        <label className="text-sm text-gray-600 block">
          源文本
          <textarea
            rows={8}
            value={form.source_text}
            onChange={(e) => setForm({ ...form, source_text: e.target.value })}
            className="mt-1 w-full rounded-md border-gray-200 text-sm"
          />
        </label>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900">风格混音</h3>
            {[
              { key: 'mix_structure', label: '结构', value: form.mix_structure },
              { key: 'mix_perception', label: '感知', value: form.mix_perception },
              { key: 'mix_meaning', label: '意义', value: form.mix_meaning },
              { key: 'mix_distribution', label: '分布', value: form.mix_distribution },
            ].map((item) => (
              <label key={item.key} className="text-xs text-gray-600 block">
                {item.label}: {item.value}
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={item.value}
                  onChange={(e) => setForm({ ...form, [item.key]: Number(e.target.value) } as any)}
                  className="mt-1 w-full"
                />
              </label>
            ))}
          </div>
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900">语言皮肤</h3>
            {[
              { key: 'skin_sentence_length', label: '句长', value: form.skin_sentence_length },
              { key: 'skin_abstraction', label: '抽象', value: form.skin_abstraction },
              { key: 'skin_emotion', label: '情感', value: form.skin_emotion },
            ].map((item) => (
              <label key={item.key} className="text-xs text-gray-600 block">
                {item.label}: {item.value}
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={item.value}
                  onChange={(e) => setForm({ ...form, [item.key]: Number(e.target.value) } as any)}
                  className="mt-1 w-full"
                />
              </label>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="text-sm text-gray-600">
            内容类型
            <input
              value={form.task_content_type}
              onChange={(e) => setForm({ ...form, task_content_type: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            主要目标
            <input
              value={form.task_primary_goal}
              onChange={(e) => setForm({ ...form, task_primary_goal: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600 md:col-span-2">
            受众强度: {form.task_audience}
            <input
              type="range"
              min={0}
              max={100}
              value={form.task_audience}
              onChange={(e) => setForm({ ...form, task_audience: Number(e.target.value) })}
              className="mt-1 w-full"
            />
          </label>
          <label className="text-sm text-gray-600 md:col-span-2">
            额外Prompt（可选）
            <textarea
              rows={3}
              value={form.custom_prompt}
              onChange={(e) => setForm({ ...form, custom_prompt: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? '生成中...' : '生成输出'}
          </button>
        </div>
      </div>
    </div>
  );
}
