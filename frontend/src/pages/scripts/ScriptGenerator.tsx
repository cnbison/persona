// 脚本生成页面
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Play,
  Pause,
  Square,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
} from 'lucide-react';
import { scriptsApi } from '../../services/scripts';
import { outlinesApi } from '../../services/outlines';
import type { BookSeries } from '../../types/outline';
import type { ScriptGenerationProgress } from '../../types/script';

export default function ScriptGenerator() {
  const [outlines, setOutlines] = useState<BookSeries[]>([]);
  const [selectedOutlineId, setSelectedOutlineId] = useState<string>('');
  const [episodeStart, setEpisodeStart] = useState<number>(1);
  const [episodeEnd, setEpisodeEnd] = useState<number>(10);

  // 生成状态
  const [generating, setGenerating] = useState(false);
  const [currentScriptId, setCurrentScriptId] = useState<string | null>(null);
  const [progress, setProgress] = useState<ScriptGenerationProgress | null>(null);

  // 脚本列表
  const [scripts, setScripts] = useState<any[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载提纲列表
  const loadOutlines = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await outlinesApi.getOutlines();
      setOutlines(response.data.outlines || []);

      // 默认选择第一个
      if (response.data.outlines && response.data.outlines.length > 0) {
        setSelectedOutlineId(response.data.outlines[0].series_id);
      }
    } catch (err: any) {
      setError(err.message || '加载提纲列表失败');
      console.error('加载提纲失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 加载脚本列表
  const loadScripts = async () => {
    try {
      const response = await scriptsApi.getScripts();
      setScripts(response.data.scripts || []);
    } catch (err: any) {
      console.error('加载脚本列表失败:', err);
    }
  };

  // 开始生成
  const handleStartGeneration = async () => {
    if (!selectedOutlineId) {
      alert('请先选择提纲！');
      return;
    }

    if (episodeStart < 1 || episodeEnd > 10 || episodeStart > episodeEnd) {
      alert('集数范围无效！请设置1-10之间的有效范围。');
      return;
    }

    try {
      setGenerating(true);
      setError(null);

      const response = await scriptsApi.generateScript({
        series_id: selectedOutlineId,
        episode_start: episodeStart,
        episode_end: episodeEnd,
      });

      setCurrentScriptId(response.data.script_id);
      alert(`脚本生成已开始！ID: ${response.data.script_id}`);
    } catch (err: any) {
      setError(`生成失败: ${err.message || '未知错误'}`);
      console.error('生成脚本失败:', err);
      setGenerating(false);
    }
  };

  // 轮询进度
  useEffect(() => {
    if (!currentScriptId || !generating) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await scriptsApi.getProgress(currentScriptId);
        console.log('📊 进度响应:', response.data);
        setProgress(response.data);

        // 如果完成或失败，停止轮询
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          setGenerating(false);
          clearInterval(pollInterval);

          // 如果完成且有生成的脚本ID，使用第一个脚本来查看
          if (response.data.status === 'completed' && response.data.extra_data?.generated_script_ids) {
            const scriptIds = response.data.extra_data.generated_script_ids;
            if (scriptIds && scriptIds.length > 0) {
              console.log('✅ 脚本生成完成，任务ID:', currentScriptId);
              console.log('✅ 实际脚本IDs:', scriptIds);
              console.log('✅ 更新当前脚本ID为:', scriptIds[0]);
              // 使用第一个生成的脚本ID
              setCurrentScriptId(scriptIds[0]);
              // 刷新脚本列表
              loadScripts();
            } else {
              console.warn('⚠️ 进度完成但没有脚本IDs');
            }
          } else {
            console.warn('⚠️ 进度完成但没有extra_data或generated_script_ids');
          }
        }
      } catch (err: any) {
        console.error('❌ 获取进度失败:', err);
      }
    }, 2000); // 每2秒轮询一次

    return () => clearInterval(pollInterval);
  }, [currentScriptId, generating]);

  useEffect(() => {
    loadOutlines();
    loadScripts();
  }, []);

  // 获取状态标签
  const getStatusBadge = (status?: string) => {
    if (!status) return null;

    const statusMap: Record<string, { color: string; icon: typeof CheckCircle; text: string }> = {
      generating: { color: 'bg-blue-100 text-blue-700', icon: RefreshCw, text: '生成中' },
      completed: { color: 'bg-green-100 text-green-700', icon: CheckCircle, text: '已完成' },
      failed: { color: 'bg-red-100 text-red-700', icon: AlertCircle, text: '失败' },
    };

    const config = statusMap[status];
    if (!config) return null;

    const Icon = config.icon;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.text}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">脚本生成</h1>
        <p className="mt-1 text-sm text-gray-600">
          基于提纲生成AI对话脚本
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* 配置区域 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 左侧：选择提纲 */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">选择提纲</h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-sm text-gray-500">加载中...</p>
            </div>
          ) : outlines.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">还没有提纲</h3>
              <p className="mt-1 text-sm text-gray-500">
                请先<Link to="/outlines" className="text-blue-600 hover:text-blue-900">创建提纲</Link>
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {outlines.map((outline) => (
                <label
                  key={outline.series_id}
                  className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedOutlineId === outline.series_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="outline"
                    value={outline.series_id}
                    checked={selectedOutlineId === outline.series_id}
                    onChange={(e) => setSelectedOutlineId(e.target.value)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">
                        {outline.title || '未命名提纲'}
                      </span>
                      {getStatusBadge(outline.status)}
                    </div>
                    {outline.description && (
                      <p className="mt-1 text-xs text-gray-500 line-clamp-2">
                        {outline.description}
                      </p>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      {outline.episodes?.length || 0} 集
                    </p>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* 右侧：生成参数 */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">生成参数</h2>

          <div className="space-y-4">
            {/* 集数范围 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                集数范围
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={episodeStart}
                  onChange={(e) => setEpisodeStart(parseInt(e.target.value) || 1)}
                  className="block w-24 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-gray-500">至</span>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={episodeEnd}
                  onChange={(e) => setEpisodeEnd(parseInt(e.target.value) || 10)}
                  className="block w-24 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-sm text-gray-500">集</span>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                将生成 {episodeEnd - episodeStart + 1} 集脚本
              </p>
            </div>

            {/* 生成按钮 */}
            <div className="pt-4 border-t border-gray-200">
              {!generating ? (
                <button
                  onClick={handleStartGeneration}
                  disabled={!selectedOutlineId}
                  className="w-full flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  <Play className="w-4 h-4 mr-2" />
                  开始生成
                </button>
              ) : (
                <button
                  disabled
                  className="w-full flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-400 cursor-not-allowed"
                >
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  生成中...
                </button>
              )}
            </div>

            {/* 进度展示 */}
            {progress && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    {progress.current_step}
                  </span>
                  <span className="text-sm font-semibold text-blue-600">
                    {progress.progress_percentage}%
                  </span>
                </div>
                {/* 进度条 */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress.progress_percentage}%` }}
                  ></div>
                </div>

                {progress.current_section && (
                  <p className="mt-2 text-xs text-gray-500">
                    当前: {progress.current_section}
                  </p>
                )}

                {progress.status === 'completed' && currentScriptId && (
                  <Link
                    to={`/scripts/${currentScriptId}`}
                    className="mt-3 block text-center text-sm text-blue-600 hover:text-blue-900"
                  >
                    查看脚本 →
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 已生成的脚本列表 */}
      {scripts.length > 0 && (
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">已生成的脚本</h2>
            <span className="text-sm text-gray-500">共 {scripts.length} 个</span>
          </div>
          <div className="space-y-3">
            {scripts.map((script) => (
              <div
                key={script.script_id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center flex-1">
                  <FileText className="h-5 w-5 text-gray-400 mr-3" />
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <p className="text-sm font-medium text-gray-900">
                        {script.title || `第${script.episode_number}集脚本`}
                      </p>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        第{script.episode_number}集
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                      <span>ID: {script.script_id.slice(0, 8)}...</span>
                      <span>{script.total_word_count}字</span>
                      <span>{Math.round(script.total_duration)}分钟</span>
                      <span>作者占比 {Math.round(script.author_speaking_ratio * 100)}%</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/scripts/${script.script_id}`}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    查看
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {scripts.length === 0 && !generating && (
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">还没有生成的脚本</h3>
          <p className="mt-1 text-sm text-gray-500">
            选择提纲并点击"开始生成"来创建第一个脚本
          </p>
        </div>
      )}
    </div>
  );
}
