// ====== API 通用响应格式 ======
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ====== 用户 ======
export interface User {
  id: number;
  username: string;
  email: string;
  nickname: string | null;
  avatar_url: string | null;
  is_admin: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  nickname?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

// ====== 书籍 ======
export interface Book {
  id: number;
  book_name: string;
  author: string;
  price: number;
  cover_url: string | null;
  stock: number;
  publisher_name: string | null;
  created_at: string;
}

export interface BookDetail {
  id: number;
  book_name: string;
  author: string;
  price: number;
  isbn: string | null;
  cover_url: string | null;
  description: string | null;
  stock: number;
  publisher: Publisher | null;
  categories: Category[];
  avg_rating: number | null;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface BookSearchParams {
  keyword?: string;
  category_id?: number;
  publisher_id?: number;
  min_price?: number;
  max_price?: number;
  sort?: string;
  page?: number;
  page_size?: number;
}

// ====== 出版社 ======
export interface Publisher {
  id: number;
  name: string;
  description: string | null;
}

// ====== 分类 ======
export interface Category {
  id: number;
  name: string;
  parent_id: number | null;
  children: Category[];
}

// ====== 书评 ======
export interface Review {
  id: number;
  user_id: number;
  book_id: number;
  rating: number;
  content: string | null;
  username: string;
  created_at: string;
}

export interface CreateReviewData {
  rating: number;
  content?: string;
}
