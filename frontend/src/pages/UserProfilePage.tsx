import { useAuth } from '../context/AuthContext';
import { formatDate } from '../utils/format';

export default function UserProfilePage() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <div className="max-w-md mx-auto mt-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
        <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
          {user.nickname?.[0] || user.username[0]}
        </div>
        <h1 className="text-xl font-semibold text-gray-800">
          {user.nickname || user.username}
        </h1>
        <p className="text-sm text-gray-400 mt-1">@{user.username}</p>
        <p className="text-sm text-gray-400">{user.email}</p>
        <p className="text-xs text-gray-300 mt-3">
          注册时间：{formatDate(user.created_at)}
        </p>
        <button
          onClick={logout}
          className="mt-6 px-6 py-2 bg-red-50 text-red-500 rounded-lg text-sm hover:bg-red-100"
        >
          退出登录
        </button>
      </div>
    </div>
  );
}
