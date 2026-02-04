// 最小化的Persona列表 - 用于排查Tauri问题
import { useState } from 'react';

export default function PersonaListMinimal() {
  const [message, setMessage] = useState('');

  const handleClick = () => {
    console.log('🎯 最小化版本按钮点击！');
    setMessage('按钮点击成功！');
    alert('最小化Persona页面：按钮工作正常！');
  };

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">最小化Persona页面</h1>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-800">{message || '暂无消息'}</p>
      </div>

      <button
        onClick={handleClick}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
      >
        🔵 点击测试按钮
      </button>

      <p className="text-sm text-gray-600">
        如果这个按钮工作，说明问题在原PersonaList组件的某个特定代码中。
      </p>
    </div>
  );
}
