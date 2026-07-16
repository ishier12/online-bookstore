import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getBooks } from '../api/books';
import type { Book } from '../types';
import BookGrid from '../components/books/BookGrid';
import BookSearch from '../components/books/BookSearch';
import Pagination from '../components/common/Pagination';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { DEFAULT_PAGE_SIZE } from '../utils/constants';

export default function BookListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 筛选状态（从 URL 参数初始化）
  const [keyword, setKeyword] = useState(searchParams.get('keyword') || '');
  const [categoryId, setCategoryId] = useState<number | undefined>(
    searchParams.get('category_id') ? Number(searchParams.get('category_id')) : undefined
  );
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [sort, setSort] = useState(searchParams.get('sort') || 'created_at_desc');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params: Record<string, any> = {
        page,
        page_size: DEFAULT_PAGE_SIZE,
        sort,
      };
      if (keyword.trim()) params.keyword = keyword.trim();
      if (categoryId) params.category_id = categoryId;
      if (minPrice) params.min_price = Number(minPrice);
      if (maxPrice) params.max_price = Number(maxPrice);

      const data = await getBooks(params);
      setBooks(data.items);
      setTotal(data.total);

      // 同步 URL 参数
      const sp = new URLSearchParams();
      if (keyword.trim()) sp.set('keyword', keyword.trim());
      if (categoryId) sp.set('category_id', String(categoryId));
      if (minPrice) sp.set('min_price', minPrice);
      if (maxPrice) sp.set('max_price', maxPrice);
      if (sort !== 'created_at_desc') sp.set('sort', sort);
      if (page > 1) sp.set('page', String(page));
      setSearchParams(sp, { replace: true });
    } catch (err: any) {
      setError(err?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [keyword, categoryId, minPrice, maxPrice, sort, page]);

  useEffect(() => {
    fetchBooks();
  }, [page]); // 页码变化时重新请求

  const handleSearch = () => {
    setPage(1);
    fetchBooks();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-4">书籍列表</h1>

      <BookSearch
        keyword={keyword}
        categoryId={categoryId}
        minPrice={minPrice}
        maxPrice={maxPrice}
        sort={sort}
        onKeywordChange={setKeyword}
        onCategoryChange={setCategoryId}
        onPriceChange={(min, max) => { setMinPrice(min); setMaxPrice(max); }}
        onSortChange={setSort}
        onSearch={handleSearch}
      />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchBooks} />
      ) : books.length === 0 ? (
        <EmptyState title="没有找到相关书籍" description="试试调整筛选条件" />
      ) : (
        <>
          <p className="text-sm text-gray-400 mb-4">共 {total} 本</p>
          <BookGrid books={books} />
          <Pagination
            page={page}
            pageSize={DEFAULT_PAGE_SIZE}
            total={total}
            onChange={setPage}
          />
        </>
      )}
    </div>
  );
}
