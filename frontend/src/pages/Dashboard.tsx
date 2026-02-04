// Dashboard仪表板页面
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Users, FileText, Mic } from 'lucide-react';
import { booksApi } from '../services/books';
import { personasApi } from '../services/personas';
import { outlinesApi } from '../services/outlines';
import { scriptsApi } from '../services/scripts';

interface Stats {
  books: number;
  personas: number;
  outlines: number;
  scripts: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    books: 0,
    personas: 0,
    outlines: 0,
    scripts: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);

      // 获取著作数量
      const booksResponse = await booksApi.getBooks(0, 1);
      const booksCount = booksResponse.data.total || 0;

      // 获取Persona数量
      const personasResponse = await personasApi.listPersonas(0, 1);
      const personasCount = personasResponse.data.total || 0;

      // 获取提纲数量
      const outlinesResponse = await outlinesApi.listOutlines(0, 1);
      const outlinesCount = outlinesResponse.data.total || 0;

      // 获取脚本数量
      const scriptsResponse = await scriptsApi.getScripts();
      const scriptsCount = scriptsResponse.data.total || 0;

      setStats({
        books: booksCount,
        personas: personasCount,
        outlines: outlinesCount,
        scripts: scriptsCount,
      });

      console.log('✅ 仪表板统计数据:', {
        books: booksCount,
        personas: personasCount,
        outlines: outlinesCount,
        scripts: scriptsCount,
      });
    } catch (error) {
      console.error('❌ 加载统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const statsConfig = [
    {
      name: '著作总数',
      value: loading ? '...' : stats.books.toString(),
      icon: BookOpen,
      color: 'bg-blue-500',
      description: '已上传的经典著作',
    },
    {
      name: 'Persona',
      value: loading ? '...' : stats.personas.toString(),
      icon: Users,
      color: 'bg-green-500',
      description: '已构建的作者人格',
    },
    {
      name: '提纲',
      value: loading ? '...' : stats.outlines.toString(),
      icon: FileText,
      color: 'bg-purple-500',
      description: '已生成的提纲输出',
    },
    {
      name: '脚本',
      value: loading ? '...' : stats.scripts.toString(),
      icon: Mic,
      color: 'bg-orange-500',
      description: '已生成的对话/改写',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">仪表板</h1>
        <p className="mt-1 text-sm text-gray-600">
          欢迎使用Persona生成与应用平台
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statsConfig.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:py-6 border border-gray-200"
          >
            <dt className="truncate text-sm font-medium text-gray-500">
              {stat.name}
            </dt>
            <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
              {stat.value}
            </dd>
            <p className="mt-1 text-xs text-gray-500">{stat.description}</p>
            <div className={`absolute right-4 top-4 rounded-full p-2 ${stat.color}`}>
              <stat.icon className="h-5 w-5 text-white" />
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            to="/books/upload"
            className="flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 text-center"
          >
            上传新著作
          </Link>
          <Link
            to="/personas"
            className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 text-center"
          >
            构建Persona
          </Link>
          <button
            disabled
            className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-400 bg-gray-50 cursor-not-allowed text-center"
          >
            生成提纲
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">最近活动</h2>
        {stats.books === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无活动记录，上传您的第一本著作开始吧！
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  系统已准备就绪
                </p>
                <p className="text-xs text-gray-500">现在可以开始上传著作了</p>
              </div>
              <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                就绪
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
