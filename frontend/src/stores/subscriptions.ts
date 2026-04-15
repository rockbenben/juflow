import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface Source {
  id: string
  platform: string
  platform_uid: string
  display_name: string
  avatar_url: string | null
  home_url: string
  adapter_type: string
}

export interface Subscription {
  id: string
  source: Source
  fetch_interval: number
  notify_enabled: boolean
  notify_channels: string[]
  custom_name: string | null
}

export const useSubscriptionsStore = defineStore('subscriptions', () => {
  const subscriptions = ref<Subscription[]>([])

  async function load() {
    const { data } = await api.get('/subscriptions/')
    subscriptions.value = data
  }

  async function add(url: string, fetchInterval = 300) {
    const { data } = await api.post('/subscriptions/', { url, fetch_interval: fetchInterval })
    subscriptions.value.unshift(data)
    return data
  }

  async function remove(id: string) {
    await api.delete(`/subscriptions/${id}`)
    subscriptions.value = subscriptions.value.filter(s => s.id !== id)
  }

  return { subscriptions, load, add, remove }
})
