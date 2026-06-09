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
  display: flex;
  width: 100%;
  height: 100vh;
  background: var(--color-background-tertiary);
  overflow: hidden;
}
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
</style>
