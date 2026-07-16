import { Link } from 'react-router-dom';
import type { Book } from '../../types';
import { formatPrice } from '../../utils/format';

interface Props {
  book: Book;
}

export default function BookCard({ book }: Props) {
  return (
    <Link
      to={`/books/${book.id}`}
      className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-200"
    >
      {/* 封面占位 */}
      <div className="h-40 bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center text-4xl">
        📖
      </div>
      <div className="p-3">
        <h3 className="font-medium text-sm text-gray-900 leading-tight line-clamp-1">
          {book.book_name}
        </h3>
        <p className="text-xs text-gray-500 mt-1">{book.author}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-indigo-600 font-semibold text-sm">
            {formatPrice(book.price)}
          </span>
          {book.stock === 0 && (
            <span className="text-xs text-red-400">缺货</span>
          )}
        </div>
      </div>
    </Link>
  );
}
