<template>
  <AppLayout>
    <template #default>
      <div v-if="loading" class="text-muted text-sm">Загрузка...</div>
      <template v-else-if="project">

        <!-- Breadcrumbs -->
        <div class="breadcrumbs">
          <RouterLink to="/projects">Проекты</RouterLink>
          <svg class="breadcrumb-sep" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          <span>{{ project.name }}</span>
        </div>

        <!-- Page header -->
        <div class="page-header">
          <h1 class="page-title">{{ project.name }}</h1>
          <RouterLink :to="`/letters/new?project_id=${project.id}`" class="btn btn-primary ml-auto">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Новое письмо
          </RouterLink>
        </div>

        <!-- Recipients card -->
        <div class="card mb-4">
          <div class="section-header">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
            </svg>
            <span class="section-title">Адресаты</span>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 0 20px;">
            <!-- Default recipient -->
            <div class="form-group" style="margin-bottom:0">
              <label>Основной адресат</label>
              <select v-model="selectedDefault" @change="setDefault">
                <option :value="null">— не выбран —</option>
                <option v-for="r in allRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
            </div>

            <!-- Extra recipients -->
            <div>
              <div class="form-label">Дополнительные</div>
              <div class="flex flex-wrap gap-1" style="min-height:36px; align-items:center;">
                <span v-for="r in project.recipients" :key="r.id" class="chip">
                  {{ r.name }}
                  <button class="chip-btn" @click="removeRecipient(r.id)" title="Удалить">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </span>
                <span v-if="!project.recipients.length" class="text-subtle text-xs">Нет</span>
              </div>
            </div>
          </div>

          <!-- Add recipient row -->
          <div class="mt-3">
            <div v-if="addingRecipient" class="flex gap-2 items-center">
              <select v-model="selectedAdd" style="flex:1; padding:7px 10px; border:1px solid var(--border); border-radius:var(--r); font-size:13.5px; font-family:inherit; background:var(--surface);">
                <option :value="null">Выбрать из справочника...</option>
                <option v-for="r in availableRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
              <input
                v-model="newRecipientName"
                type="text"
                placeholder="или создать нового..."
                style="flex:1; padding:7px 10px; border:1px solid var(--border); border-radius:var(--r); font-size:13.5px; font-family:inherit;"
              />
              <button class="btn btn-primary btn-sm" @click="addRecipient">Добавить</button>
              <button class="btn btn-secondary btn-sm" @click="addingRecipient = false">Отмена</button>
            </div>
            <button v-else class="btn btn-secondary btn-sm" @click="addingRecipient = true">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Добавить адресата
            </button>
          </div>
        </div>

        <!-- Letters card -->
        <div class="card">
          <div class="section-header">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <span class="section-title">Письма</span>
            <span class="text-subtle text-xs ml-auto">{{ letters.length }} {{ pluralLetters(letters.length) }}</span>
          </div>

          <div v-if="!letters.length" class="empty-state" style="padding: 32px 16px;">
            <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width:36px;height:36px;">
              <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <div class="empty-state-title">Нет писем</div>
            <p class="empty-state-text">Создайте первое письмо для этого проекта</p>
          </div>

          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:60px;">№</th>
                  <th style="width:110px;">Дата</th>
                  <th>Адресат</th>
                  <th>Тема</th>
                  <th style="width:110px;">Статус</th>
                  <th style="width:160px;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in letters" :key="l.id">
                  <td class="font-semibold" style="color:var(--text);">{{ l.number }}</td>
                  <td class="text-muted">{{ formatDate(l.letter_date) }}</td>
                  <td>
                    <span v-if="l.recipient?.name">{{ l.recipient.name }}</span>
                    <span v-else class="text-subtle">—</span>
                  </td>
                  <td style="max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                    {{ l.subject || '—' }}
                  </td>
                  <td>
                    <span :class="['badge', l.status === 'sent' ? 'badge-sent' : 'badge-draft']">
                      {{ l.status === 'sent' ? 'Отправлено' : 'Черновик' }}
                    </span>
                  </td>
                  <td>
                    <div class="flex gap-2 justify-end">
                      <RouterLink :to="`/letters/${l.id}/edit`" class="btn btn-secondary btn-sm">
                        {{ l.status === 'draft' ? 'Редактировать' : 'Открыть' }}
                      </RouterLink>
                      <button
                        v-if="l.status === 'draft'"
                        class="btn btn-danger btn-sm"
                        @click="deleteLetter(l.id)"
                      >Удалить</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </template>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import { useProjectsStore } from '../stores/projects'
import { useRecipientsStore } from '../stores/recipients'
import { useLettersStore } from '../stores/letters'

const route = useRoute()
const projectsStore = useProjectsStore()
const recipientsStore = useRecipientsStore()
const lettersStore = useLettersStore()

const loading = ref(true)
const addingRecipient = ref(false)
const selectedAdd = ref<number | null>(null)
const newRecipientName = ref('')
const selectedDefault = ref<number | null>(null)

const project = computed(() => projectsStore.current)
const letters = computed(() => lettersStore.letters)
const allRecipients = computed(() => recipientsStore.recipients)
const availableRecipients = computed(() =>
  allRecipients.value.filter(r => !project.value?.recipients?.some(pr => pr.id === r.id))
)

onMounted(async () => {
  const id = Number(route.params.id)
  await Promise.all([
    projectsStore.fetchOne(id),
    recipientsStore.fetchAll(),
    lettersStore.fetchByProject(id),
  ])
  selectedDefault.value = project.value?.default_recipient?.id ?? null
  loading.value = false
})

async function setDefault() {
  if (!project.value || !selectedDefault.value) return
  await projectsStore.setDefaultRecipient(project.value.id, selectedDefault.value)
}

async function addRecipient() {
  if (!project.value) return
  let rid = selectedAdd.value
  if (!rid && newRecipientName.value.trim()) {
    const r = await recipientsStore.create(newRecipientName.value.trim())
    rid = r.id
  }
  if (rid) await projectsStore.addRecipient(project.value.id, rid)
  addingRecipient.value = false
  selectedAdd.value = null
  newRecipientName.value = ''
}

async function removeRecipient(rid: number) {
  if (!project.value) return
  await projectsStore.removeRecipient(project.value.id, rid)
}

async function deleteLetter(id: number) {
  if (!confirm('Удалить письмо?')) return
  await lettersStore.remove(id)
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

function pluralLetters(n: number) {
  if (n % 10 === 1 && n % 100 !== 11) return 'письмо'
  if ([2,3,4].includes(n % 10) && ![12,13,14].includes(n % 100)) return 'письма'
  return 'писем'
}
</script>
