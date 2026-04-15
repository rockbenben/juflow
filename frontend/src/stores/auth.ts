import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'
import router from '../router'

interface User {
  id: string
  email: string
  username: string
  avatar_url: string | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  async function login(email: string, password: string) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    router.push('/')
  }

  async function register(email: string, username: string, password: string) {
    const { data } = await api.post('/auth/register', { email, username, password })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    router.push('/')
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { user, token, login, register, logout }
})
