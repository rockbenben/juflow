import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface Tag {
  id: string
  name: string
  color: string | null
  subscription_count: number
}

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])

  async function load() {
    const { data } = await api.get('/tags/')
    tags.value = data
  }

  async function add(name: string, color?: string) {
    const { data } = await api.post('/tags/', { name, color })
    tags.value.push(data)
    return data
  }

  async function update(id: string, payload: Partial<Tag>) {
    const { data } = await api.put(`/tags/${id}`, payload)
    const i = tags.value.findIndex(t => t.id === id)
    if (i >= 0) tags.value[i] = data
  }

  async function remove(id: string) {
    await api.delete(`/tags/${id}`)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  return { tags, load, add, update, remove }
})
