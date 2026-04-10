<template>
  <AppLayout>
    <template #default>
      <div v-if="initLoading" class="text-muted">Загрузка...</div>
      <template v-else>

        <!-- Top bar -->
        <div class="flex items-center gap-2 mb-3">
          <div class="breadcrumbs" style="margin: 0;">
            <RouterLink to="/projects">Проекты</RouterLink>
            <span>/</span>
            <RouterLink v-if="project" :to="`/projects/${project.id}`">{{ project.name }}</RouterLink>
            <span>/</span>
            {{ letter ? `Письмо №${letter.number}` : 'Новое письмо' }}
          </div>
          <div class="ml-auto flex items-center gap-2">
            <span class="save-status">{{ saveStatus }}</span>
          </div>
        </div>

        <div class="editor-layout">

          <!-- LEFT: compact form -->
          <div class="editor-sidebar">
            <div class="card" style="padding: 16px;">

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
                    class="btn btn-secondary btn-sm"
                    @click="showAddRecipient = !showAddRecipient"
                    title="Создать нового адресата"
                  >+ Новый</button>
                </div>
                <div v-if="showAddRecipient" class="flex gap-2 items-center mt-2">
                  <input v-model="newRecipientName" placeholder="Название адресата" style="flex: 1; padding: 6px 8px; border: 1px solid var(--color-border); border-radius: 6px;" />
                  <button class="btn btn-primary btn-sm" @click="createAndAddRecipient">Создать</button>
                  <button class="btn btn-secondary btn-sm" @click="showAddRecipient = false">✕</button>
                </div>
              </div>

              <!-- Number + Date + Sender -->
              <div class="flex gap-2">
                <div class="form-group" style="flex: 0 0 90px;">
                  <label>Номер</label>
                  <input :value="letter?.number || '—'" readonly style="background: var(--color-bg); color: var(--color-muted);" />
                </div>
                <div class="form-group flex-1">
                  <label>Дата</label>
                  <input v-model="form.letter_date" type="date" :disabled="readonly" />
                </div>
                <div class="form-group" style="flex: 0 0 90px;">
                  <label>От кого</label>
                  <select v-model="form.sender_type" :disabled="readonly">
                    <option value="ooo">ООО</option>
                    <option value="ip">ИП</option>
                  </select>
                </div>
              </div>

              <!-- Subject -->
              <div class="form-group">
                <label>Тема</label>
                <input
                  v-model="form.subject"
                  type="text"
                  placeholder="О запросе коммерческого предложения"
                  :disabled="readonly"
                />
              </div>

              <!-- Stale warning -->
              <div v-if="docStale && letter" class="stale-banner">
                ⚠ Реквизиты изменились. Нажмите «Обновить документ», чтобы применить.
              </div>

              <!-- Actions -->
              <div class="sidebar-actions">
                <!-- Save (new letter) -->
                <button
                  v-if="!letter && !readonly"
                  class="btn btn-primary"
                  @click="saveDraft"
                  :disabled="saving || !form.project_id"
                >{{ saving ? 'Создание...' : 'Создать и открыть' }}</button>

                <!-- Update doc (existing, form changed) -->
                <button
                  v-if="letter && docStale && !readonly"
                  class="btn btn-primary"
                  @click="regenerateAndOpen"
                  :disabled="editorLoading"
                >{{ editorLoading ? 'Обновление...' : '↺ Обновить документ' }}</button>

                <!-- Save metadata only (no regen needed) -->
                <button
                  v-if="letter && !docStale && !readonly"
                  class="btn btn-secondary"
                  @click="saveMeta"
                  :disabled="saving"
                >{{ saving ? 'Сохранение...' : 'Сохранить' }}</button>

                <button class="btn btn-secondary" @click="downloadFile('docx')" :disabled="!letter">
                  ↓ DOCX
                </button>
                <button class="btn btn-secondary" @click="downloadFile('pdf')" :disabled="!letter">
                  ↓ PDF
                </button>
                <button
                  v-if="letter && letter.status === 'draft'"
                  class="btn btn-secondary"
                  @click="markSent"
                >✓ Отправлено</button>
                <span v-if="letter?.status === 'sent'" class="badge badge-sent" style="align-self: center;">Отправлено</span>
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

            <!-- OnlyOffice container — always in DOM once letter exists so the iframe has a stable element -->
            <div v-show="letter && !editorLoading" id="onlyoffice-container" class="onlyoffice-frame"></div>
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
  destroyEditor()

  try {
    // Fetch editor config (this also regenerates the .docx)
    const { data } = await api.get(`/onlyoffice/editor-config/${letter.value.id}`)
    lastGenSnapshot.value = formSnapshot()

    await loadApiScript(data.server)

    const DocsAPI = (window as any).DocsAPI
    if (!DocsAPI) throw new Error('DocsAPI not available after script load')

    docEditor = new DocsAPI.DocEditor('onlyoffice-container', {
      ...data.config,
      width:  '100%',
      height: '100%',
      events: {
        onDocumentReady() {
          editorLoading.value = false
        },
        onError(event: any) {
          console.error('OnlyOffice error', event)
          editorLoading.value = false
        },
      },
    })
  } catch (err) {
    console.error('Failed to open OnlyOffice editor:', err)
    saveStatus.value = 'Ошибка загрузки редактора'
    editorLoading.value = false
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
