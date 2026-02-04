// 提纲列表页面
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, FileText, BookOpen, User, Clock, CheckCircle, AlertCircle, Trash2 } from 'lucide-react';
import { outlinesApi } from '../../services/outlines';
import { booksApi } from '../../services/books';
import { personasApi } from '../../services/personas';
import type { BookSeries } from '../../types/outline';
import type { Book } from '../../types/book';
import type { AuthorPersona } from '../../types/persona';

export default function OutlineList() {
  const [outlines, setOutlines] = useState<BookSeries[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [personas, setPersonas] = useState<AuthorPersona[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // 加载数据
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载所有数据
      const [outlinesResponse, booksResponse, personasResponse] = await Promise.all([
        outlinesApi.getOutlines().catch(() => ({ data: { outlines: [], total: 0 } })),
        booksApi.getBooks(0, 100),
        personasApi.listPersonas(0, 100).catch(() => ({ data: { items: [], total: 0 } }))
      ]);

      setOutlines(outlinesResponse.data.outlines || []);
      setBooks(booksResponse.data.books || []);
      setPersonas(personasResponse.data.items || []);

      console.log('✅ 提纲列表数据加载完成:');
      console.log(`  - 著作: ${booksResponse.data.books?.length || 0} 本`);
      console.log(`  - Personas: ${personasResponse.data.items?.length || 0} 个`);
      console.log(`  - 提纲: ${outlinesResponse.data.outlines?.length || 0} 个`);
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载提纲列表失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 生成提纲
  const handleGenerateOutline = async () => {
    // 检查是否有可用的著作和Persona
    if (books.length === 0) {
      alert('请先上传著作！');
      navigate('/books/upload');
      return;
    }

    if (personas.length === 0) {
      alert('请先构建至少一个Persona！');
      navigate('/personas');
      return;
    }

    // 简化版：使用第一个可用的著作和Persona
    const firstBook = books[0];
    const firstPersona = personas[0];

    console.log('🎯 准备生成提纲:', {
      book: firstBook.title,
      persona: firstPersona.author_name
    });

    if (!confirm(`确定要基于《${firstBook.title}》生成提纲吗？\n这将使用Persona: ${firstPersona.author_name}`)) {
      return;
    }

    try {
      setGenerating(true);

      const response = await outlinesApi.generateOutline({
        book_id: firstBook.book_id,
        persona_id: firstPersona.persona_id,
      });

      console.log('✅ 提纲生成响应:', response);

      alert(`提纲生成成功！ID: ${response.data.series_id}`);

      // 刷新列表
      await loadData();

      // 跳转到详情页
      navigate(`/outlines/${response.data.series_id}`);
    } catch (err: any) {
      console.error('❌ 生成提纲失败:', err);
      alert(`生成失败: ${err.message || '未知错误'}`);
    } finally {
      setGenerating(false);
    }
  };

  // 删除提纲
  const handleDeleteOutline = async (outlineId: string, title: string) => {
    if (!confirm(`确定要删除提纲《${title}》吗？\n这将删除所有10集内容，此操作不可恢复！`)) {
      return;
    }

    try {
      const response = await outlinesApi.deleteOutline(outlineId);
      console.log('✅ 删除提纲成功:', response);

      alert(`删除成功！已删除 ${response.data.deleted_episodes} 集内容`);

      // 刷新列表
      await loadData();
    } catch (err: any) {
      console.error('❌ 删除提纲失败:', err);
      alert(`删除失败: ${err.message || '未知错误'}`);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 获取状态标签样式
  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { color: string; icon: typeof CheckCircle; text: string }> = {
      draft: { color: 'bg-gray-100 text-gray-700', icon: Clock, text: '草稿' },
      in_progress: { color: 'bg-blue-100 text-blue-700', icon: AlertCircle, text: '进行中' },
      completed: { color: 'bg-green-100 text-green-700', icon: CheckCircle, text: '已完成' },
    };

    const config = statusMap[status] || statusMap.draft;
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">提纲管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            管理和编辑10集节目提纲，共 {outlines.length} 个提纲
          </p>
        </div>
        <button
          onClick={handleGenerateOutline}
          disabled={generating || books.length === 0}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4 mr-2" />
          {generating ? '生成中...' : '生成提纲'}
        </button>
      </div>

      {/* 提示信息 */}
      {books.length === 0 && (
        <div className="rounded-md bg-yellow-50 p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                还没有上传任何著作
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  请先<Link to="/books/upload" className="font-medium underline hover:text-yellow-900">上传著作</Link>后再生成提纲
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* 加载状态 */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-500">加载中...</p>
        </div>
      ) : outlines.length === 0 ? (
        /* 空状态 */
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            还没有生成任何提纲
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {books.length === 0
              ? '请先上传著作'
              : '点击上方按钮开始生成您的第一个提纲'}
          </p>
        </div>
      ) : (
        /* 提纲列表表格 */
        <div className="overflow-hidden bg-white shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  提纲信息
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  关联资源
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  集数统计
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  创建时间
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {outlines.map((outline) => (
                <tr key={outline.series_id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {outline.title || '未命名提纲'}
                        </div>
                        {outline.description && (
                          <div className="text-sm text-gray-500 truncate max-w-xs">
                            {outline.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="text-sm space-y-1">
                      <div className="flex items-center text-gray-900">
                        <BookOpen className="h-3 w-3 mr-1 text-gray-400" />
                        著作ID: {outline.book_id?.slice(0, 8)}...
                      </div>
                      {outline.persona_id && (
                        <div className="flex items-center text-gray-500">
                          <User className="h-3 w-3 mr-1 text-gray-400" />
                          PersonaID: {outline.persona_id.slice(0, 8)}...
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {outline.episodes?.length || 0} 集
                    </div>
                    <div className="text-xs text-gray-500">
                      10集计划
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getStatusBadge(outline.status || 'draft')}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {outline.created_at
                      ? new Date(outline.created_at).toLocaleDateString('zh-CN')
                      : '-'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <Link
                        to={`/outlines/${outline.series_id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        查看详情
                      </Link>
                      <button
                        onClick={() => handleDeleteOutline(outline.series_id, outline.title || '未命名提纲')}
                        className="text-red-600 hover:text-red-900"
                        title="删除提纲"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
