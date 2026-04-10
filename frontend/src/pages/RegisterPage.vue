<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-left-content">
        <div class="auth-left-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
          </svg>
        </div>
        <h1>Letter Builder</h1>
        <p>Создайте аккаунт и начните управлять деловой перепиской эффективно</p>
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-form-card">
        <h2>Создать аккаунт</h2>
        <p class="auth-subtitle">Заполните данные для регистрации</p>

        <form @submit.prevent="submit">
          <div class="form-group">
            <label>ФИО</label>
            <input v-model="full_name" type="text" required placeholder="Иванов Иван Иванович" autocomplete="name" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="email" type="email" required placeholder="you@company.ru" autocomplete="email" />
          </div>
          <div class="form-group">
            <label>Пароль</label>
            <input v-model="password" type="password" required placeholder="Минимум 8 символов" autocomplete="new-password" />
          </div>

          <div v-if="error" class="alert alert-error mb-4">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0; margin-top:1px">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </div>

          <button type="submit" class="btn btn-primary w-full" :disabled="loading" style="justify-content:center; padding:10px;">
            {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
          </button>
        </form>

        <p class="auth-footer">
          Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const full_name = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const result = await auth.register(email.value, password.value, full_name.value)
    router.push(result === 'ok' ? '/projects' : '/pending')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>
