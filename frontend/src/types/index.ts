// 图片类型
export interface Image {
  id: string
  url: string
  thumbnail: string
  title: string
  description?: string
  width: number
  height: number
  aspectRatio: number
  createdAt: string
  updatedAt: string
}

// 文章/帖子类型
export interface Post {
  id: string
  title: string
  content: string
  excerpt?: string
  coverImage?: Image
  images: Image[]
  tags: string[]
  published: boolean
  createdAt: string
  updatedAt: string
}

// 用户类型
export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
}

// 认证相关
export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

// API 响应
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}
