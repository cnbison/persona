// Persona列表页面
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Plus, BookOpen, Eye, Upload } from 'lucide-react';
import { booksApi } from '../../services/books';
import { personasApi } from '../../services/personas';
import type { Book } from '../../types/book';
import type { AuthorPersona } from '../../types/persona';

export default function PersonaList() {
  const [books, setBooks] = useState<Book[]>([]);
  const [personas, setPersonas] = useState<AuthorPersona[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [buildingPersonaId, setBuildingPersonaId] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importMode, setImportMode] = useState<'new' | 'new_version' | 'overwrite'>('new_version');
  const [importResult, setImportResult] = useState<string | null>(null);
  const [importFileName, setImportFileName] = useState<string | null>(null);

  // 调试：组件挂载时打印日志
  console.log('🔵 PersonaList组件已加载');

  // 加载著作和Persona列表
  const loadData = async () => {
    try {
      console.log('🔄 开始加载数据...');
      setLoading(true);
      setError(null);

      // 加载所有著作
      console.log('📚 调用 booksApi.getBooks()...');
      const booksResponse = await booksApi.getBooks(0, 50);
      console.log('✅ booksApi响应:', booksResponse);

      // 检查响应结构
      if (!booksResponse || !booksResponse.data) {
        console.error('❌ booksResponse结构异常:', booksResponse);
        throw new Error('API响应格式异常');
      }

      const booksData = booksResponse.data.books || [];
      console.log(`✅ 获取到 ${booksData.length} 本书`);
      setBooks(booksData);

      // 加载Persona列表
      const personasResponse = await personasApi.listPersonas();
      console.log('✅ Personas响应:', personasResponse);
      const personasData = personasResponse.data.items || [];
      console.log(`✅ 获取到 ${personasData.length} 个Persona`);
      setPersonas(personasData);

      console.log('✅ 数据加载完成');
    } catch (err: any) {
      console.error('❌ 加载失败:', err);
      setError(err.message || '加载失败');
      console.error('完整错误:', err);
    } finally {
      setLoading(false);
    }
  };

  // 从著作构建Persona
  const handleBuildPersona = async (book: Book) => {
    console.log('🎯 点击了构建Persona按钮', book);

    try {
      console.log('📡 开始调用API...');
      console.log('  Book ID:', book.book_id);

      // 设置loading状态
      setBuildingPersonaId(book.book_id);

      const response = await personasApi.createPersona(book.book_id);
      console.log('✅ API响应:', response);

      if (response.data && response.data.persona_id) {
        console.log(`✅ Persona构建成功: ${response.data.persona_id}`);

        // 显示成功提示（使用console而不是alert，避免阻塞）
        console.log(`🎉 《${book.title}》的Persona构建成功！`);

        // 刷新列表
        await loadData();

        // 3秒后清除loading状态
        setTimeout(() => {
          setBuildingPersonaId(null);
        }, 3000);
      } else {
        console.error('❌ 响应格式异常:', response);
        setError('构建响应格式异常，请查看控制台');
        setBuildingPersonaId(null);
      }
    } catch (err: any) {
      console.error('❌ 构建Persona时出错:', err);

      // 检查是否是超时错误
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        console.log('⏱️ 请求超时，但Persona可能已成功创建，正在刷新列表...');
        setError('请求超时，正在刷新列表...');

        // 超时也刷新列表，可能已经创建成功
        await loadData();

        // 3秒后清除错误提示和loading状态
        setTimeout(() => {
          setError(null);
          setBuildingPersonaId(null);
        }, 3000);
      } else {
        setError(`构建失败: ${err.message || err.code || '未知错误'}`);
        setBuildingPersonaId(null);
      }
    }
  };

  const handleImportPersona = async (file: File | null) => {
    if (!file) return;
    try {
      setImporting(true);
      setImportResult(null);
      setImportFileName(file.name);
      const content = await file.text();
      const payload = JSON.parse(content);
      const response = await personasApi.importPersona(payload, importMode);
      const personaId = response?.data?.persona_id;
      const version = response?.data?.version;
      setImportResult(`导入成功：${personaId}（版本 ${version}）`);
      await loadData();
    } catch (err: any) {
      setImportResult(`导入失败：${err.message || '未知错误'}`);
    } finally {
      setImporting(false);
    }
  };

  useEffect(() => {
    console.log('🔄 useEffect触发，开始加载数据...');
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Persona管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            构建和管理作者Persona，共 {personas.length} 个
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            导入Persona
            <input
              type="file"
              accept="application/json"
              className="hidden"
              onChange={(e) => handleImportPersona(e.target.files?.[0] || null)}
              disabled={importing}
            />
          </label>
          <select
            value={importMode}
            onChange={(e) => setImportMode(e.target.value as 'new' | 'new_version' | 'overwrite')}
            className="rounded-md border border-gray-200 text-sm"
          >
            <option value="new_version">导入为新版本</option>
            <option value="new">导入为新Persona</option>
            <option value="overwrite">覆盖同ID</option>
          </select>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {importResult && (
        <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-700">
          {importResult}
          {importFileName && (
            <span className="ml-2 text-xs text-blue-500">({importFileName})</span>
          )}
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
                  {persona.version && (
                    <p className="text-xs text-gray-400">版本 {persona.version}</p>
                  )}
                </div>
              </div>
            </div>

                    <div className="space-y-1 mb-3">
                      <p className="text-xs text-gray-600">
                        思维方式: <span className="font-medium">{persona.thinking_style || 'N/A'}</span>
                      </p>
                      {persona.created_at && (
                        <p className="text-xs text-gray-600">
                          创建时间: <span className="font-medium">{new Date(persona.created_at).toLocaleDateString('zh-CN')}</span>
                        </p>
                      )}
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
              构建新Persona ({books.length} 本著作)
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
                            disabled={buildingPersonaId === book.book_id}
                            className={`inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md ${
                              buildingPersonaId === book.book_id
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'text-white bg-blue-600 hover:bg-blue-700'
                            }`}
                          >
                            {buildingPersonaId === book.book_id ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                构建中...
                              </>
                            ) : (
                              <>
                                <Plus className="h-4 w-4 mr-1" />
                                构建Persona
                              </>
                            )}
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
