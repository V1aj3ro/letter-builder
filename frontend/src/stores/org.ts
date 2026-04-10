import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface Organization {
  id: number
  // ООО
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
  // ИП
  ip_full_name: string
  ip_inn: string
  ip_ogrnip: string
  ip_legal_address: string
  ip_bank_name: string
  ip_bik: string
  ip_account: string
  ip_corr_account: string
  ip_phone: string
  ip_signer_name: string
  ip_signer_role: string
  // Файлы
  logo_path: string | null
  footer_banner_path: string | null
  signature_path: string | null
  template_ooo_path: string | null
  template_ip_path: string | null
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

  async function uploadFooterBanner(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/organization/footer-banner', form)
    org.value = res.data
  }

  async function uploadTemplateOoo(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/organization/template-ooo', form)
    org.value = res.data
  }

  async function uploadTemplateIp(file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/organization/template-ip', form)
    org.value = res.data
  }

  return {
    org, loading, fetch, save,
    uploadLogo, uploadSignature, uploadFooterBanner,
    uploadTemplateOoo, uploadTemplateIp,
  }
})
