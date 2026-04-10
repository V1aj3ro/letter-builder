<template>
  <AppLayout>
    <template #default>
      <div v-if="loading" class="text-muted">Загрузка...</div>
      <template v-else-if="project">
        <!-- Breadcrumbs -->
        <div class="breadcrumbs">
          <RouterLink to="/projects">Проекты</RouterLink>
          <span>/</span>
          {{ project.name }}
        </div>

        <div class="flex items-center gap-2 mb-3">
          <h1 class="page-title">{{ project.name }}</h1>
          <RouterLink :to="`/letters/new?project_id=${project.id}`" class="btn btn-primary ml-auto">
            + Новое письмо
          </RouterLink>
        </div>

        <!-- Recipients editor -->
        <div class="card mb-3">
          <h3 style="margin: 0 0 16px; font-size: 1rem; font-weight: 600;">Адресаты</h3>

          <!-- Default recipient -->
          <div class="form-group">
            <label>Основной адресат</label>
            <select v-model="selectedDefault" @change="setDefault">
              <option :value="null">— не выбран —</option>
              <option v-for="r in allRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>

          <!-- Extra recipients -->
          <div class="mb-2">
            <label style="font-size: 0.875rem; font-weight: 500; display: block; margin-bottom: 6px;">
              Дополнительные адресаты
            </label>
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;">
              <span v-for="r in project.recipients" :key="r.id" class="chip">
                {{ r.name }}
                <button @click="removeRecipient(r.id)" title="Удалить">×</button>
              </span>
              <span v-if="!project.recipients.length" class="text-muted text-sm">Нет</span>
            </div>

            <!-- Add recipient inline -->
            <div v-if="addingRecipient" class="flex gap-2 items-center">
              <select v-model="selectedAdd" style="flex: 1; padding: 6px 8px; border: 1px solid var(--color-border); border-radius: 6px;">
                <option :value="null">Выбрать из справочника...</option>
                <option v-for="r in availableRecipients" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
              <input
                v-model="newRecipientName"
                type="text"
                placeholder="или создать нового..."
                style="flex: 1; padding: 6px 8px; border: 1px solid var(--color-border); border-radius: 6px;"
              />
              <button class="btn btn-primary btn-sm" @click="addRecipient">Добавить</button>
              <button class="btn btn-secondary btn-sm" @click="addingRecipient = false">Отмена</button>
            </div>
            <button v-else class="btn btn-secondary btn-sm" @click="addingRecipient = true">
              + Добавить адресата
            </button>
          </div>
        </div>

        <!-- Letters table -->
        <div class="card">
          <div class="flex items-center gap-2 mb-3">
            <h3 style="margin: 0; font-size: 1rem; font-weight: 600;">Письма</h3>
          </div>

          <div v-if="!letters.length" class="text-muted text-sm">Нет писем. Создайте первое!</div>
          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>№</th>
                  <th>Дата</th>
                  <th>Адресат</th>
                  <th>Тема</th>
                  <th>Статус</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in letters" :key="l.id">
                  <td>{{ l.number }}</td>
                  <td>{{ formatDate(l.letter_date) }}</td>
                  <td>{{ l.recipient?.name || '—' }}</td>
                  <td>{{ l.subject || '—' }}</td>
                  <td>
                    <span :class="['badge', l.status === 'sent' ? 'badge-sent' : 'badge-draft']">
                      {{ l.status === 'sent' ? 'Отправлено' : 'Черновик' }}
                    </span>
                  </td>
                  <td>
                    <div class="flex gap-2">
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
import api from '../api'

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
  if (!project.value) return
  if (selectedDefault.value) {
    await projectsStore.setDefaultRecipient(project.value.id, selectedDefault.value)
  }
}

async function addRecipient() {
  if (!project.value) return
  let rid = selectedAdd.value
  if (!rid && newRecipientName.value.trim()) {
    const r = await recipientsStore.create(newRecipientName.value.trim())
    rid = r.id
  }
  if (rid) {
    await projectsStore.addRecipient(project.value.id, rid)
  }
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
  return new Date(d).toLocaleDateString('ru-RU')
}
</script>
