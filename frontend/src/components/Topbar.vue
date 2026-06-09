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
  background: var(--color-background-primary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
  padding: 0 20px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.page-title { font-size: 15px; font-weight: 500; color: var(--color-text-primary); }
.topbar-actions { display: flex; align-items: center; gap: 8px; }
</style>
