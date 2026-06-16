import client from './client'
import type { Image, PaginatedResponse } from '@/types'

export const imagesApi = {
  getImages(page = 1, limit = 20): Promise<PaginatedResponse<Image>> {
    return client.get('/images', { params: { page, limit } }).then(res => res.data)
  },

  getImage(id: string): Promise<Image> {
    return client.get(`/images/${id}`).then(res => res.data)
  },

  uploadImage(file: File, title?: string): Promise<Image> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }
    return client.post('/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(res => res.data)
  },

  deleteImage(id: string): Promise<void> {
    return client.delete(`/images/${id}`).then(res => res.data)
  },
}
