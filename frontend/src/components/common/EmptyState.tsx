interface Props {
  title: string;
  description?: string;
}

export default function EmptyState({ title, description }: Props) {
  return (
    <div className="text-center py-16">
      <div className="text-4xl mb-3">📭</div>
      <p className="text-gray-500 font-medium">{title}</p>
      {description && <p className="text-gray-400 text-sm mt-1">{description}</p>}
    </div>
  );
}
