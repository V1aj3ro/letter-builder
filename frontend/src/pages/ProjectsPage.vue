<template>
  <AppLayout>
    <template #default>
      <div class="flex items-center gap-2 mb-3">
        <h1 class="page-title">Проекты</h1>
        <button class="btn btn-primary ml-auto" @click="showNew = true">+ Новый проект</button>
      </div>

      <div v-if="loading" class="text-muted">Загрузка...</div>
      <div v-else-if="!store.projects.length" class="text-muted">Нет проектов. Создайте первый!</div>
      <div v-else class="project-grid">
        <RouterLink
          v-for="p in store.projects"
          :key="p.id"
          :to="`/projects/${p.id}`"
          class="project-card"
        >
          <h3>{{ p.name }}</h3>
          <div class="meta">
            {{ p.letter_count }} писем · {{ formatDate(p.created_at) }}
          </div>
          <div v-if="p.default_recipient" class="meta mt-2">
            📬 {{ p.default_recipient.name }}
          </div>
        </RouterLink>
      </div>
    </template>
  </AppLayout>

  <!-- New project modal -->
  <div v-if="showNew" class="modal-overlay" @click.self="showNew = false">
    <div class="modal">
      <h3>Новый проект</h3>
      <div class="form-group">
        <label>Название</label>
        <input v-model="newName" type="text" placeholder="Название проекта" @keydown.enter="createProject" />
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="showNew = false">Отмена</button>
        <button class="btn btn-primary" @click="createProject" :disabled="!newName.trim()">Создать</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useProjectsStore } from '../stores/projects'

const store = useProjectsStore()
const loading = ref(true)
const showNew = ref(false)
const newName = ref('')

onMounted(async () => {
  await store.fetchAll()
  loading.value = false
})

async function createProject() {
  if (!newName.value.trim()) return
  const p = await store.create(newName.value.trim())
  newName.value = ''
  showNew.value = false
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('ru-RU')
}
</script>
