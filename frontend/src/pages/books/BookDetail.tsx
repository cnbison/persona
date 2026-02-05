// 著作详情页面
import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, User, FileText, BookOpen } from 'lucide-react';
import { booksApi } from '../../services/books';
import { evidenceApi } from '../../services/evidence';
import type { BookDetail as BookDetailType } from '../../types/book';

interface ParagraphItem {
  paragraph_id: string;
  chapter_id: string;
  paragraph_number: number;
  content: string;
  word_count: number;
}

export default function BookDetail() {
  const { bookId } = useParams<{ bookId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [book, setBook] = useState<BookDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [displayedViewpoints, setDisplayedViewpoints] = useState(10);
  const [buildingEvidence, setBuildingEvidence] = useState(false);
  const [selectedChapterId, setSelectedChapterId] = useState<string | null>(null);
  const [selectedParagraphId, setSelectedParagraphId] = useState<string | null>(null);
  const [selectedParagraphNumber, setSelectedParagraphNumber] = useState<number | null>(null);
  const [paragraphs, setParagraphs] = useState<ParagraphItem[]>([]);
  const [paragraphsLoading, setParagraphsLoading] = useState(false);
  const [paragraphsError, setParagraphsError] = useState<string | null>(null);
  const [parseStats, setParseStats] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    if (bookId) {
      loadBookDetail();
    }
  }, [bookId]);

  useEffect(() => {
    const chapterId = searchParams.get('chapter_id');
    const paragraphId = searchParams.get('paragraph_id');
    const paragraphNumberParam = searchParams.get('paragraph_number');
    setSelectedChapterId(chapterId);
    setSelectedParagraphId(paragraphId);
    setSelectedParagraphNumber(paragraphNumberParam ? Number(paragraphNumberParam) : null);
    if (chapterId) {
      loadParagraphs(chapterId);
    }
  }, [searchParams]);

  const loadBookDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await booksApi.getBook(bookId);
      setBook(response.data);
      setParseStats(response.data?.parse_stats || null);
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

  const loadParagraphs = async (chapterId: string) => {
    try {
      setParagraphsLoading(true);
      setParagraphsError(null);
      const response = await evidenceApi.listParagraphs(chapterId);
      const items = response?.data?.items || [];
      const sorted = [...items].sort((a, b) => a.paragraph_number - b.paragraph_number);
      setParagraphs(sorted);
    } catch (err: any) {
      setParagraphsError(err.message || '段落加载失败');
    } finally {
      setParagraphsLoading(false);
    }
  };

  const handleSelectChapter = (chapterId: string, paragraphId?: string, paragraphNumber?: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('chapter_id', chapterId);
    if (paragraphId) {
      params.set('paragraph_id', paragraphId);
    } else {
      params.delete('paragraph_id');
    }
    if (paragraphNumber) {
      params.set('paragraph_number', String(paragraphNumber));
    } else {
      params.delete('paragraph_number');
    }
    setSearchParams(params);
  };

  const handleClearLocation = () => {
    const params = new URLSearchParams(searchParams);
    params.delete('chapter_id');
    params.delete('paragraph_id');
    params.delete('paragraph_number');
    setSearchParams(params);
    setSelectedChapterId(null);
    setSelectedParagraphId(null);
    setSelectedParagraphNumber(null);
    setParagraphs([]);
  };

  useEffect(() => {
    if (!paragraphs.length) return;
    if (!selectedParagraphId && !selectedParagraphNumber) return;
    const targetById = selectedParagraphId
      ? document.getElementById(`paragraph-${selectedParagraphId}`)
      : null;
    if (targetById) {
      targetById.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    if (selectedParagraphNumber) {
      const targetByNumber = document.querySelector(`[data-paragraph-number="${selectedParagraphNumber}"]`);
      if (targetByNumber) {
        (targetByNumber as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [paragraphs, selectedParagraphId, selectedParagraphNumber]);

  const selectedChapterTitle = useMemo(() => {
    if (!book || !selectedChapterId) return null;
    const chapter = book.chapters.find((item) => item.chapter_id === selectedChapterId);
    return chapter?.title ?? null;
  }, [book, selectedChapterId]);

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

        {parseStats && (
          <div className="mt-4 rounded-lg border border-gray-200 bg-gray-50 p-4 text-xs text-gray-700">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-800">解析统计</span>
              <span className="text-gray-500">
                章节识别策略：{parseStats.chapter_detection?.strategy || 'unknown'}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2">
              <div>原始字符数：{parseStats.raw_chars ?? '-'}</div>
              <div>清洗后字符数：{parseStats.cleaned_chars ?? '-'}</div>
              <div>原始行数：{parseStats.raw_lines ?? '-'}</div>
              <div>清洗后行数：{parseStats.cleaned_lines ?? '-'}</div>
              <div>章节命中数：{parseStats.chapters_detected ?? '-'}</div>
              <div>匹配标题数：{parseStats.chapter_detection?.patterns_matched ?? '-'}</div>
            </div>
          </div>
        )}

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
                  <td className="px-4 py-3 text-sm text-gray-900">
                    <button
                      onClick={() => handleSelectChapter(chapter.chapter_id)}
                      className="text-left text-blue-600 hover:underline"
                    >
                      {chapter.title}
                    </button>
                  </td>
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

      {/* 章节段落定位 */}
      {selectedChapterId && (
        <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">章节段落视图</h2>
              <p className="mt-1 text-sm text-gray-600">
                {selectedChapterTitle ? selectedChapterTitle : '章节'} ({selectedChapterId})
              </p>
            </div>
            <button
              onClick={handleClearLocation}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              清除定位
            </button>
          </div>

          {paragraphsError && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-800">
              {paragraphsError}
            </div>
          )}

          {paragraphsLoading ? (
            <div className="mt-6 text-center text-sm text-gray-500">段落加载中...</div>
          ) : (
            <div className="mt-6 space-y-4">
              {paragraphs.length === 0 ? (
                <div className="text-sm text-gray-500">
                  暂无段落信息，请先点击上方“构建证据库”生成段落索引。
                </div>
              ) : (
                paragraphs.map((paragraph) => {
                  const highlighted =
                    (selectedParagraphId && paragraph.paragraph_id === selectedParagraphId) ||
                    (selectedParagraphNumber && paragraph.paragraph_number === selectedParagraphNumber);
                  return (
                    <div
                      key={paragraph.paragraph_id}
                      id={`paragraph-${paragraph.paragraph_id}`}
                      data-paragraph-number={paragraph.paragraph_number}
                      className={`rounded-lg border px-4 py-3 ${highlighted ? 'border-blue-400 bg-blue-50' : 'border-gray-200'}`}
                    >
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>段落 #{paragraph.paragraph_number}</span>
                        <span>{paragraph.word_count.toLocaleString()} 字</span>
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-sm text-gray-900">
                        {paragraph.content}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      )}

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
