<template>
  <AppLayout>
    <template #default>
      <div class="page-header">
        <div>
          <h1 class="page-title">Проекты</h1>
          <p class="text-muted text-sm mt-1">Управляйте проектами и деловой перепиской</p>
        </div>
        <button class="btn btn-primary ml-auto" @click="showNew = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Новый проект
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="project-grid">
        <div v-for="i in 4" :key="i" class="card" style="height:130px; animation: pulse 1.5s ease infinite;">
          <div style="width:40px;height:40px;background:var(--border);border-radius:10px;margin-bottom:12px;"></div>
          <div style="width:60%;height:14px;background:var(--border);border-radius:4px;margin-bottom:8px;"></div>
          <div style="width:40%;height:12px;background:var(--border);border-radius:4px;"></div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!store.projects.length" class="card">
        <div class="empty-state">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3h6l2 3h10a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
          </svg>
          <div class="empty-state-title">Нет проектов</div>
          <p class="empty-state-text">Создайте первый проект для управления письмами</p>
          <button class="btn btn-primary mt-4" @click="showNew = true">Создать проект</button>
        </div>
      </div>

      <!-- Grid -->
      <div v-else class="project-grid">
        <RouterLink
          v-for="(p, idx) in store.projects"
          :key="p.id"
          :to="`/projects/${p.id}`"
          class="project-card"
        >
          <div class="flex items-center gap-3">
            <div class="project-card-icon" :style="{ background: cardColors[idx % cardColors.length].bg }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="cardColors[idx % cardColors.length].icon" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3h6l2 3h10a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
              </svg>
            </div>
            <div class="project-card-body">
              <div class="project-card-name">{{ p.name }}</div>
              <div class="project-card-meta">
                <span>{{ p.letter_count }} {{ pluralLetters(p.letter_count) }}</span>
                <span style="color:var(--subtle);">·</span>
                <span>{{ formatDate(p.created_at) }}</span>
              </div>
            </div>
          </div>
          <div v-if="p.default_recipient" class="project-card-footer">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            {{ p.default_recipient.name }}
          </div>
        </RouterLink>
      </div>
    </template>
  </AppLayout>

  <!-- New project modal -->
  <div v-if="showNew" class="modal-overlay" @click.self="showNew = false">
    <div class="modal">
      <div class="modal-header">
        <h3>Новый проект</h3>
        <p class="text-muted text-sm mt-1">Введите название для нового проекта</p>
      </div>
      <div class="form-group" style="margin-bottom:0">
        <label>Название проекта</label>
        <input
          v-model="newName"
          type="text"
          placeholder="Например: БЦ Горизонт — реконструкция"
          @keydown.enter="createProject"
          ref="nameInput"
          autofocus
        />
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="showNew = false">Отмена</button>
        <button class="btn btn-primary" @click="createProject" :disabled="!newName.trim()">Создать проект</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useProjectsStore } from '../stores/projects'

const store = useProjectsStore()
const loading = ref(true)
const showNew = ref(false)
const newName = ref('')
const nameInput = ref<HTMLInputElement | null>(null)

const cardColors = [
  { bg: '#EEF2FF', icon: '#6366F1' },
  { bg: '#F0FDF4', icon: '#16A34A' },
  { bg: '#FFF7ED', icon: '#EA580C' },
  { bg: '#FDF4FF', icon: '#9333EA' },
  { bg: '#EFF6FF', icon: '#2563EB' },
  { bg: '#FFF1F2', icon: '#E11D48' },
]

onMounted(async () => {
  await store.fetchAll()
  loading.value = false
})

async function createProject() {
  if (!newName.value.trim()) return
  await store.create(newName.value.trim())
  newName.value = ''
  showNew.value = false
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

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
