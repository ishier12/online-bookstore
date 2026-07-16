import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBooks } from '../api/books';
import type { Book } from '../types';
import BookGrid from '../components/books/BookGrid';
import Loading from '../components/common/Loading';

export default function HomePage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBooks({ page_size: 8, sort: 'created_at_desc' })
      .then((data) => setBooks(data.items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {/* Hero */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-8 mb-8 text-white">
        <h1 className="text-3xl font-bold mb-2">📚 发现你的下一本好书</h1>
        <p className="text-indigo-100">探索海量技术书籍，从入门到精通</p>
        <Link
          to="/books"
          className="inline-block mt-4 bg-white text-indigo-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-50"
        >
          浏览全部 →
        </Link>
      </div>

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
