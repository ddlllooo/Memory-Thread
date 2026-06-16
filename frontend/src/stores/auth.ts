import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(sessionStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      // Mock 登录：admin / admin123
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        const mockToken = 'mock-token-' + Date.now()
        token.value = mockToken
        sessionStorage.setItem('token', mockToken)

        user.value = {
          id: '1',
          username: 'admin',
          email: 'admin@example.com',
          role: 'admin',
        }

        return true
      }

      error.value = '用户名或密码错误'
      return false
    } catch (err: any) {
      error.value = '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    // Mock 用户信息
    user.value = {
      id: '1',
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
    }
  }

  function logout() {
    user.value = null
    token.value = null
    sessionStorage.removeItem('token')
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchCurrentUser()
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchCurrentUser,
  }
})
