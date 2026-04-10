<template>
  <div v-if="visible" class="modal-overlay" @click.self="cancel">
    <div class="modal">
      <h3>{{ title }}</h3>
      <p style="margin: 0; color: var(--color-muted);">{{ message }}</p>
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="cancel">Отмена</button>
        <button class="btn btn-danger" @click="confirm">{{ confirmLabel }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const title = ref('')
const message = ref('')
const confirmLabel = ref('Удалить')
let resolveFn: (v: boolean) => void

function open(opts: { title?: string; message?: string; confirmLabel?: string }) {
  title.value = opts.title || 'Подтверждение'
  message.value = opts.message || 'Вы уверены?'
  confirmLabel.value = opts.confirmLabel || 'Удалить'
  visible.value = true
  return new Promise<boolean>(resolve => { resolveFn = resolve })
}
function confirm() { visible.value = false; resolveFn(true) }
function cancel() { visible.value = false; resolveFn(false) }

defineExpose({ open })
</script>
