import apiClient from './client';
import type { AuthTokens, User, RegisterData, LoginData } from '../types';

export async function register(data: RegisterData): Promise<AuthTokens> {
  return apiClient.post('/auth/register', data);
}

export async function login(data: LoginData): Promise<AuthTokens> {
  return apiClient.post('/auth/login', data);
}

export async function getMe(): Promise<User> {
  return apiClient.get('/auth/me');
}
