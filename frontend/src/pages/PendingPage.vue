<template>
  <div class="auth-page">
    <div class="auth-card" style="text-align: center;">
      <h2>⏳ Ожидание одобрения</h2>
      <p style="color: var(--color-muted);">
        Ваш аккаунт создан и ожидает одобрения администратором.<br />
        Как только администратор одобрит вашу учётную запись, вы сможете войти.
      </p>
      <button class="btn btn-secondary" @click="logout">Выйти</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
const auth = useAuthStore()
const router = useRouter()
function logout() { auth.logout(); router.push('/login') }
</script>
