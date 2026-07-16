import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User, RegisterData, LoginData } from '../types';
import * as authApi from '../api/auth';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../utils/constants';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 启动时检查本地 Token 是否有效
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }
    authApi
      .getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (data: LoginData) => {
    const result = await authApi.login(data);
    localStorage.setItem(ACCESS_TOKEN_KEY, result.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
    setUser(result.user);
  };

  const register = async (data: RegisterData) => {
    const result = await authApi.register(data);
    localStorage.setItem(ACCESS_TOKEN_KEY, result.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
    setUser(result.user);
  };

  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: !!user, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
