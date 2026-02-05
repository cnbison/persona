// 风格热力图页面
import { useMemo, useState } from 'react';
import { diagnosticsApi } from '../../services/diagnostics';

interface HeatmapMetric {
  key: string;
  label: string;
  value: number;
  max: number;
}

const defaultMetrics: HeatmapMetric[] = [
  { key: 'term_density_estimate', label: '术语密度', value: 0.08, max: 0.2 },
  { key: 'avg_sentence_length', label: '句长', value: 20, max: 40 },
  { key: 'paragraph_count', label: '段落数', value: 5, max: 10 },
  { key: 'audience_fit_score', label: '受众匹配', value: 0.7, max: 1 },
  { key: 'locked_facts_missing_ratio', label: '锁定缺失', value: 0.1, max: 1 },
];

export default function HeatmapView() {
  const [input, setInput] = useState('');
  const [reportId, setReportId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const metrics = useMemo(() => {
    if (!input) return defaultMetrics;

    try {
      const parsed = JSON.parse(input);
      return defaultMetrics.map((metric) => ({
        ...metric,
        value: typeof parsed[metric.key] === 'number' ? parsed[metric.key] : metric.value,
      }));
    } catch (err) {
      return defaultMetrics;
    }
  }, [input]);

  const handleLoadReport = async () => {
    if (!reportId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await diagnosticsApi.getReport(reportId);
      const metricsData = response?.data?.metrics || {};
      setInput(JSON.stringify(metricsData, null, 2));
    } catch (err: any) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const getIntensity = (value: number, max: number) => {
    const ratio = Math.min(Math.max(value / max, 0), 1);
    const intensity = Math.round(20 + ratio * 60);
    return `rgb(34, 197, 94, ${intensity / 100})`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">风格热力图</h1>
        <p className="mt-1 text-sm text-gray-600">展示诊断指标的强度分布</p>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">诊断指标输入</h2>
        <div className="flex flex-col md:flex-row gap-3 mb-4">
          <input
            value={reportId}
            onChange={(e) => setReportId(e.target.value)}
            placeholder="诊断报告ID（可选）"
            className="flex-1 rounded-md border-gray-200 text-sm"
          />
          <button
            onClick={handleLoadReport}
            disabled={loading || !reportId}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? '加载中...' : '拉取指标'}
          </button>
        </div>
        {error && (
          <div className="mb-3 rounded-md bg-red-50 p-3 text-sm text-red-800">
            {error}
          </div>
        )}
        <textarea
          rows={6}
          placeholder="粘贴诊断指标JSON，例如 {\"term_density_estimate\":0.12}"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full rounded-md border-gray-200 text-sm"
        />
        <p className="mt-2 text-xs text-gray-500">未输入时展示示例数据</p>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">热力图</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics.map((metric) => (
            <div key={metric.key} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">{metric.label}</p>
                <span className="text-xs text-gray-500">{metric.value}</span>
              </div>
              <div className="mt-3 h-3 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full"
                  style={{
                    width: `${Math.min((metric.value / metric.max) * 100, 100)}%`,
                    backgroundColor: getIntensity(metric.value, metric.max),
                  }}
                />
              </div>
              <p className="mt-2 text-xs text-gray-500">最大值参考：{metric.max}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
