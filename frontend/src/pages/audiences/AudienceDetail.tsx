// 受众Persona详情页面
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { audiencesApi } from '../../services/audiences';
import type { AudiencePersona } from '../../types/audience';

export default function AudienceDetail() {
  const { audienceId } = useParams<{ audienceId: string }>();
  const navigate = useNavigate();

  const [audience, setAudience] = useState<AudiencePersona | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (audienceId) {
      loadDetail();
    }
  }, [audienceId]);

  const loadDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await audiencesApi.getAudience(audienceId!);
      setAudience(response.data);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error || !audience) {
    return (
      <div className="text-center py-12 bg-red-50 rounded-lg">
        <p className="text-red-800">{error || '受众Persona不存在'}</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          返回
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        返回
      </button>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900">{audience.label}</h1>
        <p className="mt-1 text-sm text-gray-500">ID: {audience.audience_id}</p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>教育阶段：{audience.education_stage}</div>
          <div>先验知识：{audience.prior_knowledge}</div>
          <div>认知偏好：{audience.cognitive_preference}</div>
          <div>语言风格：{audience.language_preference}</div>
          <div>语气偏好：{audience.tone_preference}</div>
          <div>术语密度：{audience.term_density}</div>
          <div>句长复杂度：{audience.sentence_length}</div>
          <div>抽象程度：{audience.abstraction_level}</div>
          <div>案例复杂度：{audience.example_complexity}</div>
          <div>论证深度：{audience.proof_depth}</div>
        </div>

        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-900">硬性限制</h2>
          <p className="mt-2 text-sm text-gray-600">
            {(audience.constraints || []).length > 0
              ? audience.constraints.join('、')
              : '无'}
          </p>
        </div>
      </div>
    </div>
  );
}
