<template>
  <AppLayout>
    <template #default>
      <div class="page-header">
        <h1 class="page-title">Профиль</h1>
      </div>

      <div style="max-width: 520px; display: flex; flex-direction: column; gap: 16px;">

        <!-- Profile info card -->
        <div class="card">
          <div class="flex items-center gap-4 mb-5">
            <div class="profile-avatar">{{ initials }}</div>
            <div>
              <div class="font-semibold" style="font-size:16px;">{{ auth.user?.full_name }}</div>
              <div class="text-muted text-sm">{{ auth.user?.email }}</div>
              <div class="mt-1">
                <span v-if="auth.isAdmin" class="badge badge-admin">Администратор</span>
                <span v-else class="badge badge-approved">Пользователь</span>
              </div>
            </div>
          </div>

          <form @submit.prevent="saveProfile">
            <div class="form-group">
              <label>ФИО</label>
              <input v-model="form.full_name" type="text" required />
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0 16px;">
              <div class="form-group">
                <label>Должность</label>
                <input v-model="form.position" type="text" placeholder="Инженер-проектировщик" />
              </div>
              <div class="form-group">
                <label>Телефон (исполнитель)</label>
                <input v-model="form.phone" type="text" placeholder="+7 (999) 000-00-00" />
              </div>
            </div>

            <div v-if="saved" class="alert alert-success mb-4">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Данные сохранены
            </div>

            <button type="submit" class="btn btn-primary">Сохранить изменения</button>
          </form>
        </div>

        <!-- Password card -->
        <div class="card">
          <div class="card-title">Изменить пароль</div>
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label>Текущий пароль</label>
              <input v-model="pwd.current" type="password" required autocomplete="current-password" />
            </div>
            <div class="form-group">
              <label>Новый пароль</label>
              <input v-model="pwd.new" type="password" required autocomplete="new-password" />
            </div>

            <div v-if="pwdError" class="alert alert-error mb-4">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ pwdError }}
            </div>
            <div v-if="pwdSaved" class="alert alert-success mb-4">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Пароль успешно изменён
            </div>

            <button type="submit" class="btn btn-secondary">Изменить пароль</button>
          </form>
        </div>

      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore()
const saved = ref(false)
const pwdSaved = ref(false)
const pwdError = ref('')

const form = reactive({ full_name: '', position: '', phone: '' })
const pwd = reactive({ current: '', new: '' })

const initials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?'
})

onMounted(() => {
  if (auth.user) {
    form.full_name = auth.user.full_name
    form.position = auth.user.position || ''
    form.phone = auth.user.phone || ''
  }
})

async function saveProfile() {
  await api.patch('/profile', form)
  await auth.fetchMe()
  saved.value = true
  setTimeout(() => saved.value = false, 2500)
}

async function changePassword() {
  pwdError.value = ''
  try {
    await api.patch('/profile/password', { current_password: pwd.current, new_password: pwd.new })
    pwd.current = ''
    pwd.new = ''
    pwdSaved.value = true
    setTimeout(() => pwdSaved.value = false, 2500)
  } catch (e: any) {
    pwdError.value = e?.response?.data?.detail || 'Неверный текущий пароль'
  }
}
</script>
