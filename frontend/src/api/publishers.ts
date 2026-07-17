import apiClient from './client';
import type { Publisher } from '../types';

export async function getPublishers(): Promise<Publisher[]> {
  return apiClient.get('/publishers');
}
