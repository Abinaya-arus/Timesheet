<template>
  <div>
    <!-- Date bar -->
    <div class="date-bar">
      <span class="date-label">Date:</span>
      <div
        v-for="p in periods"
        :key="p"
        class="date-chip"
        :class="{ active: activePeriod === p }"
        @click="selectPeriod(p)"
      >{{ p }}</div>
      <input
        type="date"
        class="form-input"
        style="padding:4px 8px;font-size:12px;width:auto"
        v-model="selectedDate"
        @change="selectSpecificDate"
      >
    </div>

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-value" :style="s.color ? `color:${s.color}` : ''">{{ s.value }}</div>
        <div class="stat-sub">{{ s.sub }}</div>
      </div>
    </div>

    <!-- Day timeline (Today / custom date) -->
    <div v-if="isDayView" class="section-card">
      <div class="section-title">{{ timelineTitle }} Timeline</div>
      <div v-if="timelineBlocks.length" class="timeline-track">
        <div
          v-for="b in timelineBlocks"
          :key="b.id"
          class="tl-block"
          :style="{ left: b.left, width: b.width, background: b.color }"
          :title="b.title"
        >{{ b.label }}</div>
      </div>
      <div v-else class="tl-empty">No activity recorded for this day.</div>
      <div class="timeline-labels">
        <span v-for="t in timeLabels" :key="t">{{ t }}</span>
      </div>
    </div>


    <!-- Entries -->
    <div class="section-title" style="margin-bottom:10px">
      {{ entriesTitle }}
      <span style="font-size:11px;font-weight:400;color:var(--color-text-tertiary);margin-left:6px">
        {{ filteredEntries.length }} entr{{ filteredEntries.length === 1 ? 'y' : 'ies' }}
      </span>
    </div>
    <div v-if="filteredEntries.length === 0" class="empty-entries">
      <i class="ti ti-calendar-off" aria-hidden="true"></i>
      No entries found for this {{ activePeriod === 'Custom' ? 'date' : activePeriod.toLowerCase() }}.
    </div>
    <div v-else>
      <div v-for="group in groupedEntries" :key="group.date" class="day-group">
        <!-- Day header with single action -->
        <div class="day-header">
          <div class="day-header-left">
            <span class="day-label">{{ fmtDate(group.date) }}</span>
            <span class="day-total">{{ group.totalHours.toFixed(1) }}h · {{ group.entries.length }} entries</span>
          </div>
          <div class="day-header-right">
            <span class="badge" :class="statusPill(group.dayStatus)">{{ group.dayStatus }}</span>
            <!-- Employee: submit their own draft days -->
            <button
              v-if="isEmployee() && group.dayStatus === 'Draft'"
              class="mini-act-btn submit-btn"
              @click="submitDay(group.date)"
            ><i class="ti ti-send" aria-hidden="true"></i> Submit</button>
            <!-- Admin viewing an employee: approve/reject every day regardless of status (except already approved/rejected) -->
            <template v-if="isAdmin() && viewingEmployee">
              <button
                v-if="group.dayStatus !== 'Approved'"
                class="mini-act-btn approve-btn"
                @click="approveDay(group.date)"
              ><i class="ti ti-check" aria-hidden="true"></i> Approve</button>
            </template>
            <template v-else-if="isAdmin() && !viewingEmployee">
              <button
                v-if="group.dayStatus === 'Submitted'"
                class="mini-act-btn approve-btn"
                @click="approveDay(group.date)"
              ><i class="ti ti-check" aria-hidden="true"></i> Approve</button>
            </template>
          </div>
        </div>
        <!-- Entries for this day -->
        <div class="entry-list">
          <template v-for="e in group.entries" :key="e.id">
            <!-- Normal row -->
            <div class="entry-row" :class="{ 'entry-draft': e.status === 'Draft' }">
              <div class="status-dot" :style="{ background: e.dotColor }"></div>
              <div class="entry-time">{{ e.startTime }} – {{ e.endTime }}</div>
              <span class="badge" :style="{ background: e.actBg, color: e.actColor }">{{ e.activityType || e.activity }}</span>
              <div class="entry-project">{{ e.project }}</div>
              <div class="entry-desc">{{ e.desc }}</div>
              <!-- Draft: edit only -->
              <div v-if="e.status === 'Draft' && isEmployee()" class="entry-actions">
                <button class="entry-act-btn edit-btn" @click="startEdit(e)">
                  <i class="ti ti-pencil" aria-hidden="true"></i> Edit
                </button>
              </div>
            </div>
            <!-- Inline edit form -->
            <div v-if="editingId === e.id" class="inline-edit">
              <div class="ie-grid">
                <div class="form-group">
                  <label class="form-label">Project</label>
                  <input class="form-input" v-model="editDraft.project">
                </div>
                <div class="form-group">
                  <label class="form-label">Activity</label>
                  <select class="form-input" v-model="editDraft.activityType">
                    <option v-for="a in actTypes" :key="a">{{ a }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Start</label>
                  <input type="time" class="form-input" v-model="editDraft.startTime">
                </div>
                <div class="form-group">
                  <label class="form-label">End</label>
                  <input type="time" class="form-input" v-model="editDraft.endTime">
                </div>
              </div>
              <div class="form-group" style="margin-bottom:10px">
                <label class="form-label">Description</label>
                <textarea class="form-input" rows="2" style="resize:none" v-model="editDraft.description"></textarea>
              </div>
              <div class="ie-actions">
                <button class="btn btn-primary" @click="saveEdit(e.id)">Save</button>
                <button class="btn" @click="cancelEdit">Cancel</button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../composables/useAuth.js'
import { useEntries } from '../stores/entries.js'
import { api } from '../api/index.js'

const { liveEntries, updateEntry: storeUpdate, submitEntry: storeSubmit,
        fetchTodayEntries, submitDay: storeSubmitDay } = useEntries()

const { isAdmin, isEmployee, viewingEmployee } = useAuth()

/* ── helpers ───────────────────────────────────────────────── */
function toISO(d) { return d.toISOString().slice(0, 10) }
function addDays(iso, n) {
  const d = new Date(iso); d.setDate(d.getDate() + n); return toISO(d)
}
function toMinutes(t) { const [h, m] = t.split(':').map(Number); return h * 60 + m }

/* ── reactive today — refreshes at midnight ────────────────── */
const today = ref(toISO(new Date()))
let   midnightTimer = null

function msUntilMidnight() {
  const now  = new Date()
  const next = new Date(now)
  next.setHours(24, 0, 0, 0)           // next midnight
  return next - now
}

function scheduleMidnightRefresh() {
  midnightTimer = setTimeout(() => {
    today.value = toISO(new Date())     // new day — week/month filters recompute
    selectedDate.value = today.value    // reset date picker to today
    activePeriod.value = 'Today'
    scheduleMidnightRefresh()           // schedule the next midnight
  }, msUntilMidnight())
}

onMounted(() => {
  scheduleMidnightRefresh()
  fetchTodayEntries()
  loadHistoricalEntries()
})
onUnmounted(() => clearTimeout(midnightTimer))

/* ── historical entries from API ──────────────────────────── */
const historicalRaw = ref([])

async function loadHistoricalEntries() {
  try {
    const emp = viewingEmployee.value?.id || undefined
    // load last 30 days excluding today
    const data = await api.getEntries({ employee: emp })
    historicalRaw.value = (data || []).filter(e => e.date !== today.value)
  } catch(err) {
    console.error('loadHistoricalEntries', err)
  }
}

/* ── activity colour map ───────────────────────────────────── */
const ACT = {
  Development:   { bg:'#E6F1FB', color:'#185FA5', dot:'#378ADD', tl:'#378ADD' },
  Meeting:       { bg:'#FCEBEB', color:'#A32D2D', dot:'#E24B4A', tl:'#E24B4A' },
  Learning:      { bg:'#EAF3DE', color:'#3B6D11', dot:'#639922', tl:'#639922' },
  Research:      { bg:'#EEEDFE', color:'#534AB7', dot:'#7F77DD', tl:'#7F77DD' },
  Testing:       { bg:'#FFF4E5', color:'#854F0B', dot:'#BA7517', tl:'#BA7517' },
  Documentation: { bg:'#F4F5F6', color:'#4B5563', dot:'#9ca3af', tl:'#9ca3af' },
  'Bug Fixing':  { bg:'#FCEBEB', color:'#A32D2D', dot:'#E24B4A', tl:'#E24B4A' },
  Deployment:    { bg:'#EAF3DE', color:'#3B6D11', dot:'#639922', tl:'#639922' },
  Support:       { bg:'#EEEDFE', color:'#534AB7', dot:'#7F77DD', tl:'#7F77DD' },
}
function a(type) { return ACT[type] || { bg:'#F4F5F6', color:'#4B5563', dot:'#9ca3af', tl:'#9ca3af' } }

/* ── merge live (today) + historical (API) ─────────────────── */
const allEntries = computed(() => {
  const enrich = e => ({
    ...e,
    id:           e.id || e.name,
    desc:         e.description || e.desc || '',
    activityType: e.activityType || e.activity_type || '',
    startTime:    e.startTime   || (e.start_time ? String(e.start_time).slice(0,5) : ''),
    endTime:      e.endTime     || (e.end_time   ? String(e.end_time).slice(0,5)   : ''),
    actBg:    a(e.activityType || e.activity_type).bg,
    actColor: a(e.activityType || e.activity_type).color,
    dotColor: a(e.activityType || e.activity_type).dot,
    tlColor:  a(e.activityType || e.activity_type).tl,
    durationH: e.durationH || (e.duration ? parseFloat(e.duration) : 0),
  })
  return [
    ...liveEntries.value.map(enrich),
    ...historicalRaw.value.map(enrich),
  ]
})

/* ── inline edit state ─────────────────────────────────────── */
const editingId = ref(null)
const editDraft = ref({})

function startEdit(e) {
  editingId.value = e.id
  editDraft.value = { project: e.project, activityType: e.activityType, description: e.desc, startTime: e.startTime, endTime: e.endTime }
}
function saveEdit(id) {
  storeUpdate(id, { ...editDraft.value, description: editDraft.value.description })
  editingId.value = null
}
function cancelEdit() { editingId.value = null }

const actTypes = ['Development','Meeting','Learning','Research','Testing','Documentation','Bug Fixing','Deployment','Support']

/* ── state ─────────────────────────────────────────────────── */
const periods      = ['Today', 'This Week', 'This Month']
const activePeriod = ref('Today')
const selectedDate = ref(today)

/* ── date range helpers ────────────────────────────────────── */
function weekStart(iso) {
  const d = new Date(iso)
  d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1))
  return toISO(d)
}
function monthStart(iso) { return iso.slice(0, 7) + '-01' }

/* ── filtered entries ──────────────────────────────────────── */
const filteredEntries = computed(() => {
  const t   = today.value
  const all = allEntries.value
  if (activePeriod.value === 'Today')      return all.filter(e => e.date === t)
  if (activePeriod.value === 'This Week')  return all.filter(e => e.date >= weekStart(t) && e.date <= t)
  if (activePeriod.value === 'This Month') return all.filter(e => e.date >= monthStart(t) && e.date <= t)
  return all.filter(e => e.date === selectedDate.value)
})

/* ── stats (computed from filtered entries) ────────────────── */
const stats = computed(() => {
  const entries  = filteredEntries.value
  const totalH   = entries.reduce((s, e) => s + e.durationH, 0)
  const projects = new Set(entries.map(e => e.project)).size
  const label    = activePeriod.value === 'Today' ? 'Today' : activePeriod.value === 'Custom' ? 'Period' : activePeriod.value
  return [
    { label: `Hours (${label})`, value: totalH.toFixed(1) + 'h', sub: entries.length + ' entries' },
    { label: 'Projects',         value: String(projects),        sub: 'Active this period' },
  ]
})

/* ── timeline (day view only when single date selected) ─────── */
const DAY_START = 8 * 60   // 08:00
const DAY_SPAN  = 12 * 60  // 8:00 → 20:00

const timelineBlocks = computed(() => {
  const singleDay = activePeriod.value === 'Today' || activePeriod.value === 'Custom'
  if (!singleDay) return []
  return filteredEntries.value.map(e => {
    const start = toMinutes(e.startTime)
    const end   = toMinutes(e.endTime)
    const left  = Math.max(0, ((start - DAY_START) / DAY_SPAN) * 100)
    const width = Math.min(100 - left, ((end - start) / DAY_SPAN) * 100)
    return {
      id:    e.id,
      label: e.activity,
      color: e.tlColor,
      left:  left.toFixed(2) + '%',
      width: width.toFixed(2) + '%',
      title: `${e.activity} ${e.startTime}–${e.endTime} · ${e.project}`,
    }
  })
})

const isDayView = computed(() =>
  activePeriod.value === 'Today' || activePeriod.value === 'Custom'
)


const timelineTitle = computed(() => {
  if (activePeriod.value === 'Today')       return "Today's"
  if (activePeriod.value === 'This Week')   return 'This Week'
  if (activePeriod.value === 'This Month')  return 'This Month'
  return fmtDate(selectedDate.value) + "'s"
})

const entriesTitle = computed(() => {
  if (activePeriod.value === 'Today')  return "Today's Entries"
  if (activePeriod.value === 'Custom') return fmtDate(selectedDate.value) + ' Entries'
  return activePeriod.value + ' Entries'
})

const timeLabels = ['8:00','10:00','12:00','14:00','16:00','18:00','20:00']

/* ── actions ───────────────────────────────────────────────── */
function selectPeriod(p) {
  activePeriod.value = p
  if (p === 'Today') selectedDate.value = today.value
}

function selectSpecificDate() {
  activePeriod.value = 'Custom'
}

/* ── grouped entries (by date) ─────────────────────────────── */
const groupedEntries = computed(() => {
  const map = {}
  for (const e of filteredEntries.value) {
    if (!map[e.date]) map[e.date] = []
    map[e.date].push(e)
  }
  return Object.entries(map)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, entries]) => {
      const totalHours = entries.reduce((s, e) => s + e.durationH, 0)
      const statuses   = entries.map(e => e.status)
      const dayStatus  = statuses.every(s => s === 'Approved') ? 'Approved'
                       : statuses.every(s => s === 'Rejected') ? 'Rejected'
                       : statuses.some(s => s === 'Submitted') ? 'Submitted'
                       : 'Draft'
      return { date, entries, totalHours, dayStatus }
    })
})

async function submitDay(date) {
  await storeSubmitDay(date)
}
async function approveDay(date) {
  const emp = viewingEmployee.value?.id || ''
  await api.approveDay(date, emp)
  liveEntries.value
    .filter(e => e.date === date)
    .forEach(e => { e.status = 'Approved' })
}

function fmtDate(iso) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-GB', { day:'numeric', month:'short' })
}

function statusPill(s) {
  return { 'pill-green': s==='Approved', 'pill-blue': s==='Submitted', 'pill-amber': s==='Draft', 'pill-red': s==='Rejected' }
}
</script>

<style scoped>
.timeline-track {
  @apply relative h-[42px] rounded-lg overflow-hidden mb-2;
  background: var(--color-background-secondary);
}
.tl-block {
  @apply absolute h-full rounded-md flex items-center px-2 text-[10px] font-medium text-white cursor-pointer transition-[filter] duration-150 overflow-hidden whitespace-nowrap;
}
.tl-block:hover { @apply brightness-90; }
.tl-empty {
  @apply h-[42px] rounded-lg flex items-center justify-center text-[11px] mb-2;
  background: var(--color-background-secondary);
  color: var(--color-text-tertiary);
}
.timeline-labels {
  @apply flex justify-between text-[10px] px-[2px];
  color: var(--color-text-tertiary);
}
.empty-entries {
  @apply rounded-lg p-7 text-center text-[12px] flex items-center justify-center gap-2;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  color: var(--color-text-tertiary);
}
.day-group { @apply mb-[14px]; }
.day-header {
  @apply flex items-center justify-between px-[14px] py-[7px];
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: 6px 6px 0 0;
}
.day-header-left  { @apply flex items-center gap-[10px]; }
.day-label        { @apply text-[12px] font-semibold; color: var(--color-text-primary); }
.day-total        { @apply text-[11px]; color: var(--color-text-tertiary); }
.day-header-right { @apply flex items-center gap-[6px]; }
.day-group .entry-list { @apply mb-0; border-radius: 0 0 8px 8px; }
.mini-act-btn {
  @apply inline-flex items-center gap-1 px-[10px] py-1 rounded-md text-[11px] font-medium cursor-pointer transition-opacity duration-150;
  border: 0.5px solid;
  font-family: var(--font-sans);
}
.mini-act-btn:hover { @apply opacity-80; }
.submit-btn  { @apply bg-[#E6F1FB] text-[#185FA5] border-[#b3d4f7]; }
.approve-btn { @apply bg-[#EAF3DE] text-[#3B6D11] border-[#C0DD97]; }
.reject-btn  { @apply bg-[#FCEBEB] text-[#A32D2D] border-[#F7C1C1]; }
.entry-draft { @apply bg-[#fffdf5]; }
.entry-actions {
  @apply flex gap-[5px] items-center;
  grid-column: 6;
}
.entry-act-btn {
  @apply inline-flex items-center gap-1 px-2 py-[3px] rounded-[5px] text-[10.5px] font-medium cursor-pointer transition-opacity duration-150;
  border: 0.5px solid;
  font-family: var(--font-sans);
}
.entry-act-btn:hover { @apply opacity-80; }
.edit-btn { @apply bg-[#F4F5F6] text-[#4B5563] border-[#d1d5db]; }
.inline-edit {
  @apply bg-[#f8fafc] px-[14px] py-3 pl-[30px];
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.ie-grid {
  @apply grid gap-[10px] mb-[10px];
  grid-template-columns: 1fr 1fr 120px 120px;
}
.ie-actions { @apply flex gap-2 justify-end; }
</style>
