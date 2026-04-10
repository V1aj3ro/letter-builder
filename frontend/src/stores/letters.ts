import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface Letter {
  id: number
  number: number
  letter_date: string
  project_id: number
  recipient_id: number | null
  created_by: number
  subject: string | null
  body: string | null
  sender_type: string
  status: string
  docx_path: string | null
  pdf_path: string | null
  created_at: string
  sent_at: string | null
  recipient: { id: number; name: string } | null
  creator: { id: number; full_name: string; phone: string | null } | null
}

export const useLettersStore = defineStore('letters', () => {
  const letters = ref<Letter[]>([])
  const current = ref<Letter | null>(null)

  async function fetchByProject(projectId: number) {
    const res = await api.get(`/letters?project_id=${projectId}`)
    letters.value = res.data
  }

  async function fetchOne(id: number) {
    const res = await api.get(`/letters/${id}`)
    current.value = res.data
    return res.data as Letter
  }

  async function create(data: {
    project_id: number
    recipient_id?: number | null
    subject?: string
    body?: string
    letter_date?: string
    sender_type?: string
  }): Promise<Letter> {
    const res = await api.post('/letters', data)
    current.value = res.data
    return res.data
  }

  async function update(id: number, data: Partial<Letter>) {
    const res = await api.put(`/letters/${id}`, data)
    current.value = res.data
    return res.data as Letter
  }

  async function remove(id: number) {
    await api.delete(`/letters/${id}`)
    letters.value = letters.value.filter(l => l.id !== id)
  }

  async function markSent(id: number) {
    const res = await api.patch(`/letters/${id}/status`, { status: 'sent' })
    current.value = res.data
    return res.data as Letter
  }

  return { letters, current, fetchByProject, fetchOne, create, update, remove, markSent }
})
