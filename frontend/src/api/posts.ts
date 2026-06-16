import client from './client'
import type { Post, PaginatedResponse } from '@/types'

export const postsApi = {
  getPosts(page = 1, limit = 10): Promise<PaginatedResponse<Post>> {
    return client.get('/posts', { params: { page, limit } }).then(res => res.data)
  },

  getPost(id: string): Promise<Post> {
    return client.get(`/posts/${id}`).then(res => res.data)
  },

  createPost(post: Partial<Post>): Promise<Post> {
    return client.post('/posts', post).then(res => res.data)
  },

  updatePost(id: string, post: Partial<Post>): Promise<Post> {
    return client.put(`/posts/${id}`, post).then(res => res.data)
  },

  deletePost(id: string): Promise<void> {
    return client.delete(`/posts/${id}`).then(res => res.data)
  },
}
