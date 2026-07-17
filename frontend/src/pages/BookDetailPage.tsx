import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getBook } from '../api/books';
import { getReviews, createReview } from '../api/reviews';
import { useAuth } from '../context/AuthContext';
import type { BookDetail, Review } from '../types';
import StarRating from '../components/common/StarRating';
import ReviewList from '../components/reviews/ReviewList';
import ReviewForm from '../components/reviews/ReviewForm';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import Pagination from '../components/common/Pagination';
import { formatPrice, formatDate } from '../utils/format';

export default function BookDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();

  const [book, setBook] = useState<BookDetail | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewTotal, setReviewTotal] = useState(0);
  const [reviewPage, setReviewPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchBook = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError('');
    try {
      const data = await getBook(Number(id));
      setBook(data);
    } catch (err: any) {
      setError(err?.detail || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const fetchReviews = useCallback(async () => {
    if (!id) return;
    try {
      const data = await getReviews(Number(id), reviewPage);
      setReviews(data.items);
      setReviewTotal(data.total);
    } catch {}
  }, [id, reviewPage]);

  useEffect(() => {
    fetchBook();
  }, [fetchBook]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const handleReviewSubmit = async (rating: number, content: string) => {
    if (!id) return;
    await createReview(Number(id), { rating, content });
    // 刷新书评列表和书籍数据（均分会变）
    setReviewPage(1);
    fetchBook();
  };

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} onRetry={fetchBook} />;
  if (!book) return <ErrorMessage message="书籍不存在" />;

  return (
    <div>
      {/* 书籍信息 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* 封面 */}
          <div className="w-full md:w-48 h-64 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg flex items-center justify-center text-6xl flex-shrink-0">
            📖
          </div>

          {/* 信息 */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">{book.book_name}</h1>
            <p className="text-gray-500 mb-3">{book.author} 著</p>

            <div className="flex items-center gap-3 mb-3">
              <StarRating rating={book.avg_rating ?? 0} />
              <span className="text-sm text-gray-400">({book.review_count} 条评价)</span>
            </div>

            {book.publisher && (
              <p className="text-sm text-gray-600 mb-2">
                出版社：
                <Link to={`/books?publisher_id=${book.publisher.id}`} className="text-indigo-600 hover:underline">
                  {book.publisher.name}
                </Link>
              </p>
            )}

            {book.isbn && (
              <p className="text-sm text-gray-500 mb-2">ISBN：{book.isbn}</p>
            )}

            <div className="flex items-center gap-2 mb-3">
              {book.categories.map((cat) => (
                <Link
                  key={cat.id}
                  to={`/books?category_id=${cat.id}`}
                  className="bg-indigo-50 text-indigo-600 text-xs px-2 py-0.5 rounded-full hover:bg-indigo-100 transition-colors"
                >
                  {cat.name}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-4 mt-4">
              <span className="text-3xl font-bold text-indigo-600">
                {formatPrice(book.price)}
              </span>
              {book.stock > 0 ? (
                <span className="text-sm text-green-600">有货（库存 {book.stock}）</span>
              ) : (
                <span className="text-sm text-red-400">暂时缺货</span>
              )}
            </div>

            <p className="text-xs text-gray-400 mt-3">
              上架时间：{formatDate(book.created_at)}
            </p>
          </div>
        </div>

        {/* 简介 */}
        {book.description && (
          <div className="mt-6 pt-4 border-t border-gray-100">
            <h3 className="text-sm font-medium text-gray-700 mb-2">内容简介</h3>
            <p className="text-sm text-gray-600 leading-relaxed">{book.description}</p>
          </div>
        )}
      </div>

      {/* 书评 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          书评 ({reviewTotal})
        </h2>

        {isAuthenticated ? (
          <ReviewForm onSubmit={handleReviewSubmit} />
        ) : (
          <p className="text-sm text-gray-400 py-4">
            请先<a href="/login" className="text-indigo-600 hover:underline">登录</a>后发表书评
          </p>
        )}

        <div className="mt-4">
          <ReviewList reviews={reviews} />
        </div>

        <Pagination
          page={reviewPage}
          pageSize={10}
          total={reviewTotal}
          onChange={setReviewPage}
        />
      </div>
    </div>
  );
}
