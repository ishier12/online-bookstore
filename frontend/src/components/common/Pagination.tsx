interface Props {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, pageSize, total, onChange }: Props) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const pages: number[] = [];
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== -1) {
      pages.push(-1);
    }
  }

  return (
    <div className="flex justify-center items-center gap-1 mt-8">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="px-3 py-1.5 rounded text-sm disabled:text-gray-300 disabled:cursor-not-allowed hover:bg-gray-100"
      >
        &laquo;
      </button>
      {pages.map((p, i) =>
        p === -1 ? (
          <span key={`ellipsis-${i}`} className="px-2 text-gray-400">...</span>
        ) : (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={`px-3 py-1.5 rounded text-sm ${
              p === page
                ? 'bg-indigo-600 text-white'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
          >
            {p}
          </button>
        )
      )}
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="px-3 py-1.5 rounded text-sm disabled:text-gray-300 disabled:cursor-not-allowed hover:bg-gray-100"
      >
        &raquo;
      </button>
    </div>
  );
}
