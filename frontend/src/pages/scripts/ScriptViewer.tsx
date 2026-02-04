// 脚本查看页面
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Download,
  FileText,
  User,
  Mic,
  BookOpen,
  TrendingUp,
  Clock,
} from 'lucide-react';
import { scriptsApi } from '../../services/scripts';

// 临时类型定义 - 与后端API返回格式匹配
interface DialogueTurn {
  turn_id: string;
  speaker: 'author' | 'host';
  content: string;
  original_text_reference?: string;
  hot_topic_reference?: string;
  duration_seconds?: number;
  word_count: number;
}

interface ScriptResponse {
  script_id: string;
  outline_id: string;
  book_id: string;
  episode_number: number;
  title: string;
  theme: string;
  dialogue_turns: DialogueTurn[];
  statistics: {
    total_duration: number;
    total_word_count: number;
    author_speaking_ratio: number;
    host_speaking_ratio: number;
  };
  quality_metrics?: any;
  generation_time?: string;
  version: string;
}

export default function ScriptViewer() {
  const { scriptId } = useParams<{ scriptId: string }>();
  const [script, setScript] = useState<ScriptResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // 加载脚本
  const loadScript = async () => {
    if (!scriptId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await scriptsApi.getScript(scriptId);
      setScript(response.data);
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载脚本失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 导出脚本
  const handleExport = async (format: 'txt' | 'md' | 'json') => {
    if (!scriptId) return;

    try {
      setExporting(true);
      const response = await scriptsApi.exportScript(scriptId, format);

      // 创建下载链接
      const link = document.createElement('a');
      link.href = response.data.download_url;
      link.download = response.data.filename;
      link.click();

      alert(`导出成功！文件名: ${response.data.filename}`);
    } catch (err: any) {
      alert(`导出失败: ${err.message || '未知错误'}`);
      console.error('导出脚本失败:', err);
    } finally {
      setExporting(false);
    }
  };

  useEffect(() => {
    loadScript();
  }, [scriptId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  if (error || !script) {
    return (
      <div className="space-y-6">
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error || '脚本不存在'}</p>
        </div>
        <Link
          to="/scripts"
          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-900"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          返回
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/scripts"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            返回
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {script.title || `第${script.episode_number}集脚本`}
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              主题: {script.theme}
            </p>
            <p className="text-xs text-gray-500">
              ID: {script.script_id?.slice(0, 8)}...
            </p>
          </div>
        </div>

        {/* 导出按钮 */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleExport('txt')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-2" />
            TXT
          </button>
          <button
            onClick={() => handleExport('md')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-2" />
            MD
          </button>
          <button
            onClick={() => handleExport('json')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4 mr-2" />
            JSON
          </button>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-blue-100 p-3">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">总时长</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(script.statistics.total_duration)}分钟
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-green-100 p-3">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">总字数</p>
              <p className="text-2xl font-semibold text-gray-900">
                {script.statistics.total_word_count}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-purple-100 p-3">
              <User className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">作者占比</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(script.statistics.author_speaking_ratio * 100)}%
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-orange-100 p-3">
              <Mic className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">主持人占比</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(script.statistics.host_speaking_ratio * 100)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 对话内容 */}
      <div className="rounded-lg bg-white shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">对话内容</h2>
          <p className="text-sm text-gray-600 mt-1">
            共 {script.dialogue_turns.length} 轮对话
          </p>
        </div>

        <div className="p-6 space-y-4 max-h-[800px] overflow-y-auto">
          {script.dialogue_turns.map((turn, index) => (
            <DialogueBubble key={index} dialogue={turn} />
          ))}
        </div>
      </div>
    </div>
  );
}

// 对话气泡组件
interface DialogueBubbleProps {
  dialogue: DialogueTurn;
}

function DialogueBubble({ dialogue }: DialogueBubbleProps) {
  const isAuthor = dialogue.speaker === 'author';

  return (
    <div className={`flex ${isAuthor ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isAuthor
            ? 'bg-purple-50 border-l-4 border-purple-600'
            : 'bg-blue-50 border-r-4 border-blue-600'
        }`}
      >
        {/* 说话人标签 */}
        <div className="flex items-center mb-2">
          {isAuthor ? (
            <>
              <User className="w-4 h-4 text-purple-600 mr-1.5" />
              <span className="text-sm font-medium text-purple-900">作者</span>
            </>
          ) : (
            <>
              <Mic className="w-4 h-4 text-blue-600 mr-1.5" />
              <span className="text-sm font-medium text-blue-900">主持人</span>
            </>
          )}
          {dialogue.duration_seconds && (
            <>
              <span className="mx-2 text-gray-300">|</span>
              <span className="text-xs text-gray-500">
                {Math.round(dialogue.duration_seconds / 60)}分钟
              </span>
            </>
          )}
          <span className="mx-2 text-gray-300">|</span>
          <span className="text-xs text-gray-500">{dialogue.word_count}字</span>
        </div>

        {/* 对话内容 */}
        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
          {dialogue.content}
        </p>

        {/* 引用标注 */}
        {(dialogue.original_text_reference || dialogue.hot_topic_reference) && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-1.5">
            {dialogue.original_text_reference && (
              <div className="flex items-start text-xs">
                <BookOpen className="w-3 h-3 text-green-600 mr-1.5 mt-0.5 flex-shrink-0" />
                <span className="text-green-700">{dialogue.original_text_reference}</span>
              </div>
            )}
            {dialogue.hot_topic_reference && (
              <div className="flex items-start text-xs">
                <TrendingUp className="w-3 h-3 text-red-600 mr-1.5 mt-0.5 flex-shrink-0" />
                <span className="text-red-700">{dialogue.hot_topic_reference}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
