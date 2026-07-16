import type { Review } from '../../types';
import StarRating from '../common/StarRating';
import { formatDate } from '../../utils/format';

interface Props {
  review: Review;
}

export default function ReviewItem({ review }: Props) {
  return (
    <div className="border-b border-gray-100 py-4 last:border-0">
      <div className="flex items-center gap-3 mb-2">
        <span className="font-medium text-sm text-gray-800">{review.username}</span>
        <StarRating rating={review.rating} size="sm" />
        <span className="text-xs text-gray-400 ml-auto">{formatDate(review.created_at)}</span>
      </div>
      {review.content && (
        <p className="text-sm text-gray-600 leading-relaxed">{review.content}</p>
      )}
    </div>
  );
}
