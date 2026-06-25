<template>
  <div>
    <div class="section-title" style="margin-bottom:10px">Pending Approvals</div>

    <div v-if="employeeGroups.length === 0" class="empty-entries">
      <i class="ti ti-checks" aria-hidden="true"></i> All caught up — nothing to approve.
    </div>

    <div v-for="emp in employeeGroups" :key="emp.name" class="emp-approval-block">
      <!-- Employee header -->
      <div class="emp-approval-header">
        <div class="emp-header-left">
          <div class="avatar" :style="{ background: emp.avatarBg, color: emp.avatarColor }">
            {{ emp.initials }}
          </div>
          <div>
            <div class="emp-header-name">{{ emp.name }}</div>
            <div class="emp-header-meta">{{ emp.dept }}</div>
          </div>
        </div>
        <div class="emp-header-right">
          <span class="pending-pill">
            {{ emp.pendingDays }} day{{ emp.pendingDays !== 1 ? 's' : '' }} not approved
          </span>
          <button class="mini-act-btn approve-btn" @click="approveAll(emp)">
            <i class="ti ti-checks" aria-hidden="true"></i> Approve All
          </button>
        </div>
      </div>

      <!-- Days for this employee -->
      <div class="day-approval-list">
        <div v-for="day in emp.days" :key="day.date" class="day-approval-block">
          <!-- Day row -->
          <div class="day-approval-row">
            <div class="day-approval-left">
              <span class="day-approval-date">{{ fmtDate(day.date) }}</span>
              <span class="day-approval-hours">{{ day.totalHours.toFixed(1) }}h · {{ day.entries.length }} entries</span>
              <span class="badge" :class="statusPill(day.status)">{{ day.status }}</span>
            </div>
            <div class="day-approval-actions">
              <button class="mini-act-btn approve-btn" @click="approveDay(emp, day)">
                <i class="ti ti-check" aria-hidden="true"></i> Approve
              </button>
            </div>
          </div>

          <!-- Entries for this day -->
          <div class="day-entries">
            <div class="entry-row" style="padding: 11px 18px 11px 28px" v-for="e in day.entries" :key="e.id">
              <div class="status-dot" :style="{ background: actColor(e.activity) }"></div>
              <div class="entry-time">{{ e.startTime }} – {{ e.endTime }}</div>
              <span class="badge" :style="{ background: actBg(e.activity), color: actColor(e.activity) }">{{ e.activity }}</span>
              <div class="entry-project">{{ e.project }}</div>
              <div class="entry-desc">{{ e.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/index.js'

function toISO(d) { return d.toISOString().slice(0, 10) }
function addDays(iso, n) { const d = new Date(iso); d.setDate(d.getDate() + n); return toISO(d) }
const today = toISO(new Date())

const ACT_COLORS = {
  Development:   { bg:'#E6F1FB', color:'#185FA5' },
  Meeting:       { bg:'#FCEBEB', color:'#A32D2D' },
  Learning:      { bg:'#EAF3DE', color:'#3B6D11' },
  Research:      { bg:'#EEEDFE', color:'#534AB7' },
  Testing:       { bg:'#FFF4E5', color:'#854F0B' },
  Documentation: { bg:'#F4F5F6', color:'#4B5563' },
  'Bug Fixing':  { bg:'#FCEBEB', color:'#A32D2D' },
  Design:        { bg:'#FFF0FB', color:'#7B3F8C' },
}
function actBg(a)    { return ACT_COLORS[a]?.bg    ?? '#F4F5F6' }
function actColor(a) { return ACT_COLORS[a]?.color ?? '#4B5563' }

/* ── load from API, fall back to empty ────────────────────── */
onMounted(async () => {
  try {
    const data = await api.getPendingApprovals()
    if (data && data.length) {
      pendingData.value = data.map(emp => ({
        name:       emp.name,
        initials:   emp.initials,
        dept:       emp.dept,
        avatarBg:   '#E6F1FB',
        avatarColor:'#185FA5',
        days: (emp.days || []).map(d => ({
          date:    d.date,
          status:  d.status || 'Submitted',
          entries: (d.entries || []).map(e => ({
            id:        e.name,
            startTime: String(e.start_time || '').slice(0,5),
            endTime:   String(e.end_time   || '').slice(0,5),
            activity:  e.activity_type || '',
            project:   e.project || '',
            desc:      e.description || '',
          })),
        })),
      }))
    }
  } catch(e) {
    console.error('getPendingApprovals', e)
  }
})

/* ── mock pending data (used if API not available) ─────────── */
const pendingData = ref([
  {
    name: 'Mike K', initials: 'MK', dept: 'QA',
    avatarBg: '#FAEEDA', avatarColor: '#854F0B',
    days: [
      {
        date: addDays(today, -3), status: 'Submitted',
        entries: [
          { id:1, startTime:'09:00', endTime:'12:00', activity:'Testing',     project:'Mobile App',     desc:'Functional test suite run' },
          { id:2, startTime:'13:00', endTime:'16:00', activity:'Bug Fixing',  project:'Mobile App',     desc:'Fixed crash on login screen' },
        ]
      },
      {
        date: addDays(today, -2), status: 'Submitted',
        entries: [
          { id:3, startTime:'09:30', endTime:'11:30', activity:'Testing',     project:'ERPNext Portal', desc:'Regression tests after hotfix' },
          { id:4, startTime:'13:00', endTime:'15:00', activity:'Documentation', project:'ERPNext Portal', desc:'Updated test case docs' },
        ]
      },
      {
        date: addDays(today, -1), status: 'Submitted',
        entries: [
          { id:5, startTime:'10:00', endTime:'13:00', activity:'Testing',     project:'Mobile App',     desc:'Performance benchmark tests' },
        ]
      },
    ]
  },
  {
    name: 'Sara R', initials: 'SR', dept: 'Design',
    avatarBg: '#EAF3DE', avatarColor: '#3B6D11',
    days: [
      {
        date: addDays(today, -2), status: 'Submitted',
        entries: [
          { id:6, startTime:'09:00', endTime:'12:00', activity:'Design',      project:'UI Revamp',      desc:'Redesigned onboarding flow' },
          { id:7, startTime:'13:00', endTime:'15:00', activity:'Meeting',     project:'UI Revamp',      desc:'Design review with product team' },
        ]
      },
      {
        date: addDays(today, -1), status: 'Submitted',
        entries: [
          { id:8, startTime:'09:00', endTime:'11:00', activity:'Design',      project:'UI Revamp',      desc:'Component library updates' },
        ]
      },
    ]
  },
  {
    name: 'John Dev', initials: 'JD', dept: 'Engineering',
    avatarBg: '#E6F1FB', avatarColor: '#185FA5',
    days: [
      {
        date: addDays(today, -1), status: 'Submitted',
        entries: [
          { id:9,  startTime:'09:00', endTime:'12:00', activity:'Development', project:'ERPNext Portal', desc:'Timesheet module integration' },
          { id:10, startTime:'13:00', endTime:'15:30', activity:'Research',    project:'AI Integration', desc:'Evaluated embedding APIs' },
        ]
      },
    ]
  },
])

/* ── computed groups ───────────────────────────────────────── */
const employeeGroups = computed(() =>
  pendingData.value
    .map(emp => ({
      ...emp,
      days: emp.days.map(d => ({
        ...d,
        totalHours: d.entries.reduce((s, e) => {
          const [sh, sm] = e.startTime.split(':').map(Number)
          const [eh, em] = e.endTime.split(':').map(Number)
          return s + (eh * 60 + em - sh * 60 - sm) / 60
        }, 0),
      })),
      pendingDays: emp.days.length,
    }))
    .filter(emp => emp.days.length > 0)
)

/* ── actions ───────────────────────────────────────────────── */
async function approveDay(emp, day) {
  try {
    await api.approveDay(day.date, emp.employee_id || emp.name)
  } catch(e) { console.error(e) }
  removeDay(emp.name, day.date)
}
async function approveAll(emp) {
  for (const day of emp.days) {
    try { await api.approveDay(day.date, emp.employee_id || emp.name) } catch(e) {}
  }
  pendingData.value = pendingData.value.filter(e => e.name !== emp.name)
}
function removeDay(empName, date) {
  const emp = pendingData.value.find(e => e.name === empName)
  if (!emp) return
  emp.days = emp.days.filter(d => d.date !== date)
  if (emp.days.length === 0)
    pendingData.value = pendingData.value.filter(e => e.name !== empName)
}

function fmtDate(iso) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-GB', { day:'numeric', month:'short', weekday:'short' })
}
function statusPill(s) {
  return { 'pill-green': s==='Approved', 'pill-blue': s==='Submitted', 'pill-amber': s==='Draft', 'pill-red': s==='Rejected' }
}
</script>

<style scoped>
.emp-approval-block {
  @apply rounded-lg overflow-hidden mb-5;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
}
.emp-approval-header {
  @apply flex items-center justify-between px-[18px] py-4;
  background: var(--color-background-secondary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.emp-header-left  { @apply flex items-center gap-3; }
.emp-header-name  { @apply text-[14px] font-semibold; color: var(--color-text-primary); }
.emp-header-meta  { @apply text-[12px] mt-[2px]; color: var(--color-text-tertiary); }
.emp-header-right { @apply flex items-center gap-[10px]; }
.pending-pill     { @apply text-[11px] font-medium bg-[#FAEEDA] text-[#854F0B] px-3 py-[3px] rounded-[20px]; }

.day-approval-list  { @apply flex flex-col; }
.day-approval-block { border-bottom: 0.5px solid var(--color-border-tertiary); }
.day-approval-block:last-child { border-bottom: none; }

.day-approval-row {
  @apply flex items-center justify-between px-[18px] py-3 bg-[#fafbfc];
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.day-approval-left    { @apply flex items-center gap-3; }
.day-approval-date    { @apply text-[13px] font-semibold whitespace-nowrap; color: var(--color-text-primary); }
.day-approval-hours   { @apply text-[11px]; color: var(--color-text-tertiary); }
.day-approval-actions { @apply flex gap-[6px]; }

.day-approval-actions .mini-act-btn.approve-btn,
.emp-header-right .mini-act-btn.approve-btn {
  @apply px-[18px] py-[6px] rounded-full text-[12px] font-medium cursor-pointer bg-[#EAF3DE] text-[#3B6D11] border border-[#C0DD97] select-none transition-[background,transform,box-shadow] duration-150;
}
.day-approval-actions .mini-act-btn.approve-btn:hover,
.emp-header-right .mini-act-btn.approve-btn:hover {
  @apply bg-[#d4ecbe] shadow-[0_2px_6px_rgba(60,110,17,0.18)];
}
.day-approval-actions .mini-act-btn.approve-btn:active,
.emp-header-right .mini-act-btn.approve-btn:active {
  @apply scale-[0.96] shadow-none bg-[#bfe0a0];
}

.day-entries { @apply py-1; }
.day-entries :deep(.entry-row) {
  grid-template-columns: 8px 110px 120px 180px 1fr;
  gap: 0 20px;
  padding: 12px 18px 12px 28px;
}

.empty-entries {
  @apply rounded-lg p-7 text-center text-[12px] flex items-center justify-center gap-2;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  color: var(--color-text-tertiary);
}
</style>
