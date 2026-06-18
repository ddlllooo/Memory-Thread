import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginCredentials } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(sessionStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  const initializing = ref(false)
  const initDone = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      token.value = response.access_token
      sessionStorage.setItem('token', response.access_token)

      // 获取用户信息
      await fetchCurrentUser()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    try {
      const userData = await authApi.getCurrentUser()
      user.value = userData
    } catch (err) {
      // token 无效，清除
      token.value = null
      sessionStorage.removeItem('token')
      user.value = null
    }
  }

  function logout() {
    user.value = null
    token.value = null
    sessionStorage.removeItem('token')
  }

  /**
   * 初始化认证状态（等待用户信息加载完成）
   * 在路由守卫中使用，避免竞态条件
   */
  async function initAuth() {
    if (initDone.value) return
    if (!token.value) {
      initDone.value = true
      return
    }
    initializing.value = true
    await fetchCurrentUser()
    initializing.value = false
    initDone.value = true
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchCurrentUser().then(() => {
      initDone.value = true
    })
  } else {
    initDone.value = true
  }

  return {
    user,
    token,
    loading,
    error,
    initializing,
    initDone,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchCurrentUser,
    initAuth,
  }
})
