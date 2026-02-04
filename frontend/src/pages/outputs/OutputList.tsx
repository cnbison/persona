// 输出内容列表页面
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, Plus, GitCompare } from 'lucide-react';
import { outputsApi } from '../../services/outputs';
import type { OutputArtifact } from '../../types/output';

export default function OutputList() {
  const navigate = useNavigate();
  const [outputs, setOutputs] = useState<OutputArtifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOutputs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await outputsApi.listOutputs(0, 50);
      const items = response?.data?.artifacts || [];
      setOutputs(items);
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOutputs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">输出内容</h1>
          <p className="mt-1 text-sm text-gray-600">管理生成结果与诊断报告</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/outputs/generate')}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            生成输出
          </button>
          <button
            onClick={() => navigate('/outputs/diff')}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-700 bg-white border border-gray-200 hover:bg-gray-50"
          >
            <GitCompare className="w-4 h-4 mr-2" />
            Diff 对比
          </button>
          <div className="inline-flex items-center text-sm text-gray-500">
            <FileText className="w-4 h-4 mr-2" />
            Outputs
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-500">加载中...</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">输出列表</h2>
          {outputs.length === 0 ? (
            <div className="text-sm text-gray-500">暂无输出内容</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {outputs.map((output) => (
                <Link
                  key={output.artifact_id}
                  to={`/outputs/${output.artifact_id}`}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="text-sm font-semibold text-gray-900">
                    {output.title || output.task_type}
                  </div>
                  <div className="mt-2 text-xs text-gray-600 space-y-1">
                    <p>任务类型: {output.task_type}</p>
                    <p>著作ID: {output.book_id.slice(0, 8)}...</p>
                    {output.created_at && (
                      <p>创建时间: {new Date(output.created_at).toLocaleString('zh-CN')}</p>
                    )}
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
