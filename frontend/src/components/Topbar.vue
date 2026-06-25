<template>
  <div class="topbar">
    <div class="page-title">{{ route.meta.title || 'TimeTrack' }}</div>
    <div class="topbar-actions">
      <router-link v-if="isEmployee()" to="/entry" class="btn btn-primary">
        <i class="ti ti-plus" aria-hidden="true"></i> New Entry
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'

const route = useRoute()
const { isEmployee } = useAuth()
</script>

<style scoped>
.topbar {
  @apply flex items-center justify-between px-5 h-[52px] flex-shrink-0;
  background: var(--color-background-primary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.page-title    { @apply text-[15px] font-medium; color: var(--color-text-primary); }
.topbar-actions { @apply flex items-center gap-2; }
</style>
