<template>
  <div class="app-shell">
    <Sidebar />
    <div class="main-area">
      <Topbar />
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import Topbar from './components/Topbar.vue'
</script>

<style>
.app-shell {
  @apply flex w-full h-screen overflow-hidden;
  background: var(--color-background-tertiary);
}
.main-area {
  @apply flex-1 flex flex-col overflow-hidden min-w-0;
}
.content-area {
  @apply flex-1 overflow-y-auto p-5;
}
</style>
