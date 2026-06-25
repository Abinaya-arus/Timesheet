<template>
  <div>
    <div class="form-card">
      <div class="section-title" style="margin-bottom:14px">New Timesheet Entry</div>

      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Date</label>
          <input type="date" class="form-input" v-model="form.date">
        </div>
        <div class="form-group">
          <label class="form-label">Project</label>
          <select class="form-input" v-model="form.project">
            <option value="" disabled>Select a project</option>
            <option v-for="p in projects" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
      </div>

      <!-- Time sliders -->
      <div class="time-sliders">
        <div class="slider-group">
          <div class="slider-header">
            <span class="form-label">Start Time</span>
            <span class="slider-time">{{ formatAmPm(startMinutes) }}</span>
          </div>
          <input type="range" class="time-slider" min="0" max="1410" step="30"
            :value="startMinutes" @input="onStartSlide">
          <div class="slider-ticks">
            <span v-for="t in timeTicks" :key="t">{{ t }}</span>
          </div>
        </div>

        <div class="slider-group">
          <div class="slider-header">
            <span class="form-label">End Time</span>
            <span class="slider-time">{{ formatAmPm(endMinutes) }}</span>
          </div>
          <input type="range" class="time-slider" min="0" max="1410" step="30"
            :value="endMinutes" @input="onEndSlide">
          <div class="slider-ticks">
            <span v-for="t in timeTicks" :key="t">{{ t }}</span>
          </div>
        </div>

        <div class="duration-badge">
          <i class="ti ti-clock" aria-hidden="true"></i> {{ duration }}
        </div>
      </div>

      <div class="form-label" style="margin-bottom:6px">Activity Type</div>
      <div class="act-grid">
        <div
          v-for="act in activityTypes"
          :key="act"
          class="act-btn"
          :class="{ selected: form.activityType === act }"
          @click="form.activityType = act"
        >{{ act }}</div>
      </div>

      <div class="form-group" style="margin-bottom:12px">
        <label class="form-label">Description</label>
        <textarea
          class="form-input auto-expand"
          rows="2"
          placeholder="What did you work on?"
          v-model="form.description"
          @input="autoExpand"
          ref="descRef"
        ></textarea>
      </div>

      <div class="form-footer">
        <label class="task-check">
          <input type="checkbox" v-model="form.taskCompleted"> Task Completed
        </label>
        <button class="btn btn-primary" @click="saveDraft">
          <i class="ti ti-device-floppy" aria-hidden="true"></i> Save Draft
        </button>
      </div>
    </div>

    <div class="autosave-hint">
      <i class="ti ti-device-floppy" aria-hidden="true"></i> Auto-saving draft every 30 seconds
    </div>

    <!-- Today's entries -->
    <div style="margin-top:20px">
      <div class="section-title">Today's Entries</div>
      <div v-if="todayEntries.length === 0" class="empty-state">
        <i class="ti ti-clock-off" aria-hidden="true"></i>
        No entries added yet today.
      </div>
      <div v-else class="entry-list">
        <div class="entry-row" v-for="e in todayEntries" :key="e.id">
          <div class="status-dot" :style="{ background: statusDotColor(e.status) }"></div>
          <div class="entry-time">{{ e.startTime }} – {{ e.endTime }}</div>
          <span class="badge" :style="{ background: actBg(e.activityType), color: actColor(e.activityType) }">{{ e.activityType }}</span>
          <div class="entry-project">{{ e.project }}</div>
          <div class="entry-desc">{{ e.description || '' }}</div>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="badge" :class="statusPill(e.status)">{{ e.status }}</span>
            <button v-if="e.status === 'Draft'" class="icon-btn" title="Delete" @click="deleteEntry(e.id)">
              <i class="ti ti-trash" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEntries } from '../stores/entries.js'
import { useProjects } from '../stores/projects.js'

const { liveEntries, addEntry, fetchTodayEntries } = useEntries()
const { projects, fetchProjects } = useProjects()

onMounted(() => { fetchTodayEntries(); fetchProjects() })

const descRef = ref(null)

function autoExpand(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

const activityTypes = ['Development','Meeting','Learning','Research','Testing','Documentation','Bug Fixing','Deployment','Support']

const activityColors = {
  Development:   { bg: '#E6F1FB', color: '#185FA5' },
  Meeting:       { bg: '#FCEBEB', color: '#A32D2D' },
  Learning:      { bg: '#EAF3DE', color: '#3B6D11' },
  Research:      { bg: '#EEEDFE', color: '#534AB7' },
  Testing:       { bg: '#FFF4E5', color: '#854F0B' },
  Documentation: { bg: '#F4F5F6', color: '#4B5563' },
  'Bug Fixing':  { bg: '#FCEBEB', color: '#A32D2D' },
  Deployment:    { bg: '#EAF3DE', color: '#3B6D11' },
  Support:       { bg: '#EEEDFE', color: '#534AB7' },
}

/* ── helpers ───────────────────────────────────────────────── */
function minsToHHMM(m) {
  const h = Math.floor(m / 60).toString().padStart(2, '0')
  const min = (m % 60).toString().padStart(2, '0')
  return `${h}:${min}`
}
function formatAmPm(mins) {
  const h   = Math.floor(mins / 60)
  const m   = mins % 60
  const ampm = h < 12 ? 'AM' : 'PM'
  const h12  = h % 12 === 0 ? 12 : h % 12
  return `${h12}:${m.toString().padStart(2,'0')} ${ampm}`
}
const timeTicks  = ['12 AM','6 AM','12 PM','6 PM','11 PM']

/* ── slider state ──────────────────────────────────────────── */
const startMinutes = ref(9 * 60)   // 9:00 AM
const endMinutes   = ref(11 * 60)  // 11:00 AM

function onStartSlide(e) {
  startMinutes.value = +e.target.value
  form.value.startTime = minsToHHMM(startMinutes.value)
  if (endMinutes.value <= startMinutes.value)
    endMinutes.value = startMinutes.value + 30
  form.value.endTime = minsToHHMM(endMinutes.value)
}
function onEndSlide(e) {
  endMinutes.value = +e.target.value
  form.value.endTime = minsToHHMM(endMinutes.value)
  if (endMinutes.value <= startMinutes.value)
    startMinutes.value = Math.max(0, endMinutes.value - 30)
  form.value.startTime = minsToHHMM(startMinutes.value)
}

const form = ref({
  date: new Date().toISOString().slice(0, 10),
  project: '',
  startTime: '09:00',
  endTime: '11:00',
  activityType: 'Development',
  description: '',
  taskCompleted: true,
})

const duration = computed(() => {
  const diff = endMinutes.value - startMinutes.value
  if (diff <= 0) return '0h 0m'
  return `${Math.floor(diff / 60)}h ${diff % 60}m`
})

const todayEntries = liveEntries   // shared store

function actBg(type)    { return activityColors[type]?.bg    ?? '#F4F5F6' }
function actColor(type) { return activityColors[type]?.color ?? '#4B5563' }

function statusDotColor(status) {
  return { Approved:'#639922', Submitted:'#378ADD', Draft:'#BA7517', Rejected:'#E24B4A' }[status] ?? '#9ca3af'
}
function statusPill(status) {
  return { 'pill-green': status==='Approved', 'pill-blue': status==='Submitted', 'pill-amber': status==='Draft', 'pill-red': status==='Rejected' }
}

function saveDraft() {
  if (!form.value.project) { alert('Please enter a project name.'); return }
  addEntry({ ...form.value, duration: duration.value, status: 'Draft' })
  resetForm()
}


function deleteEntry(id) {
  liveEntries.value = liveEntries.value.filter(e => e.id !== id)
}

function resetForm() {
  form.value.project       = ''
  form.value.description   = ''
  form.value.activityType  = 'Development'
  form.value.taskCompleted = true
}
</script>

<style scoped>
.act-grid {
  @apply grid grid-cols-3 gap-[6px] mb-3;
}
.act-btn {
  @apply py-[7px] rounded-md text-[11px] text-center cursor-pointer transition-all duration-150;
  border: 0.5px solid var(--color-border-tertiary);
  background: var(--color-background-secondary);
  color: var(--color-text-secondary);
}
.act-btn:hover,
.act-btn.selected {
  @apply border-[#378ADD] bg-[#E6F1FB] text-[#0C447C] font-medium;
}
.form-footer { @apply flex items-center justify-between; }
.task-check  { @apply flex items-center gap-[6px] text-[12px] cursor-pointer; color: var(--color-text-secondary); }
.time-sliders {
  @apply flex flex-col gap-[14px] mb-[14px] p-[14px] rounded-md;
  background: var(--color-background-secondary);
}
.slider-group  { @apply flex flex-col gap-[6px]; }
.slider-header { @apply flex items-center justify-between; }
.slider-time {
  @apply text-[13px] font-semibold px-[10px] py-[2px] rounded-[20px];
  color: var(--color-text-info);
  background: var(--color-background-info);
}
.time-slider {
  @apply w-full outline-none cursor-pointer rounded;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--color-border-secondary);
}
.time-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  @apply w-[18px] h-[18px] rounded-full cursor-pointer transition-colors duration-150;
  background: #378ADD;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.2);
}
.time-slider::-webkit-slider-thumb:hover { background: #185fa5; }
.slider-ticks {
  @apply flex justify-between text-[9px] px-[2px];
  color: var(--color-text-tertiary);
}
.duration-badge {
  @apply inline-flex items-center gap-[5px] self-end text-[12px] font-medium px-3 py-[3px] rounded-[20px];
  color: var(--color-text-info);
  background: var(--color-background-info);
}
.auto-expand { @apply resize-none overflow-hidden min-h-[60px]; }
.autosave-hint {
  @apply flex items-center gap-[6px] text-[11px] mt-2;
  color: var(--color-text-tertiary);
}
.empty-state {
  @apply rounded-lg p-6 text-center text-[12px] flex items-center justify-center gap-2;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  color: var(--color-text-tertiary);
}
.empty-state i { @apply text-[16px]; }
.icon-btn {
  @apply bg-transparent border-0 cursor-pointer px-1 py-[2px] rounded text-[14px] flex-shrink-0 transition-colors duration-150;
  color: var(--color-text-tertiary);
}
.icon-btn:hover { @apply text-[#A32D2D]; }
</style>
