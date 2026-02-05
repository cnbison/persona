// 证据检索页面
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, BookOpen } from 'lucide-react';
import { evidenceApi } from '../../services/evidence';

interface EvidenceItem {
  evidence_id: string;
  book_id: string;
  chapter_id: string;
  chapter_title?: string | null;
  paragraph_id?: string | null;
  paragraph_number?: number | null;
  viewpoint_id?: string | null;
  evidence_text: string;
  context_before?: string | null;
  context_after?: string | null;
  keywords?: string[];
  score?: number;
}

export default function EvidenceSearch() {
  const [keyword, setKeyword] = useState('');
  const [bookId, setBookId] = useState('');
  const [chapterId, setChapterId] = useState('');
  const [viewpointId, setViewpointId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<EvidenceItem[]>([]);
  const navigate = useNavigate();

  const buildLocationQuery = (item: EvidenceItem) => {
    const params = new URLSearchParams();
    if (item.chapter_id) params.set('chapter_id', item.chapter_id);
    if (item.paragraph_id) params.set('paragraph_id', item.paragraph_id);
    if (item.paragraph_number) params.set('paragraph_number', String(item.paragraph_number));
    return params.toString();
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await evidenceApi.searchEvidence({
        keyword: keyword || undefined,
        book_id: bookId || undefined,
        chapter_id: chapterId || undefined,
        viewpoint_id: viewpointId || undefined,
      });
      setResults(response?.data?.items || []);
    } catch (err: any) {
      setError(err.message || '检索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">证据检索</h1>
        <p className="mt-1 text-sm text-gray-600">按关键词/书籍/章节检索证据片段</p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <label className="text-sm text-gray-600">
            关键词
            <input
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            书籍ID
            <input
              value={bookId}
              onChange={(e) => setBookId(e.target.value)}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            章节ID
            <input
              value={chapterId}
              onChange={(e) => setChapterId(e.target.value)}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            观点ID
            <input
              value={viewpointId}
              onChange={(e) => setViewpointId(e.target.value)}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            <Search className="w-4 h-4 mr-2" />
            {loading ? '检索中...' : '开始检索'}
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">检索结果</h2>
        {results.length === 0 ? (
          <div className="text-sm text-gray-500">暂无结果</div>
        ) : (
          <div className="space-y-4">
            {results.map((item) => (
              <div key={item.evidence_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    <span>
                      {item.chapter_title ? item.chapter_title : '章节'} ({item.chapter_id})
                    </span>
                    {item.paragraph_number && (
                      <span>段落 #{item.paragraph_number}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span>Score: {item.score ?? 1.0}</span>
                    <button
                      onClick={() => {
                        if (!item.book_id || !item.chapter_id) return;
                        const query = buildLocationQuery(item);
                        navigate(`/books/${item.book_id}${query ? `?${query}` : ''}`);
                      }}
                      disabled={!item.book_id || !item.chapter_id}
                      className="inline-flex items-center rounded-md border border-blue-200 px-2 py-1 text-xs text-blue-700 hover:bg-blue-50 disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      定位章节
                    </button>
                  </div>
                </div>
                <p className="mt-2 text-sm text-gray-900 whitespace-pre-wrap">{item.evidence_text}</p>
                {item.context_before && (
                  <p className="mt-2 text-xs text-gray-500">前文：{item.context_before}</p>
                )}
                {item.context_after && (
                  <p className="mt-2 text-xs text-gray-500">后文：{item.context_after}</p>
                )}
                {item.keywords && item.keywords.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {item.keywords.map((kw, idx) => (
                      <span key={idx} className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
