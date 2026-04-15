import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface Group {
  id: string
  name: string
  icon: string | null
  sort_order: number
  subscription_count: number
}

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref<Group[]>([])

  async function load() {
    const { data } = await api.get('/groups/')
    groups.value = data
  }

  async function add(name: string, icon?: string) {
    const { data } = await api.post('/groups/', { name, icon })
    groups.value.push(data)
    return data
  }

  async function update(id: string, payload: Partial<Group>) {
    const { data } = await api.put(`/groups/${id}`, payload)
    const i = groups.value.findIndex(g => g.id === id)
    if (i >= 0) groups.value[i] = data
  }

  async function remove(id: string) {
    await api.delete(`/groups/${id}`)
    groups.value = groups.value.filter(g => g.id !== id)
  }

  return { groups, load, add, update, remove }
})
