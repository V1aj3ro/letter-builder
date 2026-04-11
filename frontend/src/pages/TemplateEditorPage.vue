<template>
  <AppLayout>
    <template #default>
      <div class="breadcrumbs mb-2">
        <RouterLink to="/settings">Настройки</RouterLink>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
        <span>{{ title }}</span>
      </div>

      <div class="editor-full" style="height: calc(100vh - var(--topbar-height) - 72px);">
        <div v-if="editorLoading" class="editor-loading">
          <div class="editor-loading-inner">
            <div class="spinner"></div>
            <div>Загрузка редактора...</div>
          </div>
        </div>

        <div v-else-if="editorError" class="editor-loading">
          <div class="editor-loading-inner">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <div class="error-title">Редактор не загрузился</div>
            <div class="text-muted text-sm">{{ editorError }}</div>
            <button class="btn btn-primary btn-sm" @click="openEditor">Попробовать снова</button>
          </div>
        </div>

        <div v-show="!editorLoading && !editorError" id="onlyoffice-container" class="onlyoffice-frame"></div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import api from '../api'

const route = useRoute()
const ttype = computed(() => route.params.type as string)
const title = computed(() => ttype.value === 'ooo' ? 'Редактор шаблона ООО' : 'Редактор шаблона ИП')

const editorLoading = ref(false)
const editorError   = ref('')

let docEditor: any = null

function destroyEditor() {
  if (docEditor) {
    try { docEditor.destroyEditor() } catch { /* ignore */ }
    docEditor = null
  }
  const el = document.getElementById('onlyoffice-container')
  if (el) el.innerHTML = ''
}

function loadApiScript(serverUrl: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if ((window as any).DocsAPI) { resolve(); return }
    const existing = document.getElementById('oo-api-script')
    if (existing) { existing.addEventListener('load', () => resolve()); return }
    const s = document.createElement('script')
    s.id  = 'oo-api-script'
    s.src = `${serverUrl}/web-apps/apps/api/documents/api.js`
    s.onload  = () => resolve()
    s.onerror = () => reject(new Error(`Failed to load OnlyOffice API from ${serverUrl}`))
    document.head.appendChild(s)
  })
}

async function openEditor() {
  editorLoading.value = true
  editorError.value   = ''
  destroyEditor()

  let readyTimer: ReturnType<typeof setTimeout> | null = setTimeout(() => {
    if (editorLoading.value) {
      editorLoading.value = false
      editorError.value = 'Превышено время ожидания. Проверьте настройки APP_PUBLIC_URL.'
    }
  }, 45_000)
  const clearTimer = () => { if (readyTimer) { clearTimeout(readyTimer); readyTimer = null } }

  try {
    const { data } = await api.get(`/organization/template-config/${ttype.value}`)
    await loadApiScript(data.server)

    const DocsAPI = (window as any).DocsAPI
    if (!DocsAPI) throw new Error('DocsAPI not available')

    docEditor = new DocsAPI.DocEditor('onlyoffice-container', {
      ...data.config,
      width: '100%',
      height: '100%',
      events: {
        onDocumentReady() { clearTimer(); editorLoading.value = false },
        onError(event: any) {
          clearTimer()
          editorLoading.value = false
          editorError.value = `Ошибка OnlyOffice: ${JSON.stringify(event?.data ?? event)}`
        },
        onRequestClose() { clearTimer(); editorLoading.value = false },
      },
    })
  } catch (err: any) {
    clearTimer()
    editorLoading.value = false
    editorError.value = err?.response?.data?.detail ?? err?.message ?? 'Не удалось загрузить редактор'
  }
}

onMounted(async () => {
  await nextTick()
  await openEditor()
})

onBeforeUnmount(() => destroyEditor())
</script>
