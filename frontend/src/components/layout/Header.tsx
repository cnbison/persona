// 顶部栏组件
import { Menu } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="lg:hidden text-gray-500 hover:text-gray-700"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Title */}
      <h2 className="text-lg font-semibold text-gray-900">
        AI著作跨时空对话播客
      </h2>

      {/* Right side - can add user info, etc. */}
      <div className="flex items-center space-x-4">
        {/* Placeholder for future features */}
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
          U
        </div>
      </div>
    </header>
  );
}
