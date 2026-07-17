import { useState } from 'react';

interface Props {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, pageSize, total, onChange }: Props) {
  const totalPages = Math.ceil(total / pageSize);
  const [jumpInput, setJumpInput] = useState('');

  if (totalPages <= 1) return null;

  const pages: number[] = [];
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== -1) {
      pages.push(-1);
    }
  }

  const handleJump = () => {
    const target = parseInt(jumpInput, 10);
    if (target >= 1 && target <= totalPages) {
      onChange(target);
      setJumpInput('');
    }
  };

  return (
    <div className="flex justify-center items-center gap-1 mt-8 text-sm">
      {/* 上一页 */}
      <button
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="px-3 py-1.5 rounded disabled:text-gray-300 disabled:cursor-not-allowed hover:bg-gray-100"
      >
        &laquo;
      </button>

      {/* 页码 */}
      {pages.map((p, i) =>
        p === -1 ? (
          <span key={`ellipsis-${i}`} className="px-2 text-gray-400">...</span>
        ) : (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={`px-3 py-1.5 rounded ${
              p === page
                ? 'bg-indigo-600 text-white'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
          >
            {p}
          </button>
        )
      )}

      {/* 下一页 */}
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="px-3 py-1.5 rounded disabled:text-gray-300 disabled:cursor-not-allowed hover:bg-gray-100"
      >
        &raquo;
      </button>

      {/* 跳转到指定页 */}
      <span className="text-gray-400 ml-4">前往第</span>
      <input
        type="number"
        min={1}
        max={totalPages}
        value={jumpInput}
        onChange={(e) => setJumpInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleJump()}
        placeholder={String(page)}
        className="w-16 px-2 py-1.5 border border-gray-300 rounded text-center focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <span className="text-gray-400">页</span>
      <button
        onClick={handleJump}
        disabled={!jumpInput}
        className="px-3 py-1.5 rounded bg-indigo-500 text-white text-xs hover:bg-indigo-600 disabled:opacity-30 transition-colors"
      >
        确定
      </button>
    </div>
  );
}
