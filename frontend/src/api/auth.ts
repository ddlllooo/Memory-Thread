import client from './client'
import type { LoginCredentials, AuthToken, User } from '@/types'

export const authApi = {
  login(credentials: LoginCredentials): Promise<AuthToken> {
    return client.post('/auth/login', credentials).then(res => res.data)
  },

  getCurrentUser(): Promise<User> {
    return client.get('/auth/me').then(res => res.data)
  },

  logout(): Promise<void> {
    return client.post('/auth/logout').then(res => res.data)
  },
}
