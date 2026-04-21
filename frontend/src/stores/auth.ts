import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

interface User {
  id: number
  email: string
  full_name: string
  position: string | null
  phone: string | null
  is_admin: boolean
  is_approved: boolean
}

function safeStorage() {
  try { return localStorage } catch { return null }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(safeStorage()?.getItem('token') ?? null)
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isApproved = computed(() => user.value?.is_approved ?? false)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  async function fetchMe() {
    try {
      const res = await api.get('/profile')
      user.value = res.data
    } catch {
      logout()
    }
  }

  async function login(email: string, password: string) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    safeStorage()?.setItem('token', token.value!)
    await fetchMe()
  }

  async function register(email: string, password: string, full_name: string) {
    const res = await api.post('/auth/register', { email, password, full_name })
    if (res.data.access_token) {
      token.value = res.data.access_token
      safeStorage()?.setItem('token', token.value!)
      await fetchMe()
      return 'ok'
    }
    return 'pending'
  }

  function logout() {
    token.value = null
    user.value = null
    safeStorage()?.removeItem('token')
  }

  return { token, user, isLoggedIn, isApproved, isAdmin, fetchMe, login, register, logout }
})
