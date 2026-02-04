// 禁用API的Persona列表 - 用于测试
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Plus, BookOpen, Eye } from 'lucide-react';
import type { Book } from '../../types/book';
import type { AuthorPersona } from '../../types/persona';

// 模拟数据
const MOCK_BOOKS: Book[] = [
  {
    book_id: 'mock-1',
    title: '测试著作1',
    author: '测试作者1',
    language: 'zh',
    file_type: 'pdf',
    total_words: 10000,
    total_chapters: 10,
    total_viewpoints: 50
  },
  {
    book_id: 'mock-2',
    title: '测试著作2',
    author: '测试作者2',
    language: 'zh',
    file_type: 'epub',
    total_words: 15000,
    total_chapters: 12,
    total_viewpoints: 60
  }
];

export default function PersonaListNoAPI() {
  const [books] = useState<Book[]>(MOCK_BOOKS);
  const [personas] = useState<AuthorPersona[]>([]);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  console.log('🔵 PersonaListNoAPI组件已加载');

  const handleBuildPersona = (book: Book) => {
    console.log('🎯 点击了构建Persona按钮（无API版本）', book);
    alert(`按钮点击成功！准备构建《${book.title}》的Persona\n\n（这是无API版本，不会真正调用后端）`);
  };

  const handleTestClick = () => {
    console.log('🧪 测试按钮点击！（无API版本）');
    alert('测试按钮工作正常！（无API版本）');
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Persona管理（无API版本）</h1>
          <p className="mt-1 text-sm text-gray-600">
            构建和管理作者Persona，共 {personas.length} 个
          </p>
        </div>
        {/* 调试按钮 */}
        <button
          onClick={handleTestClick}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
        >
          🧪 测试按钮
        </button>
      </div>

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
      ) : (
        <>
          {/* Persona列表 */}
          {personas.length > 0 && (
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">已创建的Persona</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {personas.map((persona) => (
                  <div
                    key={persona.persona_id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <User className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">
                            {persona.author_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {persona.persona_id.slice(0, 8)}...
                          </p>
                        </div>
                      </div>
                    </div>

                    <Link
                      to={`/personas/${persona.persona_id}`}
                      className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      查看详情
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 可用著作列表 */}
          <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              构建新Persona ({books.length} 本著作) - 使用模拟数据
            </h2>

            {books.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                暂无著作，请先上传著作
              </div>
            ) : (
              <div className="overflow-hidden border border-gray-200 rounded-md">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        著作信息
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        语言/格式
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        统计
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {books.map((book) => (
                      <tr key={book.book_id} className="hover:bg-gray-50">
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <BookOpen className="h-5 w-5 text-blue-600" />
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {book.title}
                              </div>
                              <div className="text-sm text-gray-500">{book.author}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{book.language}</div>
                          <div className="text-sm text-gray-500">{book.file_type}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                          {book.total_chapters} 章 / {book.total_viewpoints} 观点
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleBuildPersona(book)}
                            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                          >
                            <Plus className="h-4 w-4 mr-1" />
                            构建Persona
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
