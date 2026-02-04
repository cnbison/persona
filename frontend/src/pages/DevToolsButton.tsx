// 开发者工具触发按钮
import { invoke } from '@tauri-apps/api/core';

export default function DevToolsButton() {
  const handleOpenDevTools = async () => {
    try {
      await invoke('open_devtools');
      console.log('✅ 开发者工具已打开');
    } catch (error) {
      console.error('❌ 打开开发者工具失败:', error);
    }
  };

  return (
    <button
      onClick={handleOpenDevTools}
      className="fixed top-4 right-4 z-50 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold shadow-lg"
      style={{ position: 'fixed', top: '1rem', right: '1rem', zIndex: 9999 }}
    >
      🔧 打开开发者工具
    </button>
  );
}
