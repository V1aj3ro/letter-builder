import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface Recipient {
  id: number
  name: string
  created_at: string
}

export const useRecipientsStore = defineStore('recipients', () => {
  const recipients = ref<Recipient[]>([])

  async function fetchAll() {
    const res = await api.get('/recipients')
    recipients.value = res.data
  }

  async function create(name: string): Promise<Recipient> {
    const res = await api.post('/recipients', { name })
    recipients.value.push(res.data)
    return res.data
  }

  async function update(id: number, name: string) {
    const res = await api.put(`/recipients/${id}`, { name })
    const idx = recipients.value.findIndex(r => r.id === id)
    if (idx >= 0) recipients.value[idx] = res.data
  }

  async function remove(id: number) {
    await api.delete(`/recipients/${id}`)
    recipients.value = recipients.value.filter(r => r.id !== id)
  }

  return { recipients, fetchAll, create, update, remove }
})
