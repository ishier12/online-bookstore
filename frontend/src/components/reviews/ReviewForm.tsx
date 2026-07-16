import { useState } from 'react';
import StarRating from '../common/StarRating';

interface Props {
  onSubmit: (rating: number, content: string) => Promise<void>;
}

export default function ReviewForm({ onSubmit }: Props) {
  const [rating, setRating] = useState(0);
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) {
      setError('请选择评分');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await onSubmit(rating, content);
      setRating(0);
      setContent('');
    } catch (err: any) {
      setError(err?.detail || '提交失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-50 rounded-lg p-4">
      <h4 className="text-sm font-medium text-gray-700 mb-3">写下你的评价</h4>
      <div className="mb-3">
        <StarRating rating={rating} interactive onChange={setRating} />
      </div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="分享你的阅读感受..."
        rows={3}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
      />
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="mt-2 px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
      >
        {submitting ? '提交中...' : '发表评价'}
      </button>
    </form>
  );
}
