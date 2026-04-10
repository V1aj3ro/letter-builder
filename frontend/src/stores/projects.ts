import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface Recipient {
  id: number
  name: string
  created_at: string
}

export interface Project {
  id: number
  name: string
  created_by: number
  created_at: string
  default_recipient: Recipient | null
  letter_count: number
}

export interface ProjectDetail extends Project {
  recipients: Recipient[]
}

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const current = ref<ProjectDetail | null>(null)

  async function fetchAll() {
    const res = await api.get('/projects')
    projects.value = res.data
  }

  async function fetchOne(id: number) {
    const res = await api.get(`/projects/${id}`)
    current.value = res.data
  }

  async function create(name: string): Promise<Project> {
    const res = await api.post('/projects', { name })
    projects.value.unshift(res.data)
    return res.data
  }

  async function update(id: number, name: string) {
    const res = await api.put(`/projects/${id}`, { name })
    const idx = projects.value.findIndex(p => p.id === id)
    if (idx >= 0) projects.value[idx] = res.data
    if (current.value?.id === id) current.value = { ...current.value, ...res.data }
  }

  async function remove(id: number) {
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  async function addRecipient(projectId: number, recipientId: number) {
    await api.post(`/projects/${projectId}/recipients`, { recipient_id: recipientId })
    await fetchOne(projectId)
  }

  async function removeRecipient(projectId: number, recipientId: number) {
    await api.delete(`/projects/${projectId}/recipients/${recipientId}`)
    await fetchOne(projectId)
  }

  async function setDefaultRecipient(projectId: number, recipientId: number) {
    await api.put(`/projects/${projectId}/default-recipient`, { recipient_id: recipientId })
    await fetchOne(projectId)
  }

  return {
    projects, current, fetchAll, fetchOne, create, update, remove,
    addRecipient, removeRecipient, setDefaultRecipient,
  }
})
