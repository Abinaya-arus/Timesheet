<template>
  <div class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-text">
        <i class="ti ti-clock" aria-hidden="true"></i> TimeTrack
      </div>
      <div class="logo-sub">Frappe Timesheet</div>
    </div>

    <!-- Employee nav: shown to employees or when admin is viewing an employee -->
    <template v-if="showEmployeeNav">
      <div class="nav-section">
        <span v-if="viewingEmployee">{{ viewingEmployee.name }}</span>
        <span v-else>Employee</span>
      </div>
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <i class="ti ti-layout-dashboard" aria-hidden="true"></i> Dashboard
      </router-link>
      <!-- New Entry only for actual employees, not admin viewing -->
      <router-link v-if="!isAdmin()" to="/entry" class="nav-item" active-class="active">
        <i class="ti ti-plus" aria-hidden="true"></i> New Entry
      </router-link>
      <router-link to="/analytics" class="nav-item" active-class="active">
        <i class="ti ti-chart-bar" aria-hidden="true"></i> Analytics
      </router-link>
      <router-link to="/notifications" class="nav-item" active-class="active">
        <i class="ti ti-bell" aria-hidden="true"></i> Notifications
        <span class="nav-badge nav-badge-blue">3</span>
      </router-link>
      <!-- Back button for admin viewing an employee -->
      <div v-if="isAdmin() && viewingEmployee" class="nav-item back-btn" @click="exitEmployeeView">
        <i class="ti ti-arrow-left" aria-hidden="true"></i> Back to Admin
      </div>
    </template>

    <!-- Admin nav -->
    <template v-if="isAdmin()">
      <div class="nav-section">Admin</div>
      <router-link to="/admin" class="nav-item" active-class="active">
        <i class="ti ti-users" aria-hidden="true"></i> Admin Panel
      </router-link>
      <router-link to="/approvals" class="nav-item" active-class="active">
        <i class="ti ti-checks" aria-hidden="true"></i> Approvals
        <span class="nav-badge nav-badge-amber">5</span>
      </router-link>
      <router-link to="/project-hours" class="nav-item" active-class="active">
        <i class="ti ti-clock-hour-4" aria-hidden="true"></i> Project Hours
      </router-link>
      <router-link to="/projects" class="nav-item" active-class="active">
        <i class="ti ti-briefcase" aria-hidden="true"></i> Projects
      </router-link>
    </template>

    <div class="sidebar-bottom">
      <div class="user-pill">
        <div class="avatar" :class="isAdmin() ? 'avatar-admin' : ''">
          {{ currentUser.initials || '?' }}
        </div>
        <div style="flex:1;min-width:0">
          <div class="user-name">{{ currentUser.name || currentUser.email }}</div>
          <div class="user-role">{{ isAdmin() ? 'Admin' : 'Employee' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth.js'
import { useRouter } from 'vue-router'

const { currentUser, isAdmin, isEmployee, viewingEmployee, showEmployeeNav } = useAuth()
const router = useRouter()

function exitEmployeeView() {
  viewingEmployee.value = null
  router.push('/admin')
}
</script>

<style scoped>
.sidebar {
  @apply flex flex-col flex-shrink-0 h-full py-4;
  width: 200px;
  background: var(--color-background-primary);
  border-right: 0.5px solid var(--color-border-tertiary);
}
.sidebar-logo {
  @apply px-4 pb-4 mb-2;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.logo-text { @apply text-[15px] font-medium; color: var(--color-text-primary); }
.logo-sub  { @apply text-[11px]; color: var(--color-text-tertiary); }
.nav-section {
  @apply text-[10px] font-medium uppercase tracking-[.05em] px-4 pt-3 pb-1;
  color: var(--color-text-tertiary);
}
.nav-item {
  @apply flex items-center gap-2 px-4 py-[7px] cursor-pointer text-[13px] no-underline transition-colors duration-150;
  color: var(--color-text-secondary);
}
.nav-item:hover { background: var(--color-background-secondary); color: var(--color-text-primary); }
.nav-item.active { @apply font-medium; background: var(--color-background-info); color: var(--color-text-info); }
.nav-item i { @apply text-base; }
.nav-badge { @apply ml-auto text-[10px] px-[6px] py-px rounded-[10px]; }
.nav-badge-blue  { @apply bg-[#E6F1FB] text-[#185FA5]; }
.nav-badge-amber { @apply bg-[#FAEEDA] text-[#854F0B]; }
.back-btn { @apply font-medium !important; color: var(--color-text-info) !important; }
.sidebar-bottom {
  @apply mt-auto px-4 pt-3 flex flex-col gap-[10px];
  border-top: 0.5px solid var(--color-border-tertiary);
}
.user-pill { @apply flex items-center gap-2; }
.user-name { @apply text-[12px] font-medium overflow-hidden text-ellipsis whitespace-nowrap; color: var(--color-text-primary); }
.user-role { @apply text-[11px]; color: var(--color-text-tertiary); }
.avatar-admin { background: #EAF3DE !important; color: #3B6D11 !important; }
</style>
