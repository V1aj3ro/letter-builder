<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>✉ Letter Builder</h2>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input v-model="password" type="password" required placeholder="••••••••" />
        </div>
        <p v-if="error" style="color: var(--color-danger); font-size: 0.875rem;">{{ error }}</p>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 16px; font-size: 0.875rem;">
        Нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink>
      </p>
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
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/projects')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>
