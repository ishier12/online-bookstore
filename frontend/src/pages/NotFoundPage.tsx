import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-4">🔍</div>
      <h1 className="text-2xl font-bold text-gray-700 mb-2">页面不存在</h1>
      <p className="text-gray-400 mb-6">你要找的页面可能已被移除或地址错误</p>
      <Link
        to="/"
        className="inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
      >
        返回首页
      </Link>
    </div>
  );
}
