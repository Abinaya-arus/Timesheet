<template>
  <div>
    <!-- Project cards -->
    <div v-if="projectStats.length === 0" class="empty-entries">
      <i class="ti ti-briefcase-off" aria-hidden="true"></i> No projects yet.
    </div>

    <div v-for="proj in projectHours" :key="proj.name" class="proj-card">
      <!-- Project header -->
      <div class="proj-header">
        <div class="proj-header-left">
          <div class="proj-icon"><i class="ti ti-briefcase" aria-hidden="true"></i></div>
          <div>
            <div class="proj-name">{{ proj.name }}</div>
            <div class="proj-meta">{{ proj.totalHours.toFixed(1) }}h total · {{ proj.employeeCount }} employee{{ proj.employeeCount !== 1 ? 's' : '' }}</div>
          </div>
        </div>
        <div class="proj-header-right">
          <button class="proj-del-btn" @click="handleDelete(proj.name)" title="Delete project">
            <i class="ti ti-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>

      <!-- Per-employee list -->
      <div class="proj-members">
        <div class="member-row" v-for="emp in proj.employees" :key="emp.name">
          <div class="avatar" :style="{ background: emp.avatarBg, color: emp.avatarColor }" style="width:24px;height:24px;font-size:10px">
            {{ emp.initials }}
          </div>
          <span class="member-name">{{ emp.name }}</span>
          <span class="member-dept">{{ emp.dept }}</span>
          <span class="member-hours">{{ emp.hours.toFixed(1) }}h</span>
        </div>
        <div class="proj-total-row">
          <span class="proj-total-label">Total</span>
          <span class="proj-total-hours">{{ proj.totalHours.toFixed(1) }}h</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjects } from '../stores/projects.js'
import { api } from '../api/index.js'

const { projects, fetchProjects, deleteProject } = useProjects()

const projectHours = ref([])
onMounted(async () => {
  fetchProjects()
  try { projectHours.value = await api.getProjectHours() || [] } catch(e) {}
})

function handleDelete(name) {
  if (confirm(`Delete project "${name}"?`)) deleteProject(name)
}

/* ── mock employee-project hours ───────────────────────────── */
const employeeHours = [
  { name:'John Dev',  initials:'JD', dept:'Engineering', avatarBg:'#E6F1FB', avatarColor:'#185FA5', color:'#378ADD',
    projects: { 'ERPNext Portal':18, 'AI Integration':10, 'Sprint Planning':3 } },
  { name:'Sara R',    initials:'SR', dept:'Design',       avatarBg:'#EAF3DE', avatarColor:'#3B6D11', color:'#639922',
    projects: { 'UI Revamp':14, 'ERPNext Portal':4, 'Sprint Planning':2 } },
  { name:'Mike K',    initials:'MK', dept:'QA',           avatarBg:'#FAEEDA', avatarColor:'#854F0B', color:'#BA7517',
    projects: { 'Mobile App':16, 'ERPNext Portal':8, 'Bug Tracker':6 } },
  { name:'Lisa P',    initials:'LP', dept:'HR',           avatarBg:'#FCEBEB', avatarColor:'#A32D2D', color:'#E24B4A',
    projects: { 'Sprint Planning':5, 'ERPNext Portal':2 } },
]

const projectStats = computed(() =>
  projects.value.map(projName => {
    const employees = employeeHours
      .filter(e => e.projects[projName])
      .map(e => ({ ...e, hours: e.projects[projName] }))

    const totalHours = employees.reduce((s, e) => s + e.hours, 0)
    const maxHours   = Math.max(...employees.map(e => e.hours), 1)

    return {
      name: projName,
      totalHours,
      employeeCount: employees.length,
      employees: employees
        .map(e => ({ ...e, pct: (e.hours / maxHours) * 100 }))
        .sort((a, b) => b.hours - a.hours),
    }
  })
)
</script>

<style scoped>
.add-row { @apply flex items-center gap-[10px] mb-[18px]; }
.proj-card {
  @apply rounded-lg overflow-hidden mb-[14px];
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
}
.proj-header {
  @apply flex items-center justify-between px-4 py-[14px];
  background: var(--color-background-secondary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.proj-header-left { @apply flex items-center gap-3; }
.proj-icon {
  @apply w-[34px] h-[34px] rounded-lg flex items-center justify-center flex-shrink-0 text-[16px];
  background: var(--color-background-info);
  color: var(--color-text-info);
}
.proj-name      { @apply text-[13px] font-semibold; color: var(--color-text-primary); }
.proj-meta      { @apply text-[11px] mt-[2px]; color: var(--color-text-tertiary); }
.proj-del-btn {
  @apply w-7 h-7 rounded-md flex items-center justify-center cursor-pointer text-[14px] transition-opacity duration-150;
  border: 0.5px solid #F7C1C1;
  background: #FCEBEB;
  color: #A32D2D;
}
.proj-del-btn:hover { @apply opacity-75; }
.proj-members { @apply flex flex-col; }
.member-row {
  @apply flex items-center gap-[10px] px-4 py-[10px];
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.member-name  { @apply text-[12px] font-medium flex-1; color: var(--color-text-primary); }
.member-dept  { @apply text-[11px] min-w-[90px]; color: var(--color-text-tertiary); }
.member-hours { @apply text-[12px] font-medium min-w-[40px] text-right; color: var(--color-text-info); }
.proj-total-row {
  @apply flex items-center justify-between px-4 py-[10px];
  background: var(--color-background-secondary);
}
.proj-total-label { @apply text-[12px] font-semibold; color: var(--color-text-primary); }
.proj-total-hours { @apply text-[13px] font-bold; color: var(--color-text-primary); }
.empty-entries {
  @apply rounded-lg p-7 text-center text-[12px] flex items-center justify-center gap-2;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  color: var(--color-text-tertiary);
}
</style>
