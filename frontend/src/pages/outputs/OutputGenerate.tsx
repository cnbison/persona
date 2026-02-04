// 输出内容生成页面
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { outputsApi } from '../../services/outputs';

const defaultForm = {
  book_id: '',
  task_type: 'rewrite',
  title: '',
  source_text: '',
  speaker_persona_id: '',
  audience_persona_id: '',
  create_report: true,
};

export default function OutputGenerate() {
  const navigate = useNavigate();
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultId, setResultId] = useState<string | null>(null);

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
            受众Persona ID（可选）
            <input
              value={form.audience_persona_id}
              onChange={(e) => setForm({ ...form, audience_persona_id: e.target.value })}
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

        <label className="text-sm text-gray-600 block">
          源文本
          <textarea
            rows={8}
            value={form.source_text}
            onChange={(e) => setForm({ ...form, source_text: e.target.value })}
            className="mt-1 w-full rounded-md border-gray-200 text-sm"
          />
        </label>

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
