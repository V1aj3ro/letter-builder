<template>
  <aside class="app-sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="4" width="20" height="16" rx="2"/>
          <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
        </svg>
      </div>
      <span class="sidebar-logo-text">Letter Builder</span>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav">
      <RouterLink to="/projects" class="nav-item">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 3h6l2 3h10a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
        </svg>
        Проекты
      </RouterLink>

      <RouterLink to="/profile" class="nav-item">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="8" r="4"/>
          <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
        </svg>
        Профиль
      </RouterLink>

      <template v-if="auth.isAdmin">
        <div class="nav-divider"></div>
        <RouterLink to="/settings" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M18.66 5.34l-1.41 1.41"/>
          </svg>
          Настройки
        </RouterLink>
      </template>
    </nav>

    <!-- User footer -->
    <div class="sidebar-footer">
      <div class="user-avatar">{{ initials }}</div>
      <div class="user-info">
        <div class="user-name">{{ auth.user?.full_name }}</div>
        <div class="user-role">{{ auth.isAdmin ? 'Администратор' : 'Пользователь' }}</div>
      </div>
      <button class="logout-btn" @click="logout" title="Выйти">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const initials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?'
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
