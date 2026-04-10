<template>
  <div class="auth-page" style="background: var(--bg);">
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; padding:24px;">
      <div class="card" style="max-width:420px; width:100%; text-align:center; padding:40px 36px;">
        <div style="width:56px;height:56px;background:var(--warning-bg);border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h2 style="font-size:19px; font-weight:700; margin-bottom:10px;">Ожидание одобрения</h2>
        <p class="text-muted" style="font-size:14px; line-height:1.65; margin-bottom:24px;">
          Ваша учётная запись создана и ожидает одобрения администратором.<br>
          Как только администратор активирует аккаунт, вы сможете войти.
        </p>
        <button class="btn btn-secondary w-full" style="justify-content:center;" @click="logout">Выйти</button>
      </div>
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
