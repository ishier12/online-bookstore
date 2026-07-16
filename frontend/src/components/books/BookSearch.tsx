import { useState, useEffect } from 'react';
import type { Category } from '../../types';
import * as categoriesApi from '../../api/categories';

interface Props {
  keyword: string;
  categoryId: number | undefined;
  minPrice: string;
  maxPrice: string;
  sort: string;
  onKeywordChange: (v: string) => void;
  onCategoryChange: (v: number | undefined) => void;
  onPriceChange: (min: string, max: string) => void;
  onSortChange: (v: string) => void;
  onSearch: () => void;
}

export default function BookSearch({
  keyword,
  categoryId,
  minPrice,
  maxPrice,
  sort,
  onKeywordChange,
  onCategoryChange,
  onPriceChange,
  onSortChange,
  onSearch,
}: Props) {
  const [categories, setCategories] = useState<Category[]>([]);

  useEffect(() => {
    categoriesApi.getCategories().then(setCategories).catch(() => {});
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div className="flex flex-wrap gap-3 items-end">
        {/* 关键字 */}
        <div className="flex-1 min-w-[200px]">
          <label className="text-xs text-gray-500 mb-1 block">搜索</label>
          <input
            type="text"
            value={keyword}
            onChange={(e) => onKeywordChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
            placeholder="书名、作者..."
            className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </div>

        {/* 分类 */}
        <div>
          <label className="text-xs text-gray-500 mb-1 block">分类</label>
          <select
            value={categoryId ?? ''}
            onChange={(e) => onCategoryChange(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <option value="">全部分类</option>
            {categories.map((cat) => (
              <optgroup key={cat.id} label={cat.name}>
                {cat.children?.map((child) => (
                  <option key={child.id} value={child.id}>
                    {child.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* 价格 */}
        <div>
          <label className="text-xs text-gray-500 mb-1 block">价格</label>
          <div className="flex items-center gap-1">
            <input
              type="number"
              value={minPrice}
              onChange={(e) => onPriceChange(e.target.value, maxPrice)}
              placeholder="¥最低"
              className="w-20 px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
            <span className="text-gray-400">-</span>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => onPriceChange(minPrice, e.target.value)}
              placeholder="¥最高"
              className="w-20 px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        </div>

        {/* 排序 */}
        <div>
          <label className="text-xs text-gray-500 mb-1 block">排序</label>
          <select
            value={sort}
            onChange={(e) => onSortChange(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <option value="created_at_desc">最新上架</option>
            <option value="price_asc">价格从低到高</option>
            <option value="price_desc">价格从高到低</option>
            <option value="title_asc">书名 A-Z</option>
          </select>
        </div>

        {/* 搜索按钮 */}
        <button
          onClick={onSearch}
          className="px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
        >
          搜索
        </button>
      </div>
    </div>
  );
}
