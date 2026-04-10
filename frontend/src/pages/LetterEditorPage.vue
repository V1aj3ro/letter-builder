<template>
  <AppLayout>
    <template #default>
      <div v-if="initLoading" class="text-muted">Загрузка...</div>
      <template v-else>
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
          <!-- LEFT: Form -->
          <div class="editor-left">
            <div class="card">
              <!-- Project select (only if no project_id in query) -->
              <div v-if="!route.query.project_id && !letter" class="form-group">
                <label>Проект</label>
                <select v-model="form.project_id" @change="onProjectChange">
                  <option :value="null">Выберите проект...</option>
                  <option v-for="p in allProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>

              <!-- Recipient select -->
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

              <!-- Number + Date + Sender row -->
              <div class="flex gap-2">
                <div class="form-group" style="flex: 0 0 120px;">
                  <label>Номер</label>
                  <input :value="letter?.number || '—'" readonly style="background: var(--color-bg); color: var(--color-muted);" />
                </div>
                <div class="form-group flex-1">
                  <label>Дата</label>
                  <input v-model="form.letter_date" type="date" :disabled="readonly" />
                </div>
                <div class="form-group" style="flex: 0 0 140px;">
                  <label>Отправитель</label>
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

              <!-- Body (Tiptap) -->
              <div class="form-group">
                <label>Текст письма</label>
                <div class="tiptap-editor">
                  <div class="tiptap-toolbar" v-if="!readonly">
                    <!-- Formatting group -->
                    <button
                      @click="editor?.chain().focus().toggleBold().run()"
                      :class="{ 'is-active': editor?.isActive('bold') }"
                      title="Жирный (Ctrl+B)"
                    ><b>B</b></button>
                    <button
                      @click="editor?.chain().focus().toggleItalic().run()"
                      :class="{ 'is-active': editor?.isActive('italic') }"
                      title="Курсив (Ctrl+I)"
                    ><i>I</i></button>
                    <button
                      @click="editor?.chain().focus().toggleUnderline().run()"
                      :class="{ 'is-active': editor?.isActive('underline') }"
                      title="Подчёркнутый (Ctrl+U)"
                    ><u>U</u></button>

                    <span class="toolbar-sep"></span>

                    <!-- Lists group -->
                    <button
                      @click="editor?.chain().focus().toggleBulletList().run()"
                      :class="{ 'is-active': editor?.isActive('bulletList') }"
                      title="Маркированный список"
                    >☰ Список</button>
                    <button
                      @click="editor?.chain().focus().toggleOrderedList().run()"
                      :class="{ 'is-active': editor?.isActive('orderedList') }"
                      title="Нумерованный список"
                    >1. Список</button>

                    <span class="toolbar-sep"></span>

                    <!-- Table group -->
                    <button @click="insertTable" title="Вставить таблицу 3×3">⊞ Таблица</button>

                    <!-- Contextual table editing (shown only when cursor is inside a table) -->
                    <template v-if="isInTable">
                      <span class="toolbar-sep"></span>
                      <button @click="editor?.chain().focus().addRowAfter().run()" title="Добавить строку ниже">+ Строка</button>
                      <button @click="editor?.chain().focus().deleteRow().run()" title="Удалить текущую строку">− Строка</button>
                      <button @click="editor?.chain().focus().addColumnAfter().run()" title="Добавить столбец правее">+ Столбец</button>
                      <button @click="editor?.chain().focus().deleteColumn().run()" title="Удалить текущий столбец">− Столбец</button>
                      <button @click="editor?.chain().focus().deleteTable().run()" title="Удалить таблицу" class="btn-danger-toolbar">✕ Таблица</button>
                    </template>
                  </div>
                  <EditorContent :editor="editor" />
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2" style="flex-wrap: wrap; margin-top: 8px;">
                <button
                  v-if="!readonly"
                  class="btn btn-primary"
                  @click="saveDraft"
                  :disabled="saving"
                >{{ saving ? 'Сохранение...' : 'Сохранить' }}</button>

                <button class="btn btn-secondary" @click="download('docx')" :disabled="!letter">
                  ↓ Скачать DOCX
                </button>
                <button class="btn btn-secondary" @click="download('pdf')" :disabled="!letter">
                  ↓ Скачать PDF
                </button>
                <button
                  v-if="letter && letter.status === 'draft'"
                  class="btn btn-secondary"
                  @click="markSent"
                >✓ Отметить отправленным</button>
                <span v-if="letter?.status === 'sent'" class="badge badge-sent" style="align-self: center;">Отправлено</span>
              </div>
            </div>
          </div>

          <!-- RIGHT: Preview -->
          <div class="editor-right">
            <div class="letter-preview">
              <template v-if="org">
                <!-- Header -->
                <div class="preview-header">
                  <div class="preview-logo">
                    <img v-if="org.logo_path" :src="'/uploads/' + org.logo_path.split('/uploads/').pop()" alt="logo" />
                  </div>
                  <div class="preview-org-details">
                    <template v-if="form.sender_type === 'ip'">
                      <strong>{{ org.ip_full_name }}</strong><br />
                      <template v-if="org.ip_inn">ИНН {{ org.ip_inn }}<br /></template>
                      <template v-if="org.ip_ogrnip">ОГРНИП {{ org.ip_ogrnip }}<br /></template>
                      <template v-if="org.ip_account">Р/с {{ org.ip_account }}<br /></template>
                      <template v-if="org.ip_bank_name">{{ org.ip_bank_name }}<br /></template>
                      <template v-if="org.ip_corr_account">К/с {{ org.ip_corr_account }}<br /></template>
                      <template v-if="org.ip_bik">БИК {{ org.ip_bik }}<br /></template>
                      <template v-if="org.ip_legal_address">{{ org.ip_legal_address }}<br /></template>
                      <template v-if="org.ip_phone">Тел.: {{ org.ip_phone }}</template>
                    </template>
                    <template v-else>
                      <strong>{{ org.name }}</strong><br />
                      <template v-if="org.inn">ИНН {{ org.inn }}<br /></template>
                      <template v-if="org.ogrn">ОГРН {{ org.ogrn }}<br /></template>
                      <template v-if="org.account">Р/с {{ org.account }}<br /></template>
                      <template v-if="org.bank_name">{{ org.bank_name }}<br /></template>
                      <template v-if="org.corr_account">К/с {{ org.corr_account }}<br /></template>
                      <template v-if="org.bik">БИК {{ org.bik }}<br /></template>
                      <template v-if="org.legal_address">{{ org.legal_address }}<br /></template>
                      <template v-if="org.phone">Тел.: {{ org.phone }}</template>
                    </template>
                  </div>
                </div>
                <hr class="preview-hr" />
              </template>
              <div v-else class="text-muted text-sm" style="margin-bottom: 8px;">
                ⚠ Заполните данные организации в настройках
              </div>

              <div class="preview-meta">Исх.№{{ letter?.number || '___' }} от {{ formatDate(form.letter_date) }} г.</div>

              <div v-if="selectedRecipient" class="preview-recipient">{{ selectedRecipient.name }}</div>

              <div v-if="form.subject" class="preview-subject">{{ form.subject }}</div>

              <div class="preview-body" v-html="form.body || ''" />

              <!-- Signature -->
              <div class="preview-signature" v-if="org">
                <div class="preview-sig-left">
                  <template v-if="form.sender_type === 'ip'">
                    С уважением,<br />{{ org.ip_signer_role }} ИП {{ org.ip_full_name }}
                  </template>
                  <template v-else>
                    С уважением,<br />{{ org.signer_role }} {{ org.short_name }}
                  </template>
                </div>
                <div class="preview-sig-mid">
                  <img v-if="org.signature_path" :src="'/uploads/' + org.signature_path.split('/uploads/').pop()" alt="подпись" />
                </div>
                <div class="preview-sig-right">
                  {{ form.sender_type === 'ip' ? org.ip_signer_name : org.signer_name }}
                </div>
              </div>

              <!-- Footer banner -->
              <div v-if="org?.footer_banner_path" class="preview-footer-banner">
                <img :src="'/uploads/' + org.footer_banner_path.split('/uploads/').pop()" alt="баннер" />
              </div>

              <!-- Executor -->
              <div class="preview-executor" v-if="auth.user">
                Исп.:<br />{{ auth.user.full_name }}<br />{{ auth.user.phone || '' }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import Document from '@tiptap/extension-document'
import Paragraph from '@tiptap/extension-paragraph'
import Text from '@tiptap/extension-text'
import Bold from '@tiptap/extension-bold'
import Italic from '@tiptap/extension-italic'
import Underline from '@tiptap/extension-underline'
import BulletList from '@tiptap/extension-bullet-list'
import OrderedList from '@tiptap/extension-ordered-list'
import ListItem from '@tiptap/extension-list-item'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'

import AppLayout from '../components/layout/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import { useOrgStore } from '../stores/org'
import { useProjectsStore } from '../stores/projects'
import { useRecipientsStore } from '../stores/recipients'
import { useLettersStore } from '../stores/letters'
import { downloadLetter } from '../api'
import type { Letter } from '../stores/letters'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const orgStore = useOrgStore()
const projectsStore = useProjectsStore()
const recipientsStore = useRecipientsStore()
const lettersStore = useLettersStore()

const initLoading = ref(true)
const saving = ref(false)
const saveStatus = ref('')
const showAddRecipient = ref(false)
const newRecipientName = ref('')

const letter = ref<Letter | null>(null)
const project = ref<any>(null)

const form = reactive({
  project_id: null as number | null,
  recipient_id: null as number | null,
  subject: '',
  body: '',
  letter_date: new Date().toISOString().split('T')[0],
  sender_type: 'ooo',
})

const org = computed(() => orgStore.org)
const allProjects = computed(() => projectsStore.projects)
const readonly = computed(() => letter.value?.status === 'sent')
const isInTable = computed(() =>
  editor.value?.isActive('tableCell') || editor.value?.isActive('tableHeader') || false
)

const projectRecipients = computed(() => {
  if (!project.value) return recipientsStore.recipients
  const ids = new Set([
    project.value.default_recipient?.id,
    ...project.value.recipients.map((r: any) => r.id),
  ].filter(Boolean))
  if (ids.size === 0) return recipientsStore.recipients
  return recipientsStore.recipients.filter(r => ids.has(r.id))
})

const selectedRecipient = computed(() =>
  projectRecipients.value.find(r => r.id === form.recipient_id) || null
)

// Tiptap editor
const editor = useEditor({
  extensions: [
    Document, Paragraph, Text, Bold, Italic, Underline,
    BulletList, OrderedList, ListItem,
    Table.configure({ resizable: true }),
    TableRow, TableCell, TableHeader,
  ],
  content: '',
  editable: true,
  onUpdate({ editor }) {
    form.body = editor.getHTML()
  },
})

watch(() => readonly.value, (val) => {
  editor.value?.setEditable(!val)
})

function insertTable() {
  editor.value?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

// Autosave with debounce
let autoSaveTimer: ReturnType<typeof setTimeout> | null = null
function scheduleAutoSave() {
  if (!letter.value || readonly.value) return
  saveStatus.value = 'Сохранение...'
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => doAutoSave(), 2000)
}
async function doAutoSave() {
  if (!letter.value) return
  try {
    await lettersStore.update(letter.value.id, {
      recipient_id: form.recipient_id,
      subject: form.subject,
      body: form.body,
      letter_date: form.letter_date,
      sender_type: form.sender_type,
    })
    saveStatus.value = 'Сохранено ✓'
  } catch {
    saveStatus.value = 'Ошибка сохранения'
  }
}

watch([() => form.recipient_id, () => form.subject, () => form.body, () => form.letter_date, () => form.sender_type], scheduleAutoSave)

async function onProjectChange() {
  if (form.project_id) {
    await projectsStore.fetchOne(form.project_id)
    project.value = projectsStore.current
  }
}

async function saveDraft() {
  saving.value = true
  try {
    if (!letter.value) {
      const l = await lettersStore.create({
        project_id: form.project_id!,
        recipient_id: form.recipient_id,
        subject: form.subject,
        body: form.body,
        letter_date: form.letter_date,
        sender_type: form.sender_type,
      })
      letter.value = l
      router.replace(`/letters/${l.id}/edit`)
      saveStatus.value = 'Сохранено ✓'
    } else {
      await lettersStore.update(letter.value.id, {
        recipient_id: form.recipient_id,
        subject: form.subject,
        body: form.body,
        letter_date: form.letter_date,
        sender_type: form.sender_type,
      })
      letter.value = lettersStore.current!
      saveStatus.value = 'Сохранено ✓'
    }
  } catch (e) {
    saveStatus.value = 'Ошибка'
  } finally {
    saving.value = false
  }
}

async function markSent() {
  if (!letter.value) return
  await lettersStore.markSent(letter.value.id)
  letter.value = lettersStore.current!
}

async function download(format: 'pdf' | 'docx') {
  if (!letter.value) return
  await saveDraft()
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

function formatDate(d: string) {
  if (!d) return '___'
  const dt = new Date(d)
  return dt.toLocaleDateString('ru-RU')
}

onMounted(async () => {
  await Promise.all([
    orgStore.fetch(),
    projectsStore.fetchAll(),
    recipientsStore.fetchAll(),
  ])

  const letterId = route.params.id ? Number(route.params.id) : null
  const projectId = route.query.project_id ? Number(route.query.project_id) : null

  if (letterId) {
    const l = await lettersStore.fetchOne(letterId)
    letter.value = l
    form.project_id = l.project_id
    form.recipient_id = l.recipient_id
    form.subject = l.subject || ''
    form.body = l.body || ''
    form.letter_date = l.letter_date
    form.sender_type = l.sender_type || 'ooo'
    editor.value?.commands.setContent(l.body || '')
    await projectsStore.fetchOne(l.project_id)
    project.value = projectsStore.current
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
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  editor.value?.destroy()
})
</script>
