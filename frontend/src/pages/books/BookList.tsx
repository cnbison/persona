// 著作列表页面
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Trash2, Upload, Search } from 'lucide-react';
import { booksApi } from '../../services/books';
import type { Book } from '../../types/book';

export default function BookList() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // 加载著作列表
  const loadBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await booksApi.getBooks(0, 50);
      setBooks(response.data.books || []);
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载著作列表失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 删除著作
  const handleDelete = async (bookId: string, title: string) => {
    if (!confirm(`确定要删除《${title}》吗？此操作不可恢复。`)) {
      return;
    }

    try {
      await booksApi.deleteBook(bookId);
      // 从列表中移除
      setBooks(books.filter((book) => book.book_id !== bookId));
      alert('删除成功');
    } catch (err: any) {
      alert(`删除失败: ${err.message}`);
      console.error('删除著作失败:', err);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  // 搜索过滤
  const filteredBooks = books.filter(
    (book) =>
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">著作管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            管理上传的经典著作，共 {books.length} 本
          </p>
        </div>
        <Link
          to="/books/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <Upload className="w-4 h-4 mr-2" />
          上传著作
        </Link>
      </div>

      {/* 搜索框 */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="搜索著作标题或作者..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
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
      ) : filteredBooks.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchTerm ? '没有找到匹配的著作' : '还没有上传任何著作'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? '请尝试其他搜索词' : '点击上方按钮上传第一本著作'}
          </p>
        </div>
      ) : (
        /* 著作列表表格 */
        <div className="overflow-hidden bg-white shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  著作信息
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  语言/格式
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  统计
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
              {filteredBooks.map((book) => (
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
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {book.total_chapters} 章 / {book.total_viewpoints} 观点
                    </div>
                    <div className="text-sm text-gray-500">
                      {book.total_words ? `${book.total_words.toLocaleString()} 字` : '-'}
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(book.created_at).toLocaleDateString('zh-CN')}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link
                      to={`/books/${book.book_id}`}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      查看
                    </Link>
                    <button
                      onClick={() => handleDelete(book.book_id, book.title)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="h-4 w-4 inline" />
                    </button>
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
