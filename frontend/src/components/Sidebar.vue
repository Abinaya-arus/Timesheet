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
  width: 200px;
  background: var(--color-background-primary);
  border-right: 0.5px solid var(--color-border-tertiary);
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  flex-shrink: 0;
  height: 100%;
}
.sidebar-logo {
  padding: 0 16px 16px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  margin-bottom: 8px;
}
.logo-text { font-size: 15px; font-weight: 500; color: var(--color-text-primary); }
.logo-sub  { font-size: 11px; color: var(--color-text-tertiary); }
.nav-section {
  font-size: 10px; font-weight: 500; color: var(--color-text-tertiary);
  padding: 12px 16px 4px; text-transform: uppercase; letter-spacing: .05em;
}
.nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 16px; cursor: pointer; font-size: 13px;
  color: var(--color-text-secondary); text-decoration: none;
  transition: background .15s;
}
.nav-item:hover { background: var(--color-background-secondary); color: var(--color-text-primary); }
.nav-item.active { background: var(--color-background-info); color: var(--color-text-info); font-weight: 500; }
.nav-item i { font-size: 16px; }
.nav-badge { margin-left: auto; font-size: 10px; padding: 1px 6px; border-radius: 10px; }
.nav-badge-blue  { background: #E6F1FB; color: #185FA5; }
.nav-badge-amber { background: #FAEEDA; color: #854F0B; }
.back-btn { color: var(--color-text-info) !important; font-weight: 500; }
.sidebar-bottom {
  margin-top: auto; padding: 12px 16px 0;
  border-top: 0.5px solid var(--color-border-tertiary);
  display: flex; flex-direction: column; gap: 10px;
}
.user-pill { display: flex; align-items: center; gap: 8px; }
.user-name { font-size: 12px; font-weight: 500; color: var(--color-text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.user-role { font-size: 11px; color: var(--color-text-tertiary); }
.avatar-admin { background: #EAF3DE !important; color: #3B6D11 !important; }
</style>
