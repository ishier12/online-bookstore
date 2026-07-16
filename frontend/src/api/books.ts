import apiClient from './client';
import type { Book, BookDetail, BookSearchParams, PaginatedData } from '../types';

export async function getBooks(params: BookSearchParams): Promise<PaginatedData<Book>> {
  return apiClient.get('/books', { params });
}

export async function getBook(id: number): Promise<BookDetail> {
  return apiClient.get(`/books/${id}`);
}
