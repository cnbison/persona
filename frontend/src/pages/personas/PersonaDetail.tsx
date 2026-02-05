// Persona详情页面
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Brain, BookOpen, MessageSquare, Heart, Sparkles } from 'lucide-react';
import { personasApi } from '../../services/personas';
import { personaExportApi } from '../../services/personaExport';
import type { AuthorPersona } from '../../types/persona';

export default function PersonaDetail() {
  const { personaId } = useParams<{ personaId: string }>();
  const navigate = useNavigate();

  const [persona, setPersona] = useState<AuthorPersona | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);
  const [generatingPrompt, setGeneratingPrompt] = useState(false);
  const [promptSuccess, setPromptSuccess] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (personaId) {
      loadPersonaDetail();
    }
  }, [personaId]);

  const loadPersonaDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await personasApi.getPersona(personaId);
      setPersona(response.data);

      // 如果已经有system_prompt，显示出来
      if (response.data.system_prompt) {
        setSystemPrompt(response.data.system_prompt);
        setPromptSuccess(true);
      }
    } catch (err: any) {
      setError(err.message || '加载失败');
      console.error('加载Persona详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePrompt = async () => {
    try {
      setGeneratingPrompt(true);
      setPromptSuccess(false);

      const response = await personasApi.generateSystemPrompt(personaId);
      setSystemPrompt(response.data.system_prompt);
      setPromptSuccess(true);

      console.log('✅ System Prompt生成成功！');

      // 3秒后清除loading状态
      setTimeout(() => {
        setGeneratingPrompt(false);
      }, 2000);
    } catch (err: any) {
      console.error('生成System Prompt失败:', err);
      setGeneratingPrompt(false);
      alert(`生成失败: ${err.message || '未知错误'}`);
    }
  };

  const handleExport = async () => {
    if (!personaId) return;
    try {
      setExporting(true);
      const response = await personaExportApi.exportPersona(personaId);
      const payload = response.data;
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `persona-${personaId}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`导出失败: ${err.message || '未知错误'}`);
    } finally {
      setExporting(false);
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

  if (error || !persona) {
    return (
      <div className="text-center py-12 bg-red-50 rounded-lg">
        <p className="text-red-800">{error || 'Persona不存在'}</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          返回
        </button>
      </div>
    );
  }

  // 6个维度的配置
  const dimensions = [
    {
      name: '思维方式',
      icon: Brain,
      color: 'bg-blue-500',
      fields: [
        { label: '思维风格', value: persona.thinking_style },
        { label: '逻辑模式', value: persona.logic_pattern },
        { label: '推理框架', value: persona.reasoning_framework },
      ],
    },
    {
      name: '哲学体系',
      icon: Sparkles,
      color: 'bg-purple-500',
      fields: [
        { label: '核心哲学', value: persona.core_philosophy },
        { label: '理论框架', value: persona.theoretical_framework },
      ],
    },
    {
      name: '叙事风格',
      icon: BookOpen,
      color: 'bg-green-500',
      fields: [
        { label: '叙事方式', value: persona.narrative_style },
        { label: '语言节奏', value: persona.language_rhythm },
        {
          label: '修辞手法',
          value: (persona.rhetorical_devices || []).join('、'),
        },
      ],
    },
    {
      name: '价值观',
      icon: Heart,
      color: 'bg-red-500',
      fields: [
        { label: '价值取向', value: persona.value_orientation },
        { label: '判断框架', value: persona.value_judgment_framework },
        {
          label: '核心立场',
          value: (persona.core_positions || []).join(', '),
        },
      ],
    },
    {
      name: '语气性格',
      icon: MessageSquare,
      color: 'bg-yellow-500',
      fields: [
        { label: '语气', value: persona.tone },
        { label: '情感倾向', value: persona.emotion_tendency },
        {
          label: '性格特征',
          value: (persona.personality_traits || []).join('、'),
        },
        { label: '沟通风格', value: persona.communication_style },
      ],
    },
  ];

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

      {/* Persona基本信息 */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
              <User className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <h1 className="text-3xl font-bold text-gray-900">{persona.author_name}</h1>
              <p className="mt-1 text-lg text-gray-600">
                ID: {persona.persona_id.slice(0, 12)}...
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              disabled={exporting}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              {exporting ? '导出中...' : '导出JSON'}
            </button>
            <button
              onClick={handleGeneratePrompt}
              disabled={generatingPrompt || promptSuccess}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md ${
                generatingPrompt
                  ? 'bg-gray-400 cursor-not-allowed'
                  : promptSuccess
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'text-white bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {generatingPrompt ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  生成中...
                </>
              ) : promptSuccess ? (
                <>
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  已生成并保存
                </>
              ) : (
                <>生成System Prompt</>
              )}
            </button>
          </div>
        </div>

        {/* 成功提示 */}
        {promptSuccess && (
          <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex">
              <svg className="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <p className="text-sm text-green-800 font-medium">System Prompt已生成并保存到数据库</p>
                <p className="text-sm text-green-700 mt-1">后续生成对话脚本时会自动使用此提示词</p>
              </div>
            </div>
          </div>
        )}

        {persona.era && (
          <div className="flex gap-2 mb-4">
            <span className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-800">
              {persona.era}
            </span>
            {persona.identity && (
              <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                {persona.identity}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Persona卡片 */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Persona卡片</h3>
            <p className="text-sm text-gray-500 mt-1">用于快速校准与复用</p>
          </div>
          <span className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
            版本 {persona.version || '1.0'}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            <div>
              <p className="text-xs text-gray-500 mb-1">一句话画像</p>
              <p className="text-sm text-gray-900">
                {persona.core_philosophy || '暂无核心哲学摘要'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">风格摘要</p>
              <p className="text-sm text-gray-900">
                {[
                  persona.thinking_style && `思维方式：${persona.thinking_style}`,
                  persona.narrative_style && `叙事：${persona.narrative_style}`,
                  persona.tone && `语气：${persona.tone}`,
                ]
                  .filter(Boolean)
                  .join(' · ') || '暂无风格摘要'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">边界提示</p>
              <p className="text-sm text-gray-900">
                {persona.opposed_positions && persona.opposed_positions.length > 0
                  ? `避免主张：${persona.opposed_positions.join('、')}`
                  : '暂无明确边界提示'}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-500 mb-1">核心立场</p>
              <p className="text-sm text-gray-900">
                {(persona.core_positions || []).slice(0, 4).join('、') || '暂无'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">关键概念</p>
              <p className="text-sm text-gray-900">
                {Object.keys(persona.key_concepts || {}).length > 0
                  ? Object.keys(persona.key_concepts || {}).slice(0, 4).join('、')
                  : '暂无'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">证据链接</p>
              <p className="text-sm text-gray-900">
                {(persona.evidence_links || []).length > 0
                  ? persona.evidence_links.join('、')
                  : '暂无（待接入证据库）'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 6维度可视化 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dimensions.map((dimension) => (
          <div
            key={dimension.name}
            className="bg-white shadow rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center mb-4">
              <div className={`flex-shrink-0 h-10 w-10 rounded-full ${dimension.color} flex items-center justify-center`}>
                <dimension.icon className="h-5 w-5 text-white" />
              </div>
              <h3 className="ml-3 text-lg font-semibold text-gray-900">{dimension.name}</h3>
            </div>

            <div className="space-y-3">
              {dimension.fields.map((field) => (
                <div key={field.label}>
                  <p className="text-xs text-gray-500 mb-1">{field.label}</p>
                  <p className="text-sm text-gray-900">{field.value}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* 关键概念 */}
      {Object.keys(persona.key_concepts).length > 0 && (
        <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">关键概念</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(persona.key_concepts).map(([concept, definition]) => (
              <div key={concept} className="border border-gray-200 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900 mb-1">{concept}</p>
                <p className="text-xs text-gray-600">{definition}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Prompt显示 */}
      {systemPrompt && (
        <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">System Prompt</h3>
              <p className="text-sm text-gray-500 mt-1">
                ✅ 已保存到数据库，后续生成对话时自动使用
              </p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(systemPrompt);
                console.log('✅ System Prompt已复制到剪贴板');
              }}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              复制
            </button>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {systemPrompt}
            </pre>
          </div>
        </div>
      )}

      {/* 额外信息 */}
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">详细信息</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">句子结构</p>
            <p className="text-sm text-gray-900">{persona.sentence_structure}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1">表达性</p>
            <p className="text-sm text-gray-900">{persona.expressiveness}</p>
          </div>

          <div className="md:col-span-2">
            <p className="text-sm text-gray-500 mb-1">对受众态度</p>
            <p className="text-sm text-gray-900">{persona.attitude_toward_audience}</p>
          </div>

          {persona.opposed_positions && persona.opposed_positions.length > 0 && (
            <div className="md:col-span-2">
              <p className="text-sm text-gray-500 mb-1">反对立场</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {persona.opposed_positions.map((position, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center rounded-full bg-red-50 px-3 py-1 text-sm font-medium text-red-700"
                  >
                    {position}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
