// 输出内容详情页面
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { outputsApi } from '../../services/outputs';
import type { OutputArtifact, DiagnosticReport } from '../../types/output';

export default function OutputDetail() {
  const { artifactId } = useParams<{ artifactId: string }>();
  const navigate = useNavigate();

  const [output, setOutput] = useState<OutputArtifact | null>(null);
  const [reports, setReports] = useState<DiagnosticReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (artifactId) {
      loadDetail();
    }
  }, [artifactId]);

  const loadDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      const outputResponse = await outputsApi.getOutput(artifactId!);
      setOutput(outputResponse.data);

      const reportResponse = await outputsApi.listDiagnostics(artifactId!);
      setReports(reportResponse?.data?.reports || []);
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

  if (error || !output) {
    return (
      <div className="text-center py-12 bg-red-50 rounded-lg">
        <p className="text-red-800">{error || '输出内容不存在'}</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          返回
        </button>
      </div>
    );
  }

  const stageOutputs = output.stage_outputs || {};

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
        <h1 className="text-2xl font-bold text-gray-900">{output.title || output.task_type}</h1>
        <p className="mt-1 text-sm text-gray-500">ID: {output.artifact_id}</p>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
          <div>任务类型：{output.task_type}</div>
          <div>著作ID：{output.book_id}</div>
          <div>说者Persona：{output.speaker_persona_id || '未指定'}</div>
          <div>受众Persona：{output.audience_persona_id || '未指定'}</div>
          <div>格式：{output.content_format || 'text'}</div>
          {output.created_at && <div>创建时间：{new Date(output.created_at).toLocaleString('zh-CN')}</div>}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">阶段输出</h2>
        <div className="space-y-3">
          <section>
            <h3 className="text-sm font-semibold text-gray-700">canonical</h3>
            <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap">{stageOutputs.canonical || '无'}</p>
          </section>
          <section>
            <h3 className="text-sm font-semibold text-gray-700">plan</h3>
            <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap">{stageOutputs.plan || '无'}</p>
          </section>
          <section>
            <h3 className="text-sm font-semibold text-gray-700">final</h3>
            <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap">{stageOutputs.final || output.final_text || '无'}</p>
          </section>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900">诊断报告</h2>
        {reports.length === 0 ? (
          <p className="mt-2 text-sm text-gray-500">暂无诊断报告</p>
        ) : (
          <div className="mt-4 space-y-4">
            {reports.map((report) => (
              <div key={report.report_id} className="border border-gray-200 rounded-lg p-4">
                <div className="text-xs text-gray-500">报告ID: {report.report_id}</div>
                <div className="mt-2 text-sm text-gray-700">
                  {Object.entries(report.metrics || {}).map(([key, value]) => (
                    <div key={key}>
                      {key}: {value}
                    </div>
                  ))}
                </div>
                {report.issues && report.issues.length > 0 && (
                  <div className="mt-2 text-sm text-red-600">
                    问题：{report.issues.join('；')}
                  </div>
                )}
                {report.suggestions && (
                  <div className="mt-2 text-sm text-gray-600">建议：{report.suggestions}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
