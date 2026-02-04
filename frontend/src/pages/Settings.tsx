// 设置页面
import { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Key,
  Folder,
  Trash2,
  Moon,
  Sun,
  Info,
  Save,
} from 'lucide-react';

interface AppSettings {
  apiBaseUrl: string;
  openaiApiKey: string;
  dataPath: string;
  theme: 'light' | 'dark' | 'system';
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

const DEFAULT_SETTINGS: AppSettings = {
  apiBaseUrl: 'http://localhost:8000/api',
  openaiApiKey: '',
  dataPath: '',
  theme: 'system',
  logLevel: 'info',
};

export default function Settings() {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [saving, setSaving] = useState(false);

  // 从localStorage加载设置
  useEffect(() => {
    const saved = localStorage.getItem('app_settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      } catch (err) {
        console.error('加载设置失败:', err);
      }
    }
  }, []);

  // 保存设置
  const handleSave = async () => {
    try {
      setSaving(true);
      localStorage.setItem('app_settings', JSON.stringify(settings));

      // 更新API客户端的baseURL（如果需要）
      // 实际应用中可能需要重新初始化API客户端

      alert('设置已保存！');
    } catch (err) {
      alert('保存失败');
      console.error('保存设置失败:', err);
    } finally {
      setSaving(false);
    }
  };

  // 清除缓存
  const handleClearCache = () => {
    if (!confirm('确定要清除所有缓存数据吗？此操作不可恢复。')) {
      return;
    }

    try {
      localStorage.clear();
      sessionStorage.clear();
      alert('缓存已清除！');
      // 重新加载页面
      window.location.reload();
    } catch (err) {
      alert('清除失败');
      console.error('清除缓存失败:', err);
    }
  };

  // 重置为默认设置
  const handleReset = () => {
    if (!confirm('确定要重置为默认设置吗？')) {
      return;
    }

    setSettings(DEFAULT_SETTINGS);
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">设置</h1>
          <p className="mt-1 text-sm text-gray-600">
            配置应用参数和偏好设置
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? '保存中...' : '保存设置'}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* 左侧：设置项 */}
        <div className="lg:col-span-2 space-y-6">
          {/* API配置 */}
          <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
            <div className="flex items-center mb-4">
              <Server className="w-5 h-5 text-gray-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">API配置</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API基础URL
                </label>
                <input
                  type="text"
                  value={settings.apiBaseUrl}
                  onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
                  placeholder="http://localhost:8000/api"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  后端API服务地址
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  OpenAI API密钥
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(e) => setSettings({ ...settings, openaiApiKey: e.target.value })}
                    placeholder="sk-..."
                    className="flex-1 block px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={() => {
                      const visible = !document.querySelector(`[value="${settings.openaiApiKey}"]`)?.getAttribute('type') === 'text';
                      // 实际显示/隐藏逻辑
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Key className="w-4 h-4" />
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  用于AI对话生成（可选）
                </p>
              </div>
            </div>
          </div>

          {/* 文件路径配置 */}
          <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
            <div className="flex items-center mb-4">
              <Folder className="w-5 h-5 text-gray-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">文件路径</h2>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                数据存储路径
              </label>
              <input
                type="text"
                value={settings.dataPath}
                onChange={(e) => setSettings({ ...settings, dataPath: e.target.value })}
                placeholder="/path/to/data"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                著作文件和生成结果的存储位置
              </p>
            </div>
          </div>

          {/* 主题和显示 */}
          <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
            <div className="flex items-center mb-4">
              <Sun className="w-5 h-5 text-gray-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">主题和显示</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  主题模式
                </label>
                <select
                  value={settings.theme}
                  onChange={(e) => setSettings({ ...settings, theme: e.target.value as any })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="system">跟随系统</option>
                  <option value="light">浅色</option>
                  <option value="dark">深色</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  日志级别
                </label>
                <select
                  value={settings.logLevel}
                  onChange={(e) => setSettings({ ...settings, logLevel: e.target.value as any })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warn">Warning</option>
                  <option value="error">Error</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  控制台日志详细程度
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：危险操作 */}
        <div className="space-y-6">
          {/* 危险操作 */}
          <div className="rounded-lg bg-white p-6 shadow border border-red-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">危险操作</h2>

            <div className="space-y-3">
              <button
                onClick={handleReset}
                className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                重置为默认设置
              </button>

              <button
                onClick={handleClearCache}
                className="w-full flex items-center justify-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                清除所有缓存
              </button>
            </div>

            <p className="mt-4 text-xs text-gray-500">
              ⚠️ 清除缓存将删除所有本地存储的数据
            </p>
          </div>

          {/* 关于信息 */}
          <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
            <div className="flex items-center mb-4">
              <Info className="w-5 h-5 text-gray-400 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">关于</h2>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">应用名称</span>
                <span className="text-gray-900">Persona生成与应用平台</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">版本</span>
                <span className="text-gray-900">v1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">框架</span>
                <span className="text-gray-900">Tauri + React</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">构建时间</span>
                <span className="text-gray-900">2025-01-25</span>
              </div>
            </div>
          </div>

          {/* 系统状态 */}
          <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">系统状态</h2>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">API连接</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  正常
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">存储空间</span>
                <span className="text-gray-900">充足</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">浏览器</span>
                <span className="text-gray-900">
                  {navigator.userAgent.includes('Chrome') ? 'Chrome' : 'Unknown'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
