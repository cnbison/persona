// 提纲详情页面 - 10集Timeline可视化
import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Save,
  Edit,
  BookOpen,
  MessageSquare,
  Hash,
  CheckCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { outlinesApi } from '../../services/outlines';
import type { BookSeries, EpisodeOutline } from '../../types/outline';

export default function OutlineDetail() {
  const { outlineId } = useParams<{ outlineId: string }>();
  const [outline, setOutline] = useState<BookSeries | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [editingEpisode, setEditingEpisode] = useState<number | null>(null);
  const [expandedEpisodes, setExpandedEpisodes] = useState<Set<number>>(new Set());
  const navigate = useNavigate();

  // 加载提纲详情
  const loadOutline = async () => {
    if (!outlineId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await outlinesApi.getOutline(outlineId);
      setOutline(response.data);
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载提纲详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 切换集数展开/折叠
  const toggleEpisode = (episodeNumber: number) => {
    const newExpanded = new Set(expandedEpisodes);
    if (newExpanded.has(episodeNumber)) {
      newExpanded.delete(episodeNumber);
    } else {
      newExpanded.add(episodeNumber);
    }
    setExpandedEpisodes(newExpanded);
  };

  // 编辑单集
  const handleEdit = (episodeNumber: number) => {
    setEditingEpisode(episodeNumber);
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setEditingEpisode(null);
  };

  // 保存修改
  const handleSave = async (episodeNumber: number, data: Partial<EpisodeOutline>) => {
    if (!outlineId) return;

    try {
      setSaving(true);
      await outlinesApi.updateEpisode(outlineId, episodeNumber, data);

      // 更新本地状态
      if (outline) {
        setOutline({
          ...outline,
          episodes: outline.episodes?.map((ep) =>
            ep.episode_number === episodeNumber ? { ...ep, ...data } : ep
          ),
        });
      }

      setEditingEpisode(null);
      alert('保存成功！');
    } catch (err: any) {
      alert(`保存失败: ${err.message || '未知错误'}`);
      console.error('保存提纲失败:', err);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadOutline();
  }, [outlineId]);

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

  if (error || !outline) {
    return (
      <div className="space-y-6">
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error || '提纲不存在'}</p>
        </div>
        <Link
          to="/outlines"
          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-900"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          返回列表
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
            to="/outlines"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            返回
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {outline.title || '未命名提纲'}
            </h1>
            {outline.description && (
              <p className="mt-1 text-sm text-gray-600">{outline.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            outline.status === 'completed'
              ? 'bg-green-100 text-green-700'
              : outline.status === 'in_progress'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-700'
          }`}>
            <CheckCircle className="w-4 h-4 mr-1" />
            {outline.status === 'completed' ? '已完成' : outline.status === 'in_progress' ? '进行中' : '草稿'}
          </span>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-blue-100 p-3">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">总集数</p>
              <p className="text-2xl font-semibold text-gray-900">
                {outline.episodes?.length || 0} / 10
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-green-100 p-3">
              <MessageSquare className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">讨论重点</p>
              <p className="text-2xl font-semibold text-gray-900">
                {outline.episodes?.reduce((sum, ep) => sum + (ep.discussion_points?.length || 0), 0) || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-full bg-purple-100 p-3">
              <Hash className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">关联章节</p>
              <p className="text-2xl font-semibold text-gray-900">
                {outline.episodes?.reduce((sum, ep) => sum + (ep.target_chapters?.length || 0), 0) || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 10集Timeline */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">10集提纲 Timeline</h2>
          <p className="mt-1 text-sm text-gray-500">
            点击展开查看详细信息，可编辑章节分配和讨论重点
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {outline.episodes?.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-500">暂无集数数据</p>
            </div>
          ) : (
            outline.episodes?.map((episode, index) => (
              <div key={episode.episode_number} className="hover:bg-gray-50">
                {/* 集数头部 */}
                <div
                  className="px-6 py-4 cursor-pointer"
                  onClick={() => toggleEpisode(episode.episode_number)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {/* 序号圆圈 */}
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                        {episode.episode_number}
                      </div>

                      {/* 标题和摘要 */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-base font-medium text-gray-900">
                            {episode.theme || `第${episode.episode_number}集`}
                          </h3>
                          {episode.status === 'completed' && (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        {episode.theme && (
                          <p className="mt-1 text-sm text-gray-500 line-clamp-1">
                            {episode.theme}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* 展开按钮 */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(episode.episode_number);
                        }}
                        className="p-2 text-gray-400 hover:text-blue-600 rounded-md hover:bg-blue-50"
                        title="编辑"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      {expandedEpisodes.has(episode.episode_number) ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>

                {/* 展开详情 */}
                {expandedEpisodes.has(episode.episode_number) && (
                  <div className="px-6 pb-6 bg-gray-50">
                    <div className="mt-4 space-y-4">
                      {/* 主题 */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">
                          🎯 本集主题
                        </h4>
                        <p className="text-sm text-gray-900 bg-white p-3 rounded-md border border-gray-200">
                          {episode.theme}
                        </p>
                      </div>

                      {/* 目标章节 */}
                      {episode.target_chapters && episode.target_chapters.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">
                            📖 目标章节
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {episode.target_chapters.map((chapter, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-3 py-1 rounded-md text-sm bg-blue-50 border border-blue-200 text-blue-700"
                              >
                                {chapter}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 讨论重点 */}
                      {episode.discussion_points && episode.discussion_points.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">
                            💬 讨论重点
                          </h4>
                          <ul className="space-y-2">
                            {episode.discussion_points.map((point, idx) => (
                              <li
                                key={idx}
                                className="flex items-start text-sm text-gray-600 bg-white p-3 rounded-md border border-gray-200"
                              >
                                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-medium mr-2 mt-0.5">
                                  {idx + 1}
                                </span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* 热点话题匹配 */}
                      {episode.hot_topics && episode.hot_topics.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">
                            🔥 热点话题匹配
                          </h4>
                          <div className="space-y-2">
                            {episode.hot_topics.map((topic, idx) => (
                              <div
                                key={idx}
                                className="bg-white p-3 rounded-md border border-gray-200"
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <h5 className="text-sm font-medium text-gray-900">
                                    {topic.topic_title}
                                  </h5>
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                    相关度: {(topic.relevance_score * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <p className="text-xs text-gray-600">{topic.topic_description}</p>
                                <p className="text-xs text-blue-600 mt-1">
                                  连接点: {topic.connection_point}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 流程设计 */}
                      {episode.flow_design && Object.keys(episode.flow_design).length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">
                            📋 流程设计
                          </h4>
                          <pre className="text-xs text-gray-600 bg-white p-3 rounded-md border border-gray-200 overflow-x-auto">
                            {JSON.stringify(episode.flow_design, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 编辑模式 */}
                {editingEpisode === episode.episode_number && (
                  <div className="px-6 pb-6 bg-blue-50 border-t-2 border-blue-200">
                    <EpisodeEditForm
                      episode={episode}
                      onSave={handleSave}
                      onCancel={handleCancelEdit}
                      saving={saving}
                    />
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// 单集编辑表单组件
interface EpisodeEditFormProps {
  episode: EpisodeOutline;
  onSave: (episodeNumber: number, data: Partial<EpisodeOutline>) => void;
  onCancel: () => void;
  saving: boolean;
}

function EpisodeEditForm({ episode, onSave, onCancel, saving }: EpisodeEditFormProps) {
  const [title, setTitle] = useState(episode.title || '');
  const [summary, setSummary] = useState(episode.summary || '');

  const handleSubmit = () => {
    onSave(episode.episode_number, { title, summary });
  };

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900">
        编辑第{episode.episode_number}集
      </h4>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          标题
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="输入集数标题"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          摘要
        </label>
        <textarea
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          rows={3}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="输入本集摘要"
        />
      </div>

      <div className="flex justify-end space-x-3">
        <button
          onClick={onCancel}
          disabled={saving}
          className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          取消
        </button>
        <button
          onClick={handleSubmit}
          disabled={saving || !title.trim()}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? '保存中...' : '保存'}
        </button>
      </div>
    </div>
  );
}
