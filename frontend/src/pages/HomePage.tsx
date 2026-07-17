import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBooks } from '../api/books';
import { getCategories } from '../api/categories';
import type { Book, Category } from '../types';
import BookGrid from '../components/books/BookGrid';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export default function HomePage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getBooks({ page_size: 8, sort: 'created_at_desc' }),
      getCategories(),
    ])
      .then(([bookData, catData]) => {
        setBooks(bookData.items);
        setCategories(catData);
      })
      .catch((err) => setError(err?.message || '加载失败'))
      .finally(() => setLoading(false));
  }, []);

  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;

  return (
    <div>
      {/* Hero */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-8 mb-8 text-white">
        <h1 className="text-3xl font-bold mb-2">📚 发现你的下一本好书</h1>
        <p className="text-indigo-100">文学、社科、经管、科技——总有你感兴趣的</p>
        <Link
          to="/books"
          className="inline-block mt-4 bg-white text-indigo-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-50"
        >
          浏览全部 →
        </Link>
      </div>

      {/* 分类浏览 */}
      {categories.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">分类浏览</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            {categories.map((cat) => (
              <Link
                key={cat.id}
                to={`/books?category_id=${cat.id}`}
                className="bg-white border border-gray-200 rounded-xl p-4 text-center hover:border-indigo-300 hover:shadow-sm transition-all"
              >
                <div className="text-2xl mb-1">
                  {cat.name === '文学小说' ? '📖' :
                   cat.name === '人文社科' ? '🏛️' :
                   cat.name === '经济管理' ? '📊' :
                   cat.name === '科学技术' ? '🔬' :
                   cat.name === '生活休闲' ? '🌿' :
                   cat.name === '艺术设计' ? '🎨' : '📚'}
                </div>
                <div className="text-sm font-medium text-gray-700">{cat.name}</div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* 最新上架 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">最新上架</h2>
          <Link to="/books" className="text-sm text-indigo-600 hover:underline">
            查看更多 →
          </Link>
        </div>
        {loading ? <Loading /> : <BookGrid books={books} />}
      </div>
    </div>
  );
}
