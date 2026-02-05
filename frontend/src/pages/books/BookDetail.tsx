// 著作详情页面
import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, FileText, BookOpen, Upload } from 'lucide-react';
import { booksApi } from '../../services/books';
import { evidenceApi } from '../../services/evidence';
import type { BookDetail as BookDetailType } from '../../types/book';

export default function BookDetail() {
  const { bookId } = useParams<{ bookId: string }>();
  const navigate = useNavigate();

  const [book, setBook] = useState<BookDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [displayedViewpoints, setDisplayedViewpoints] = useState(10);
  const [buildingEvidence, setBuildingEvidence] = useState(false);

  useEffect(() => {
    if (bookId) {
      loadBookDetail();
    }
  }, [bookId]);

  const loadBookDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await booksApi.getBook(bookId);
      setBook(response.data);
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载著作详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBuildEvidence = async () => {
    if (!bookId) return;
    try {
      setBuildingEvidence(true);
      await evidenceApi.buildEvidence(bookId);
      alert('证据库构建完成');
    } catch (err: any) {
      alert(err.message || '构建失败');
    } finally {
      setBuildingEvidence(false);
    }
  };

  const handleLoadMore = () => {
    if (book) {
      setDisplayedViewpoints(prev => Math.min(prev + 10, book.viewpoints.length));
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

  if (error || !book) {
    return (
      <div className="text-center py-12 bg-red-50 rounded-lg">
        <p className="text-red-800">{error || '著作不存在'}</p>
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
      {/* 返回按钮 */}
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        返回
      </button>

      {/* 著作基本信息 */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <div className="border-b border-gray-200 pb-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{book.title}</h1>
              <p className="mt-2 text-lg text-gray-600">{book.author}</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex gap-3">
                <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                  {book.language}
                </span>
                <span className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-800">
                  {book.file_type}
                </span>
              </div>
              <button
                onClick={handleBuildEvidence}
                disabled={buildingEvidence}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {buildingEvidence ? '构建中...' : '构建证据库'}
              </button>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500">总字数</p>
              <p className="text-2xl font-semibold text-gray-900">
                {book.total_words ? book.total_words.toLocaleString() : '-'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">章节数</p>
              <p className="text-2xl font-semibold text-gray-900">{book.total_chapters}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">核心观点</p>
              <p className="text-2xl font-semibold text-gray-900">{book.total_viewpoints}</p>
            </div>
          </div>
        </div>

        {/* 快速操作 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => {
              // TODO: 实现构建Persona功能
              alert('Persona构建功能开发中，请前往Persona页面操作');
            }}
            className="inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <User className="w-5 h-5 mr-2" />
            构建作者Persona
          </button>
          <button
            onClick={() => {
              // TODO: 实现生成提纲功能
              alert('提纲生成功能开发中，请前往提纲页面操作');
            }}
            className="inline-flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <FileText className="w-5 h-5 mr-2" />
            生成10集提纲
          </button>
        </div>
      </div>

      {/* 章节列表 */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <BookOpen className="w-6 h-6 mr-2" />
          章节列表 ({book.chapters.length})
        </h2>

        <div className="overflow-hidden border border-gray-200 rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  章节号
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  标题
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  字数
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {book.chapters.map((chapter, index) => (
                <tr key={chapter.chapter_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    第{chapter.chapter_number}章
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{chapter.title}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {chapter.word_count.toLocaleString()} 字
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {book.chapters.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            暂无章节信息
          </div>
        )}
      </div>

      {/* 核心观点（显示前10个） */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-6 h-6 mr-2" />
          核心观点 ({book.viewpoints.length})
        </h2>

        <div className="space-y-4">
          {book.viewpoints.slice(0, displayedViewpoints).map((viewpoint, index) => (
            <div key={viewpoint.viewpoint_id} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="flex items-start justify-between mb-2">
                <p className="text-sm font-medium text-gray-900">观点 #{index + 1}</p>
                <div className="flex gap-1">
                  {viewpoint.keywords.slice(0, 3).map((keyword, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-sm text-gray-700 line-clamp-3">
                {viewpoint.content.length > 200
                  ? viewpoint.content.substring(0, 200) + '...'
                  : viewpoint.content}
              </p>
              {viewpoint.related_chapter && (
                <p className="text-xs text-gray-500 mt-1">
                  来自: {viewpoint.related_chapter}
                </p>
              )}
            </div>
          ))}
        </div>

        {book.viewpoints.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            暂无核心观点
          </div>
        )}

        {displayedViewpoints < book.viewpoints.length && (
          <div className="mt-4 text-center">
            <button
              onClick={handleLoadMore}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              加载更多观点 ({book.viewpoints.length - displayedViewpoints} 个剩余)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
