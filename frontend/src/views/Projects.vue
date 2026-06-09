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
.add-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 18px;
}

.proj-card {
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  margin-bottom: 14px;
}
.proj-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  background: var(--color-background-secondary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.proj-header-left { display: flex; align-items: center; gap: 12px; }
.proj-icon {
  width: 34px; height: 34px; border-radius: 8px;
  background: var(--color-background-info);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; color: var(--color-text-info);
  flex-shrink: 0;
}
.proj-name { font-size: 13px; font-weight: 600; color: var(--color-text-primary); }
.proj-meta { font-size: 11px; color: var(--color-text-tertiary); margin-top: 2px; }
.proj-del-btn {
  width: 28px; height: 28px; border-radius: 6px;
  border: 0.5px solid #F7C1C1; background: #FCEBEB;
  color: #A32D2D; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: opacity .15s;
}
.proj-del-btn:hover { opacity: .75; }

.proj-members { display: flex; flex-direction: column; }
.member-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.member-name  { font-size: 12px; font-weight: 500; color: var(--color-text-primary); flex: 1; }
.member-dept  { font-size: 11px; color: var(--color-text-tertiary); min-width: 90px; }
.member-hours { font-size: 12px; font-weight: 500; color: var(--color-text-info); min-width: 40px; text-align: right; }
.proj-total-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px;
  background: var(--color-background-secondary);
}
.proj-total-label { font-size: 12px; font-weight: 600; color: var(--color-text-primary); }
.proj-total-hours { font-size: 13px; font-weight: 700; color: var(--color-text-primary); }

.empty-entries {
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  padding: 28px; text-align: center;
  font-size: 12px; color: var(--color-text-tertiary);
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
</style>
