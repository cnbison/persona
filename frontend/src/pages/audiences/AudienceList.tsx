// 受众Persona列表页面
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Plus } from 'lucide-react';
import { audiencesApi } from '../../services/audiences';
import type { AudiencePersona } from '../../types/audience';

const defaultForm = {
  label: '高中生-理科',
  book_id: '',
  education_stage: '高中',
  prior_knowledge: '基础',
  cognitive_preference: '逻辑推导',
  language_preference: '简洁',
  tone_preference: '亲切',
  term_density: 3,
  sentence_length: 3,
  abstraction_level: 3,
  example_complexity: 3,
  proof_depth: 3,
  constraints: '',
};

export default function AudienceList() {
  const [audiences, setAudiences] = useState<AudiencePersona[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(defaultForm);
  const [creating, setCreating] = useState(false);

  const loadAudiences = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await audiencesApi.listAudiences();
      const items = response?.data?.audiences || [];
      setAudiences(items);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAudiences();
  }, []);

  const handleCreate = async () => {
    try {
      setCreating(true);
      setError(null);
      const payload = {
        label: form.label,
        book_id: form.book_id || undefined,
        education_stage: form.education_stage,
        prior_knowledge: form.prior_knowledge,
        cognitive_preference: form.cognitive_preference,
        language_preference: form.language_preference,
        tone_preference: form.tone_preference,
        term_density: Number(form.term_density),
        sentence_length: Number(form.sentence_length),
        abstraction_level: Number(form.abstraction_level),
        example_complexity: Number(form.example_complexity),
        proof_depth: Number(form.proof_depth),
        constraints: form.constraints
          ? form.constraints.split(',').map((item) => item.trim()).filter(Boolean)
          : [],
      };

      await audiencesApi.createAudience(payload);
      setForm(defaultForm);
      await loadAudiences();
    } catch (err: any) {
      setError(err.message || '创建失败');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">受众Persona</h1>
          <p className="mt-1 text-sm text-gray-600">
            管理受众画像与表达适配，共 {audiences.length} 个
          </p>
        </div>
        <div className="inline-flex items-center text-sm text-gray-500">
          <Users className="w-4 h-4 mr-2" />
          Audience
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">快速创建</h2>
          <button
            onClick={handleCreate}
            disabled={creating}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            <Plus className="w-4 h-4 mr-2" />
            {creating ? '创建中...' : '创建受众Persona'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <label className="text-sm text-gray-600">
            名称
            <input
              value={form.label}
              onChange={(e) => setForm({ ...form, label: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            著作ID（可选）
            <input
              value={form.book_id}
              onChange={(e) => setForm({ ...form, book_id: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            教育阶段
            <input
              value={form.education_stage}
              onChange={(e) => setForm({ ...form, education_stage: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            先验知识
            <input
              value={form.prior_knowledge}
              onChange={(e) => setForm({ ...form, prior_knowledge: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            认知偏好
            <input
              value={form.cognitive_preference}
              onChange={(e) => setForm({ ...form, cognitive_preference: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            语言风格
            <input
              value={form.language_preference}
              onChange={(e) => setForm({ ...form, language_preference: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            语气偏好
            <input
              value={form.tone_preference}
              onChange={(e) => setForm({ ...form, tone_preference: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            术语密度(1-5)
            <input
              type="number"
              min={1}
              max={5}
              value={form.term_density}
              onChange={(e) => setForm({ ...form, term_density: Number(e.target.value) })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            句长复杂度(1-5)
            <input
              type="number"
              min={1}
              max={5}
              value={form.sentence_length}
              onChange={(e) => setForm({ ...form, sentence_length: Number(e.target.value) })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            抽象程度(1-5)
            <input
              type="number"
              min={1}
              max={5}
              value={form.abstraction_level}
              onChange={(e) => setForm({ ...form, abstraction_level: Number(e.target.value) })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            案例复杂度(1-5)
            <input
              type="number"
              min={1}
              max={5}
              value={form.example_complexity}
              onChange={(e) => setForm({ ...form, example_complexity: Number(e.target.value) })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            论证深度(1-5)
            <input
              type="number"
              min={1}
              max={5}
              value={form.proof_depth}
              onChange={(e) => setForm({ ...form, proof_depth: Number(e.target.value) })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600 md:col-span-2 lg:col-span-3">
            硬性限制（逗号分隔）
            <input
              value={form.constraints}
              onChange={(e) => setForm({ ...form, constraints: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-500">加载中...</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">受众Persona列表</h2>
          {audiences.length === 0 ? (
            <div className="text-sm text-gray-500">暂无数据</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {audiences.map((audience) => (
                <Link
                  key={audience.audience_id}
                  to={`/audiences/${audience.audience_id}`}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{audience.label}</h3>
                      <p className="text-xs text-gray-500">{audience.audience_id.slice(0, 8)}...</p>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1 text-xs text-gray-600">
                    <p>阶段: {audience.education_stage}</p>
                    <p>先验: {audience.prior_knowledge}</p>
                    <p>偏好: {audience.cognitive_preference}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
