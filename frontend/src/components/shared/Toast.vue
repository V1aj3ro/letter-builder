<template>
  <Teleport to="body">
    <div class="toast-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast', t.type === 'error' ? 'toast-error' : 'toast-success']"
      >
        <svg v-if="t.type === 'success'" class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <svg v-else class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ t.message }}
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Toast { id: number; message: string; type: 'success' | 'error' }
const toasts = ref<Toast[]>([])
let nextId = 0

function show(message: string, type: 'success' | 'error' = 'success') {
  const id = nextId++
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3500)
}

defineExpose({ show })
</script>
