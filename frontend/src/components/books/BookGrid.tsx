import type { Book } from '../../types';
import BookCard from './BookCard';

interface Props {
  books: Book[];
}

export default function BookGrid({ books }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-4">
      {books.map((book) => (
        <BookCard key={book.id} book={book} />
      ))}
    </div>
  );
}
