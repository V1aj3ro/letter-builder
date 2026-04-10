<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>Регистрация</h2>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>ФИО</label>
          <input v-model="full_name" type="text" required placeholder="Иванов Иван Иванович" />
        </div>
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
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 16px; font-size: 0.875rem;">
        Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink>
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
const full_name = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const result = await auth.register(email.value, password.value, full_name.value)
    if (result === 'ok') {
      router.push('/projects')
    } else {
      router.push('/pending')
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>
