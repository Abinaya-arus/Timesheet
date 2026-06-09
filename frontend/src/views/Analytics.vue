<template>
  <div>
    <div class="tab-bar">
      <div
        v-for="t in tabs"
        :key="t"
        class="tab"
        :class="{ active: activeTab === t }"
        @click="activeTab = t"
      >{{ t }}</div>
    </div>

    <!-- Activity & Project breakdown (all tabs) -->
    <div class="analytics-grid">
      <div class="chart-card">
        <div class="section-title">Activity Breakdown</div>
        <div class="bar-row" v-for="a in current.activity" :key="a.label">
          <div class="bar-label">{{ a.label }}</div>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: a.pct + '%', background: a.color }"></div>
          </div>
          <div class="bar-val">{{ a.val }}</div>
        </div>
      </div>

      <div class="chart-card">
        <div class="section-title">Project Hours</div>
        <div class="bar-row" v-for="p in current.projects" :key="p.label">
          <div class="bar-label">{{ p.label }}</div>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: p.pct + '%', background: p.color }"></div>
          </div>
          <div class="bar-val">{{ p.val }}</div>
        </div>
      </div>
    </div>

    <!-- Daily: simple 8h goal progress bar -->
    <div v-if="activeTab === 'Daily'" class="chart-card">
      <div class="goal-row">
        <span class="goal-label">Daily Goal</span>
        <div class="goal-track">
          <div class="goal-fill" :style="{ width: goalPct + '%', background: goalPct >= 100 ? '#639922' : '#378ADD' }"></div>
        </div>
        <span class="goal-text">{{ workedHours }}h / 8h</span>
      </div>
    </div>

    <!-- Weekly / Monthly: Frappe donut — hours worked per day/week -->
    <div v-else class="chart-card">
      <div class="donut-header">
        <div class="section-title" style="margin-bottom:0">Hours Worked — {{ activeTab }}</div>
        <div class="donut-total">Total <strong>{{ current.totalHours }}h</strong></div>
      </div>
      <div ref="chartEl" class="frappe-chart-wrap"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Chart } from 'frappe-charts'

const tabs      = ['Daily', 'Weekly', 'Monthly']
const activeTab = ref('Daily')
const chartEl   = ref(null)
let   chartInst = null

const workedHours = ref(7.5)
const goalPct     = computed(() => Math.min(100, Math.round((workedHours.value / 8) * 100)))

/* ── data ──────────────────────────────────────────────────── */
const data = {
  Daily: {
    totalHours: 7.5,
    activity: [
      { label: 'Development', hours: 4,   color: '#378ADD' },
      { label: 'Meeting',     hours: 1,   color: '#E24B4A' },
      { label: 'Learning',    hours: 1,   color: '#639922' },
      { label: 'Research',    hours: 1.5, color: '#7F77DD' },
    ],
    projects: [
      { label: 'ERPNext Portal',  hours: 4.5, color: '#378ADD' },
      { label: 'Sprint Planning', hours: 1,   color: '#BA7517' },
      { label: 'AI Integration',  hours: 2,   color: '#7F77DD' },
    ],
  },
  Weekly: {
    totalHours: 36.5,
    chartLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    chartValues: [8.0, 7.5, 8.5, 7.5, 5.0],
    activity: [
      { label: 'Development', hours: 18,  color: '#378ADD' },
      { label: 'Meeting',     hours: 5,   color: '#E24B4A' },
      { label: 'Learning',    hours: 4.5, color: '#639922' },
      { label: 'Research',    hours: 5,   color: '#7F77DD' },
      { label: 'Testing',     hours: 4,   color: '#BA7517' },
    ],
    projects: [
      { label: 'ERPNext Portal',  hours: 18,  color: '#378ADD' },
      { label: 'AI Integration',  hours: 10,  color: '#7F77DD' },
      { label: 'Sprint Planning', hours: 5,   color: '#BA7517' },
      { label: 'Bug Tracker',     hours: 3.5, color: '#639922' },
    ],
  },
  Monthly: {
    totalHours: 148,
    chartLabels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    chartValues: [38, 40, 35, 35],
    activity: [
      { label: 'Development', hours: 72, color: '#378ADD' },
      { label: 'Meeting',     hours: 20, color: '#E24B4A' },
      { label: 'Testing',     hours: 22, color: '#BA7517' },
      { label: 'Research',    hours: 18, color: '#7F77DD' },
      { label: 'Learning',    hours: 16, color: '#639922' },
    ],
    projects: [
      { label: 'ERPNext Portal',  hours: 68, color: '#378ADD' },
      { label: 'AI Integration',  hours: 42, color: '#7F77DD' },
      { label: 'Sprint Planning', hours: 20, color: '#BA7517' },
      { label: 'Bug Tracker',     hours: 18, color: '#639922' },
    ],
  },
}

const current = computed(() => {
  const d    = data[activeTab.value]
  const maxA = Math.max(...d.activity.map(a => a.hours))
  const maxP = Math.max(...d.projects.map(p => p.hours))
  return {
    ...d,
    activity: d.activity.map(a => ({ ...a, pct: (a.hours / maxA) * 100, val: a.hours + 'h' })),
    projects: d.projects.map(p => ({ ...p, pct: (p.hours / maxP) * 100, val: p.hours + 'h' })),
  }
})

/* ── Frappe donut ──────────────────────────────────────────── */
function renderChart() {
  const tab = activeTab.value
  if (tab === 'Daily' || !chartEl.value) return

  if (chartEl.value) chartEl.value.innerHTML = ''
  chartInst = null

  const d = data[tab]
  chartInst = new Chart(chartEl.value, {
    type: 'donut',
    data: {
      labels:   d.chartLabels,
      datasets: [{ values: d.chartValues }],
    },
    colors:  ['#378ADD', '#5BB8E0', '#7ECCE6', '#A3DEF0', '#C5EDF8'],
    tooltipOptions: { formatTooltipY: v => v + 'h' },
    height: 240,
  })
}

watch(activeTab, async () => {
  await nextTick()
  renderChart()
})
</script>

<style scoped>
.productivity-row { display: flex; align-items: center; gap: 14px; }
.ring-wrap  { position: relative; width: 72px; height: 72px; flex-shrink: 0; }
.ring-wrap svg { position: absolute; top: 0; left: 0; }
.ring-center {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%); text-align: center;
}
.ring-val   { display: block; font-size: 15px; font-weight: 500; color: var(--color-text-primary); line-height: 1; }
.ring-lbl   { font-size: 9px; color: var(--color-text-tertiary); }
.ring-title { font-size: 13px; font-weight: 500; color: var(--color-text-primary); }
.ring-sub   { font-size: 11px; color: var(--color-text-secondary); margin-top: 2px; }

/* ── daily goal ────────────────────────────────────────────── */
.goal-row {
  display: flex; align-items: center; gap: 12px;
}
.goal-label {
  font-size: 12px; font-weight: 500;
  color: var(--color-text-secondary); white-space: nowrap;
}
.goal-track {
  flex: 1; height: 10px;
  background: var(--color-background-secondary);
  border-radius: 6px; overflow: hidden;
}
.goal-fill {
  height: 100%; border-radius: 6px;
  transition: width .4s ease, background .3s;
}
.goal-text {
  font-size: 12px; font-weight: 500;
  color: var(--color-text-primary); white-space: nowrap;
}

/* ── weekly / monthly donut ────────────────────────────────── */
.donut-header {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 4px;
}
.donut-total { font-size: 12px; color: var(--color-text-secondary); }
.frappe-chart-wrap { width: 100%; }

:deep(.frappe-chart text) {
  fill: var(--color-text-secondary) !important;
  font-family: var(--font-sans) !important;
  font-size: 11px !important;
}
:deep(.frappe-chart .legend-dataset-text) {
  fill: var(--color-text-secondary) !important;
}
</style>
