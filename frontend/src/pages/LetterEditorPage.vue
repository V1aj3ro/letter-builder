<template>
  <AppLayout>
    <template #default>
      <div v-if="initLoading" class="text-muted text-sm">Загрузка...</div>
      <template v-else>

        <!-- ── NEW LETTER: центрированная форма создания ─────────────────── -->
        <template v-if="!letter">
          <div class="breadcrumbs mb-4">
            <RouterLink to="/projects">Проекты</RouterLink>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <RouterLink v-if="project" :to="`/projects/${project.id}`">{{ project.name }}</RouterLink>
            <svg v-if="project" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <span>Новое письмо</span>
          </div>

          <div style="max-width:520px;">
            <h1 class="page-title mb-4">Новое письмо</h1>
            <div class="card">
              <div v-if="!route.query.project_id" class="form-group">
                <label>Проект</label>
                <select v-model="form.project_id" @change="onProjectChange">
                  <option :value="null">Выберите проект...</option>
                  <option v-for="p in allProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>

              <div class="form-group">
                <label>Адресат</label>
                <div class="flex gap-2">
                  <select v-model="form.recipient_id" style="flex:1;">
                    <option :value="null">— не выбран —</option>
                    <option v-for="r in projectRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
                  </select>
                  <button class="btn btn-secondary btn-sm btn-icon" @click="showAddRecipient = !showAddRecipient" title="Добавить адресата">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  </button>
                </div>
                <div v-if="showAddRecipient" class="flex gap-2 mt-2">
                  <input v-model="newRecipientName" placeholder="Название адресата" style="flex:1;padding:7px 10px;border:1px solid var(--border);border-radius:var(--r);font-size:13.5px;font-family:inherit;" />
                  <button class="btn btn-primary btn-sm" @click="createAndAddRecipient">Добавить</button>
                  <button class="btn btn-ghost btn-sm" @click="showAddRecipient = false">✕</button>
                </div>
              </div>

              <div class="flex gap-3">
                <div class="form-group flex-1">
                  <label>Дата</label>
                  <input v-model="form.letter_date" type="date" />
                </div>
                <div class="form-group" style="flex:0 0 90px;">
                  <label>От кого</label>
                  <select v-model="form.sender_type">
                    <option value="ooo">ООО</option>
                    <option value="ip">ИП</option>
                  </select>
                </div>
              </div>

              <div class="form-group" style="margin-bottom:0;">
                <label>Тема письма</label>
                <input v-model="form.subject" type="text" placeholder="О запросе коммерческого предложения" />
              </div>
            </div>

            <div class="mt-3">
              <button class="btn btn-primary" @click="saveDraft" :disabled="saving || !form.project_id" style="padding:10px 24px;">
                {{ saving ? 'Создание...' : 'Создать и открыть редактор' }}
              </button>
            </div>
          </div>
        </template>

        <!-- ── EXISTING LETTER: горизонтальная панель + редактор ─────────── -->
        <template v-else>
          <!-- Breadcrumbs -->
          <div class="breadcrumbs mb-2">
            <RouterLink to="/projects">Проекты</RouterLink>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <RouterLink v-if="project" :to="`/projects/${project.id}`">{{ project.name }}</RouterLink>
            <svg v-if="project" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep"><polyline points="9 18 15 12 9 6"/></svg>
            <span>Письмо №{{ letter.number }}</span>
            <span class="ml-auto save-status">{{ saveStatus }}</span>
          </div>

          <!-- ── Горизонтальная форма ──────────────────────────────────── -->
          <div class="letter-form-bar">
            <!-- Адресат -->
            <div class="lf-field lf-recipient">
              <div class="lf-label">Адресат</div>
              <div class="flex gap-1">
                <select v-model="form.recipient_id" :disabled="readonly" class="lf-input">
                  <option :value="null">— не выбран —</option>
                  <option v-for="r in projectRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
                </select>
                <button v-if="!readonly" class="btn btn-secondary btn-sm btn-icon" @click="showAddRecipient = !showAddRecipient" title="Новый адресат">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
              </div>
            </div>

            <!-- Дата -->
            <div class="lf-field" style="flex:0 0 140px;">
              <div class="lf-label">Дата</div>
              <input v-model="form.letter_date" type="date" :disabled="readonly" class="lf-input" />
            </div>

            <!-- Тип -->
            <div class="lf-field" style="flex:0 0 80px;">
              <div class="lf-label">Тип</div>
              <select v-model="form.sender_type" :disabled="readonly" class="lf-input">
                <option value="ooo">ООО</option>
                <option value="ip">ИП</option>
              </select>
            </div>

            <!-- Тема -->
            <div class="lf-field lf-subject">
              <div class="lf-label">Тема</div>
              <input v-model="form.subject" type="text" :disabled="readonly" class="lf-input" placeholder="О запросе коммерческого предложения" />
            </div>

            <!-- Разделитель -->
            <div class="lf-sep"></div>

            <!-- Кнопки действий -->
            <div class="lf-actions">
              <!-- Сохранить мета (всегда доступно) -->
              <button v-if="!readonly" class="btn btn-secondary btn-sm" @click="saveMeta" :disabled="saving">
                {{ saving ? '...' : 'Сохранить' }}
              </button>

              <!-- Обновить из шаблона (деструктивно — с предупреждением) -->
              <button v-if="!readonly" class="btn btn-ghost btn-sm" @click="confirmRegenerate" :disabled="editorLoading" title="Пересоздать документ из шаблона">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.28-6.24"/></svg>
                Обновить шаблон
              </button>

              <!-- Скачать -->
              <button class="btn btn-secondary btn-sm" @click="downloadFile('docx')" title="Скачать DOCX">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                DOCX
              </button>
              <button class="btn btn-secondary btn-sm" @click="downloadFile('pdf')" title="Скачать PDF">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                PDF
              </button>

              <!-- Статус -->
              <button v-if="letter.status === 'draft'" class="btn btn-secondary btn-sm" @click="markSent">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Отправлено
              </button>
              <span v-else class="badge badge-sent">Отправлено</span>
            </div>
          </div>

          <!-- Новый адресат inline -->
          <div v-if="showAddRecipient" class="flex gap-2 mb-2">
            <input v-model="newRecipientName" placeholder="Название нового адресата" style="flex:1;max-width:300px;padding:7px 10px;border:1px solid var(--border);border-radius:var(--r);font-size:13.5px;font-family:inherit;" />
            <button class="btn btn-primary btn-sm" @click="createAndAddRecipient">Добавить</button>
            <button class="btn btn-ghost btn-sm" @click="showAddRecipient = false">Отмена</button>
          </div>

          <!-- ── Редактор ──────────────────────────────────────────────── -->
          <div class="editor-full">
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

      </template>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
let _pendingRegen = false  // set to true only when form fields changed

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
    // Fetch editor config. Pass regenerate=true only when explicitly requested
    // (form changed) — otherwise preserve existing OnlyOffice edits.
    const { data } = await api.get(`/onlyoffice/editor-config/${letter.value.id}`, {
      params: { regenerate: _pendingRegen },
    })
    _pendingRegen = false

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
      _pendingRegen = true  // first open — always generate
      await nextTick()
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

async function confirmRegenerate() {
  if (!confirm('Пересоздать документ из шаблона?\n\nВсе правки, сделанные в редакторе, будут заменены новым документом на основе текущих реквизитов.')) return
  await regenerateAndOpen()
}

async function regenerateAndOpen() {
  if (!letter.value) return
  saving.value = true
  _pendingRegen = true
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

    initLoading.value = false
    await nextTick()
    await openEditor()
    return
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
