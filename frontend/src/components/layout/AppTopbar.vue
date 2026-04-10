<template>
  <header class="app-topbar">
    <div class="flex items-center flex-1 gap-2">
      <slot name="left" />
    </div>
    <div class="flex items-center gap-2">
      <slot name="right" />
      <RouterLink to="/letters/new" class="btn btn-primary btn-sm">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Новое письмо
      </RouterLink>
    </div>
  </header>
</template>
