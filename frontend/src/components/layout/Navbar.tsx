import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim()) {
      navigate(`/books?keyword=${encodeURIComponent(keyword.trim())}`);
    }
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="text-xl font-bold text-indigo-600 hover:text-indigo-700">
          📚 在线书店
        </Link>

        {/* 搜索栏 */}
        <form onSubmit={handleSearch} className="flex-1 max-w-md mx-6">
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="搜索书名、作者..."
            className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </form>

        {/* 右侧 */}
        <div className="flex items-center gap-4 text-sm">
          <Link to="/books" className="text-gray-600 hover:text-indigo-600">
            所有书籍
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="text-gray-600 hover:text-indigo-600">
                {user?.nickname || user?.username}
              </Link>
              <button onClick={logout} className="text-gray-400 hover:text-red-500">
                退出
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-600 hover:text-indigo-600">
                登录
              </Link>
              <Link
                to="/register"
                className="bg-indigo-600 text-white px-3 py-1 rounded-lg hover:bg-indigo-700"
              >
                注册
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
