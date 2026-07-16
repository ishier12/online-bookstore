import apiClient from './client';
import type { Review, CreateReviewData, PaginatedData } from '../types';

export async function getReviews(
  bookId: number,
  page: number = 1,
  pageSize: number = 10
): Promise<PaginatedData<Review>> {
  return apiClient.get(`/books/${bookId}/reviews`, { params: { page, page_size: pageSize } });
}

export async function createReview(bookId: number, data: CreateReviewData): Promise<Review> {
  return apiClient.post(`/books/${bookId}/reviews`, data);
}
