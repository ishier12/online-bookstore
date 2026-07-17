import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { getBooks } from '../api/books';
import { getCategories } from '../api/categories';
import type { Book, Category } from '../types';
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
  const [publisherId, setPublisherId] = useState<number | undefined>(
    searchParams.get('publisher_id') ? Number(searchParams.get('publisher_id')) : undefined
  );
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [sort, setSort] = useState(searchParams.get('sort') || 'created_at_desc');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
  const [categories, setCategories] = useState<Category[]>([]);

  // 找到当前筛选的分类名（用于顶部提示）
  const currentCategoryName = (() => {
    if (!categoryId) return null;
    for (const cat of categories) {
      if (cat.id === categoryId) return cat.name;
      for (const child of cat.children || []) {
        if (child.id === categoryId) return `${cat.name} / ${child.name}`;
      }
    }
    return null;
  })();

  // 加载分类列表（用于显示当前分类名）
  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
  }, []);

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
      if (publisherId) params.publisher_id = publisherId;
      if (minPrice) params.min_price = Number(minPrice);
      if (maxPrice) params.max_price = Number(maxPrice);

      const data = await getBooks(params);
      setBooks(data.items);
      setTotal(data.total);

      // 同步 URL 参数
      const sp = new URLSearchParams();
      if (keyword.trim()) sp.set('keyword', keyword.trim());
      if (categoryId) sp.set('category_id', String(categoryId));
      if (publisherId) sp.set('publisher_id', String(publisherId));
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
  }, [keyword, categoryId, publisherId, minPrice, maxPrice, sort, page]);

  // URL 参数变化时自动查询（支持浏览器前进后退 + 从详情页跳转带参数）
  useEffect(() => {
    fetchBooks();
  }, [page]);

  const handleSearch = () => {
    setPage(1);
    fetchBooks();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-4">书籍列表</h1>

      {/* 当前筛选提示 */}
      {(currentCategoryName || publisherId) && (
        <div className="flex items-center gap-2 mb-4 text-sm">
          <span className="text-gray-500">当前筛选：</span>
          {currentCategoryName && (
            <span className="bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full">
              📂 {currentCategoryName}
            </span>
          )}
          {publisherId && (
            <span className="bg-purple-50 text-purple-600 px-3 py-1 rounded-full">
              🏢 出版社 ID: {publisherId}
            </span>
          )}
          <Link to="/books" className="text-gray-400 hover:text-red-500 ml-2">
            清除筛选 ✕
          </Link>
        </div>
      )}

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
