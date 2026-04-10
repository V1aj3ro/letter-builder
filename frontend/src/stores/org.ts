import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface Organization {
  id: number
  name: string
  short_name: string
  inn: string
  ogrn: string
  legal_address: string
  bank_name: string
  bik: string
  account: string
  corr_account: string
  phone: string
  signer_name: string
  signer_role: string
  logo_path: string | null
  signature_path: string | null
}

export const useOrgStore = defineStore('org', () => {
  const org = ref<Organization | null>(null)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      const res = await api.get('/organization')
      org.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function save(data: Partial<Organization>) {
    const res = await api.put('/organization', data)
    org.value = res.data
  }

  async function uploadLogo(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/organization/logo', form)
    org.value = res.data
  }

  async function uploadSignature(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/organization/signature', form)
    org.value = res.data
  }

  return { org, loading, fetch, save, uploadLogo, uploadSignature }
})
