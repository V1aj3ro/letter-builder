<template>
  <AppLayout>
    <template #default>
      <h1 class="page-title mb-3">Профиль</h1>
      <div class="card" style="max-width: 480px;">
        <form @submit.prevent="saveProfile">
          <div class="form-group">
            <label>ФИО</label>
            <input v-model="form.full_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Должность</label>
            <input v-model="form.position" type="text" placeholder="Инженер-проектировщик" />
          </div>
          <div class="form-group">
            <label>Телефон (для блока «Исп.:»)</label>
            <input v-model="form.phone" type="text" placeholder="+7..." />
          </div>
          <p v-if="saved" style="color: var(--color-success); font-size: 0.875rem;">Сохранено ✓</p>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </form>

        <hr style="margin: 24px 0; border-color: var(--color-border);" />

        <h3 style="margin: 0 0 16px; font-size: 1rem; font-weight: 600;">Изменить пароль</h3>
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label>Текущий пароль</label>
            <input v-model="pwd.current" type="password" required />
          </div>
          <div class="form-group">
            <label>Новый пароль</label>
            <input v-model="pwd.new" type="password" required />
          </div>
          <p v-if="pwdError" style="color: var(--color-danger); font-size: 0.875rem;">{{ pwdError }}</p>
          <p v-if="pwdSaved" style="color: var(--color-success); font-size: 0.875rem;">Пароль изменён ✓</p>
          <button type="submit" class="btn btn-secondary">Изменить пароль</button>
        </form>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore()
const saved = ref(false)
const pwdSaved = ref(false)
const pwdError = ref('')

const form = reactive({ full_name: '', position: '', phone: '' })
const pwd = reactive({ current: '', new: '' })

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
  setTimeout(() => saved.value = false, 2000)
}

async function changePassword() {
  pwdError.value = ''
  try {
    await api.patch('/profile/password', { current_password: pwd.current, new_password: pwd.new })
    pwd.current = ''
    pwd.new = ''
    pwdSaved.value = true
    setTimeout(() => pwdSaved.value = false, 2000)
  } catch (e: any) {
    pwdError.value = e?.response?.data?.detail || 'Ошибка'
  }
}
</script>
