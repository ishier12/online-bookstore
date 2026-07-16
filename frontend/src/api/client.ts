/**
 * Axios 实例 — 统一配置 baseURL、JWT 拦截、响应解包
 */
import axios from 'axios';
import { API_BASE_URL, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// 请求拦截器：自动附上 JWT Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：统一解包 { code, message, data } → 直接返回 data
apiClient.interceptors.response.use(
  (response) => response.data.data,
  async (error) => {
    if (error.response?.status === 401) {
      // Token 过期 → 尝试刷新
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const newToken = res.data.data.access_token;
          localStorage.setItem(ACCESS_TOKEN_KEY, newToken);
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(error.config);
        } catch {
          // 刷新失败 → 清除并跳转登录
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
          window.location.href = '/login';
        }
      }
      // 没有 refresh token → 直接跳登录
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

export default apiClient;
