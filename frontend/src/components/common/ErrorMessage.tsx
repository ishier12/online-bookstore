interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: Props) {
  return (
    <div className="text-center py-12">
      <p className="text-red-500 mb-3">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-indigo-600 hover:underline text-sm"
        >
          重试
        </button>
      )}
    </div>
  );
}
