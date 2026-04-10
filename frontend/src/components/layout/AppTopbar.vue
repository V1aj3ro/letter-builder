<template>
  <header class="app-topbar">
    <div class="flex items-center gap-2 flex-1">
      <slot name="left" />
    </div>
    <div class="flex items-center gap-2">
      <RouterLink to="/letters/new" class="btn btn-primary btn-sm">+ Новое письмо</RouterLink>
      <slot name="right" />
    </div>
  </header>
</template>
