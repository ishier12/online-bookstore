interface Props {
  rating: number;       // 当前评分（支持小数）
  maxStars?: number;
  size?: 'sm' | 'md';
  interactive?: boolean;  // 是否可交互
  onChange?: (rating: number) => void;
}

export default function StarRating({
  rating,
  maxStars = 5,
  size = 'md',
  interactive = false,
  onChange,
}: Props) {
  const sizeClass = size === 'sm' ? 'text-sm' : 'text-lg';

  return (
    <div className={`flex items-center gap-0.5 ${sizeClass}`}>
      {Array.from({ length: maxStars }, (_, i) => {
        const starValue = i + 1;
        const filled = starValue <= Math.floor(rating);
        const half = !filled && starValue - 0.5 <= rating;

        return (
          <span
            key={i}
            onClick={() => interactive && onChange?.(starValue)}
            className={`${interactive ? 'cursor-pointer hover:scale-110' : ''} transition-transform ${
              filled ? 'text-yellow-400' : half ? 'text-yellow-300' : 'text-gray-300'
            }`}
          >
            ★
          </span>
        );
      })}
      {rating > 0 && (
        <span className="text-gray-500 text-sm ml-1">{rating.toFixed(1)}</span>
      )}
    </div>
  );
}
