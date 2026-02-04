// 输出Diff对比页面
import { useState } from 'react';
import { diffApi } from '../../services/diff';

interface DiffPiece {
  text: string;
  type: 'equal' | 'replace' | 'delete' | 'insert';
}

const defaultForm = {
  a_text: '',
  b_text: '',
};

export default function DiffView() {
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [diffA, setDiffA] = useState<DiffPiece[]>([]);
  const [diffB, setDiffB] = useState<DiffPiece[]>([]);

  const buildPieces = (
    aText: string,
    bText: string,
    opcodes: Array<{ tag: string; a_start: number; a_end: number; b_start: number; b_end: number }>
  ) => {
    const aPieces: DiffPiece[] = [];
    const bPieces: DiffPiece[] = [];

    opcodes.forEach((op) => {
      const aPart = aText.slice(op.a_start, op.a_end);
      const bPart = bText.slice(op.b_start, op.b_end);

      if (op.tag === 'equal') {
        aPieces.push({ text: aPart, type: 'equal' });
        bPieces.push({ text: bPart, type: 'equal' });
      } else if (op.tag === 'replace') {
        aPieces.push({ text: aPart, type: 'delete' });
        bPieces.push({ text: bPart, type: 'insert' });
      } else if (op.tag === 'delete') {
        aPieces.push({ text: aPart, type: 'delete' });
      } else if (op.tag === 'insert') {
        bPieces.push({ text: bPart, type: 'insert' });
      }
    });

    setDiffA(aPieces);
    setDiffB(bPieces);
  };

  const handleDiff = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await diffApi.diffByText({
        a_text: form.a_text,
        b_text: form.b_text,
      });
      const data = response.data;
      buildPieces(form.a_text, form.b_text, data.opcodes || []);
    } catch (err: any) {
      setError(err.message || '对比失败');
    } finally {
      setLoading(false);
    }
  };

  const renderPieces = (pieces: DiffPiece[]) =>
    pieces.map((piece, index) => {
      let className = 'text-gray-800';
      if (piece.type === 'insert') className = 'bg-green-100 text-green-900';
      if (piece.type === 'delete') className = 'bg-red-100 text-red-900 line-through';
      return (
        <span key={index} className={`whitespace-pre-wrap ${className}`}>
          {piece.text}
        </span>
      );
    });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Diff 对比</h1>
        <p className="mt-1 text-sm text-gray-600">对比两段文本的差异</p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white shadow rounded-lg border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="text-sm text-gray-600">
            文本A
            <textarea
              rows={6}
              value={form.a_text}
              onChange={(e) => setForm({ ...form, a_text: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
          <label className="text-sm text-gray-600">
            文本B
            <textarea
              rows={6}
              value={form.b_text}
              onChange={(e) => setForm({ ...form, b_text: e.target.value })}
              className="mt-1 w-full rounded-md border-gray-200 text-sm"
            />
          </label>
        </div>
        <div className="flex justify-end">
          <button
            onClick={handleDiff}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? '对比中...' : '生成Diff'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white shadow rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-2">文本A</h2>
          <div className="text-sm text-gray-800 whitespace-pre-wrap">
            {renderPieces(diffA)}
          </div>
        </div>
        <div className="bg-white shadow rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-2">文本B</h2>
          <div className="text-sm text-gray-800 whitespace-pre-wrap">
            {renderPieces(diffB)}
          </div>
        </div>
      </div>
    </div>
  );
}
