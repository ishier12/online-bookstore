import type { Review } from '../../types';
import ReviewItem from './ReviewItem';
import EmptyState from '../common/EmptyState';

interface Props {
  reviews: Review[];
}

export default function ReviewList({ reviews }: Props) {
  if (reviews.length === 0) {
    return <EmptyState title="暂无书评" description="成为第一个评价的人吧" />;
  }

  return (
    <div>
      {reviews.map((review) => (
        <ReviewItem key={review.id} review={review} />
      ))}
    </div>
  );
}
