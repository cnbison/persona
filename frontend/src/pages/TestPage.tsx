// 测试页面 - 用于诊断Tauri按钮问题
import { useState } from 'react';

export default function TestPage() {
  const [clickCount, setClickCount] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev]);
  };

  const handleBasicClick = () => {
    setClickCount(prev => prev + 1);
    addLog(`✅ 基础按钮点击成功！计数: ${clickCount + 1}`);
  };

  const handleAlertClick = () => {
    addLog('📢 调用alert()');
    alert('Alert测试成功！');
    addLog('✅ Alert已关闭');
  };

  const handleConfirmClick = () => {
    addLog('❓ 调用confirm()');
    const result = confirm('请点击"确定"或"取消"');
    addLog(`✅ Confirm返回: ${result}`);
  };

  const handleAsyncClick = async () => {
    addLog('🔄 开始异步操作...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    addLog('✅ 异步操作完成！');
    alert('异步操作完成！');
  };

  const handleFetchClick = async () => {
    addLog('📡 开始API请求...');
    try {
      const response = await fetch('http://localhost:8000/api/health');
      addLog(`✅ 响应状态: ${response.status}`);
      const data = await response.json();
      addLog(`✅ 响应数据: ${JSON.stringify(data)}`);
      alert(`API请求成功！状态: ${response.status}`);
    } catch (error: any) {
      addLog(`❌ API请求失败: ${error.message}`);
      alert(`API请求失败: ${error.message}`);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">🧪 Tauri按钮测试页面</h1>

      {/* 统计信息 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-lg font-semibold text-blue-900">
          点击次数: <span className="text-blue-600">{clickCount}</span>
        </p>
      </div>

      {/* 日志区域 */}
      <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto">
        <h2 className="text-white font-semibold mb-2">📋 事件日志</h2>
        {logs.length === 0 ? (
          <p className="text-gray-500">暂无日志</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, index) => (
              <p key={index} className="text-green-400 text-sm font-mono">
                {log}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* 测试按钮组 */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">测试按钮</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 基础点击 */}
          <button
            onClick={handleBasicClick}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            🔵 基础点击测试
          </button>

          {/* Alert */}
          <button
            onClick={handleAlertClick}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
          >
            📢 Alert测试
          </button>

          {/* Confirm */}
          <button
            onClick={handleConfirmClick}
            className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-semibold"
          >
            ❓ Confirm测试
          </button>

          {/* 异步操作 */}
          <button
            onClick={handleAsyncClick}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
          >
            🔄 异步操作测试
          </button>

          {/* API请求 */}
          <button
            onClick={handleFetchClick}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold md:col-span-2"
          >
            📡 API请求测试
          </button>
        </div>
      </div>

      {/* 清除日志按钮 */}
      <button
        onClick={() => {
          setLogs([]);
          setClickCount(0);
        }}
        className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold"
      >
        🗑️ 清除日志和计数
      </button>
    </div>
  );
}
