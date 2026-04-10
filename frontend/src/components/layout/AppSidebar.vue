<template>
  <aside class="app-sidebar">
    <div class="sidebar-logo">✉ Letter Builder</div>
    <nav class="sidebar-nav">
      <RouterLink to="/projects">📁 Проекты</RouterLink>
      <RouterLink to="/profile">👤 Профиль</RouterLink>
      <RouterLink v-if="auth.isAdmin" to="/settings">⚙ Настройки</RouterLink>
    </nav>
    <div style="padding: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
      <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;">
        {{ auth.user?.full_name }}
      </div>
      <button class="btn btn-secondary btn-sm" style="width: 100%" @click="logout">Выйти</button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
const auth = useAuthStore()
const router = useRouter()
function logout() {
  auth.logout()
  router.push('/login')
}
</script>
