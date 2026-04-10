<template>
  <AppLayout>
    <template #default>
      <div v-if="initLoading" class="text-muted">Загрузка...</div>
      <template v-else>

        <!-- Top bar -->
        <div class="flex items-center gap-2 mb-3">
          <div class="breadcrumbs" style="margin: 0;">
            <RouterLink to="/projects">Проекты</RouterLink>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <RouterLink v-if="project" :to="`/projects/${project.id}`">{{ project.name }}</RouterLink>
            <svg v-if="project" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <span>{{ letter ? `Письмо №${letter.number}` : 'Новое письмо' }}</span>
          </div>
          <div class="ml-auto flex items-center gap-2">
            <span class="save-status">{{ saveStatus }}</span>
          </div>
        </div>

        <div class="editor-layout">

          <!-- LEFT: compact form -->
          <div class="editor-sidebar">
            <div class="card">

              <!-- Project select (new letter only) -->
              <div v-if="!route.query.project_id && !letter" class="form-group">
                <label>Проект</label>
                <select v-model="form.project_id" @change="onProjectChange">
                  <option :value="null">Выберите проект...</option>
                  <option v-for="p in allProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>

              <!-- Recipient -->
              <div class="form-group">
                <label>Адресат</label>
                <div class="flex gap-2 items-center">
                  <select v-model="form.recipient_id" :disabled="readonly" style="flex: 1;">
                    <option :value="null">— не выбран —</option>
                    <option v-for="r in projectRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
                  </select>
                  <button
                    v-if="!readonly"
                    class="btn btn-secondary btn-sm btn-icon"
                    @click="showAddRecipient = !showAddRecipient"
                    title="Создать нового адресата"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  </button>
                </div>
                <div v-if="showAddRecipient" class="flex gap-2 items-center mt-2">
                  <input v-model="newRecipientName" placeholder="Название адресата" style="flex:1; padding:6px 9px; border:1px solid var(--border); border-radius:var(--r); font-size:13px; font-family:inherit;" />
                  <button class="btn btn-primary btn-sm" @click="createAndAddRecipient">Добавить</button>
                  <button class="btn btn-ghost btn-sm" @click="showAddRecipient = false">✕</button>
                </div>
              </div>

              <!-- Number + Date + Sender -->
              <div class="flex gap-2">
                <div class="form-group" style="flex: 0 0 72px;">
                  <label>№</label>
                  <input :value="letter?.number || '—'" readonly />
                </div>
                <div class="form-group flex-1">
                  <label>Дата</label>
                  <input v-model="form.letter_date" type="date" :disabled="readonly" />
                </div>
                <div class="form-group" style="flex: 0 0 76px;">
                  <label>Тип</label>
                  <select v-model="form.sender_type" :disabled="readonly">
                    <option value="ooo">ООО</option>
                    <option value="ip">ИП</option>
                  </select>
                </div>
              </div>

              <!-- Subject -->
              <div class="form-group" style="margin-bottom:0">
                <label>Тема письма</label>
                <input
                  v-model="form.subject"
                  type="text"
                  placeholder="О запросе коммерческого предложения"
                  :disabled="readonly"
                />
              </div>
            </div>

            <!-- Stale warning -->
            <div v-if="docStale && letter" class="stale-banner">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0; margin-top:1px;">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              Реквизиты изменились. Нажмите «Обновить», чтобы применить.
            </div>

            <!-- Actions -->
            <div class="card">
              <div class="sidebar-actions">
                <button
                  v-if="!letter && !readonly"
                  class="btn btn-primary"
                  @click="saveDraft"
                  :disabled="saving || !form.project_id"
                  style="justify-content:center;"
                >{{ saving ? 'Создание...' : 'Создать и открыть' }}</button>

                <button
                  v-if="letter && docStale && !readonly"
                  class="btn btn-primary"
                  @click="regenerateAndOpen"
                  :disabled="editorLoading"
                  style="justify-content:center;"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.28-6.24"/></svg>
                  {{ editorLoading ? 'Обновление...' : 'Обновить документ' }}
                </button>

                <button
                  v-if="letter && !docStale && !readonly"
                  class="btn btn-secondary"
                  @click="saveMeta"
                  :disabled="saving"
                  style="justify-content:center;"
                >{{ saving ? 'Сохранение...' : 'Сохранить' }}</button>

                <div class="flex gap-2">
                  <button class="btn btn-secondary flex-1" @click="downloadFile('docx')" :disabled="!letter" style="justify-content:center;">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    DOCX
                  </button>
                  <button class="btn btn-secondary flex-1" @click="downloadFile('pdf')" :disabled="!letter" style="justify-content:center;">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    PDF
                  </button>
                </div>

                <button
                  v-if="letter && letter.status === 'draft'"
                  class="btn btn-secondary"
                  @click="markSent"
                  style="justify-content:center;"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Отметить отправленным
                </button>
                <div v-if="letter?.status === 'sent'" style="text-align:center;">
                  <span class="badge badge-sent">Отправлено</span>
                </div>
              </div>
            </div>
          </div>

          <!-- RIGHT: OnlyOffice editor -->
          <div class="editor-main">
            <!-- No letter yet -->
            <div v-if="!letter" class="editor-placeholder">
              <div class="editor-placeholder-inner">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📄</div>
                <div style="font-weight: 600; margin-bottom: 6px;">Редактор документа</div>
                <div class="text-muted text-sm">Заполните форму и нажмите<br>«Создать и открыть»</div>
              </div>
            </div>

            <!-- Loading -->
            <div v-else-if="editorLoading" class="editor-loading">
              <div class="editor-loading-inner">
                <div class="spinner"></div>
                <div>Загрузка редактора...</div>
              </div>
            </div>

            <!-- Error -->
            <div v-else-if="editorError" class="editor-loading">
              <div class="editor-loading-inner" style="max-width: 360px; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 8px;">⚠️</div>
                <div style="font-weight: 600; margin-bottom: 8px; color: var(--color-text);">Редактор не загрузился</div>
                <div class="text-muted text-sm" style="margin-bottom: 16px;">{{ editorError }}</div>
                <button class="btn btn-primary" @click="openEditor">Попробовать снова</button>
              </div>
            </div>

            <!-- OnlyOffice container — always in DOM once letter exists so the iframe has a stable element -->
            <div v-show="letter && !editorLoading && !editorError" id="onlyoffice-container" class="onlyoffice-frame"></div>
          </div>

        </div>
      </template>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import { useOrgStore } from '../stores/org'
import { useProjectsStore } from '../stores/projects'
import { useRecipientsStore } from '../stores/recipients'
import { useLettersStore } from '../stores/letters'
import { downloadLetter } from '../api'
import api from '../api'
import type { Letter } from '../stores/letters'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const orgStore       = useOrgStore()
const projectsStore  = useProjectsStore()
const recipientsStore = useRecipientsStore()
const lettersStore   = useLettersStore()

// ── State ─────────────────────────────────────────────────────────────────────

const initLoading  = ref(true)
const saving       = ref(false)
const saveStatus   = ref('')
const editorLoading = ref(false)
const editorError   = ref('')
const showAddRecipient = ref(false)
const newRecipientName = ref('')

const letter  = ref<Letter | null>(null)
const project = ref<any>(null)

const form = reactive({
  project_id:   null as number | null,
  recipient_id: null as number | null,
  subject:      '',
  letter_date:  new Date().toISOString().split('T')[0],
  sender_type:  'ooo',
})

// Snapshot of form when document was last generated — used to detect staleness
const lastGenSnapshot = ref('')

// Whether form has changed since last generation
const docStale = computed(() => {
  if (!letter.value) return false
  return formSnapshot() !== lastGenSnapshot.value
})

function formSnapshot() {
  return JSON.stringify({
    recipient_id: form.recipient_id,
    subject:      form.subject,
    letter_date:  form.letter_date,
    sender_type:  form.sender_type,
  })
}

// ── Computed ──────────────────────────────────────────────────────────────────

const allProjects = computed(() => projectsStore.projects)
const readonly    = computed(() => letter.value?.status === 'sent')

const projectRecipients = computed(() => {
  if (!project.value) return recipientsStore.recipients
  const ids = new Set([
    project.value.default_recipient?.id,
    ...project.value.recipients.map((r: any) => r.id),
  ].filter(Boolean))
  if (ids.size === 0) return recipientsStore.recipients
  return recipientsStore.recipients.filter(r => ids.has(r.id))
})

// ── OnlyOffice ────────────────────────────────────────────────────────────────

let docEditor: any = null

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

function destroyEditor() {
  if (docEditor) {
    try { docEditor.destroyEditor() } catch { /* ignore */ }
    docEditor = null
  }
  // Clear the container
  const el = document.getElementById('onlyoffice-container')
  if (el) el.innerHTML = ''
}

async function openEditor() {
  if (!letter.value) return
  editorLoading.value = true
  editorError.value   = ''
  destroyEditor()

  // Safety timeout — if onDocumentReady never fires in 45s, show error
  let readyTimer: ReturnType<typeof setTimeout> | null = setTimeout(() => {
    if (editorLoading.value) {
      editorLoading.value = false
      editorError.value = 'Превышено время ожидания. Убедитесь, что переменная APP_PUBLIC_URL прописана в .env на сервере и указывает на публичный адрес приложения (например https://letters.demo.corpcore.ru).'
    }
  }, 45_000)

  const clearTimer = () => { if (readyTimer) { clearTimeout(readyTimer); readyTimer = null } }

  try {
    // Fetch editor config (this also regenerates the .docx)
    const { data } = await api.get(`/onlyoffice/editor-config/${letter.value.id}`)
    lastGenSnapshot.value = formSnapshot()

    await loadApiScript(data.server)

    const DocsAPI = (window as any).DocsAPI
    if (!DocsAPI) throw new Error('DocsAPI not available after script load')

    console.log('[OnlyOffice] server:', data.server)
    console.log('[OnlyOffice] document url:', data.config?.document?.url)
    console.log('[OnlyOffice] callback url:', data.config?.editorConfig?.callbackUrl)
    console.log('[OnlyOffice] jwt token present:', !!data.config?.token)

    docEditor = new DocsAPI.DocEditor('onlyoffice-container', {
      ...data.config,
      width:  '100%',
      height: '100%',
      events: {
        onDocumentReady() {
          clearTimer()
          editorLoading.value = false
        },
        onError(event: any) {
          clearTimer()
          console.error('OnlyOffice error', event)
          editorLoading.value = false
          editorError.value = `Ошибка OnlyOffice: ${JSON.stringify(event?.data ?? event)}`
        },
        onRequestClose() {
          clearTimer()
          editorLoading.value = false
        },
      },
    })
  } catch (err: any) {
    clearTimer()
    console.error('Failed to open OnlyOffice editor:', err)
    editorLoading.value = false
    editorError.value = err?.message ?? 'Не удалось загрузить редактор'
  }
}

// ── CRUD ──────────────────────────────────────────────────────────────────────

async function saveDraft() {
  saving.value = true
  try {
    if (!letter.value) {
      const l = await lettersStore.create({
        project_id:   form.project_id!,
        recipient_id: form.recipient_id,
        subject:      form.subject,
        body:         '',
        letter_date:  form.letter_date,
        sender_type:  form.sender_type,
      })
      letter.value = l
      router.replace(`/letters/${l.id}/edit`)
      saveStatus.value = 'Сохранено ✓'
      // Open editor immediately after creation
      await openEditor()
    }
  } catch {
    saveStatus.value = 'Ошибка'
  } finally {
    saving.value = false
  }
}

async function saveMeta() {
  if (!letter.value) return
  saving.value = true
  try {
    await lettersStore.update(letter.value.id, {
      recipient_id: form.recipient_id,
      subject:      form.subject,
      letter_date:  form.letter_date,
      sender_type:  form.sender_type,
    })
    letter.value = lettersStore.current!
    saveStatus.value = 'Сохранено ✓'
  } catch {
    saveStatus.value = 'Ошибка'
  } finally {
    saving.value = false
  }
}

async function regenerateAndOpen() {
  if (!letter.value) return
  saving.value = true
  try {
    // Save form data first
    await lettersStore.update(letter.value.id, {
      recipient_id: form.recipient_id,
      subject:      form.subject,
      letter_date:  form.letter_date,
      sender_type:  form.sender_type,
    })
    letter.value = lettersStore.current!
    saveStatus.value = 'Сохранено ✓'
  } catch {
    saveStatus.value = 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
  await openEditor()
}

async function markSent() {
  if (!letter.value) return
  await lettersStore.markSent(letter.value.id)
  letter.value = lettersStore.current!
}

async function downloadFile(format: 'pdf' | 'docx') {
  if (!letter.value) return
  await downloadLetter(letter.value.id, format)
}

async function createAndAddRecipient() {
  if (!newRecipientName.value.trim() || !project.value) return
  const r = await recipientsStore.create(newRecipientName.value.trim())
  await projectsStore.addRecipient(project.value.id, r.id)
  project.value = projectsStore.current
  form.recipient_id = r.id
  newRecipientName.value = ''
  showAddRecipient.value = false
}

async function onProjectChange() {
  if (form.project_id) {
    await projectsStore.fetchOne(form.project_id)
    project.value = projectsStore.current
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([
    orgStore.fetch(),
    projectsStore.fetchAll(),
    recipientsStore.fetchAll(),
  ])

  const letterId  = route.params.id      ? Number(route.params.id)      : null
  const projectId = route.query.project_id ? Number(route.query.project_id) : null

  if (letterId) {
    const l = await lettersStore.fetchOne(letterId)
    letter.value       = l
    form.project_id    = l.project_id
    form.recipient_id  = l.recipient_id
    form.subject       = l.subject || ''
    form.letter_date   = l.letter_date
    form.sender_type   = l.sender_type || 'ooo'

    await projectsStore.fetchOne(l.project_id)
    project.value = projectsStore.current

    lastGenSnapshot.value = formSnapshot()

    // Auto-open editor
    await openEditor()
  } else if (projectId) {
    form.project_id = projectId
    await projectsStore.fetchOne(projectId)
    project.value = projectsStore.current
    if (project.value?.default_recipient) {
      form.recipient_id = project.value.default_recipient.id
    }
  }

  initLoading.value = false
})

onBeforeUnmount(() => {
  destroyEditor()
})
</script>
