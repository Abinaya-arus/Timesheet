import { ref } from 'vue'
import { api } from '../api/index.js'

// Reactive cache of today's entries — loaded from Frappe on mount
const liveEntries = ref([])
const loading     = ref(false)

export function useEntries() {
  async function fetchTodayEntries() {
    loading.value = true
    try {
      const today = new Date().toISOString().slice(0, 10)
      const data  = await api.getEntries({ date: today })
      liveEntries.value = (data || []).map(normalise)
    } catch (e) {
      console.error('fetchTodayEntries', e)
    } finally {
      loading.value = false
    }
  }

  async function addEntry(entry) {
    const saved = await api.createEntry(entry)
    liveEntries.value.push(normalise({ ...entry, ...saved }))
  }

  async function updateEntry(name, updates) {
    await api.updateEntry(name, updates)
    const e = liveEntries.value.find(x => x.id === name || x.name === name)
    if (e) Object.assign(e, updates)
  }

  async function submitEntry(name) {
    await api.submitEntry(name)
    const e = liveEntries.value.find(x => x.id === name || x.name === name)
    if (e) e.status = 'Submitted'
  }

  async function submitDay(date) {
    await api.submitDay(date)
    liveEntries.value
      .filter(e => e.date === date && e.status === 'Draft')
      .forEach(e => { e.status = 'Submitted' })
  }

  async function deleteEntryById(name) {
    await api.deleteEntry(name)
    liveEntries.value = liveEntries.value.filter(e => (e.id || e.name) !== name)
  }

  return { liveEntries, loading, fetchTodayEntries, addEntry, updateEntry, submitEntry, submitDay, deleteEntryById }
}

function normalise(e) {
  return {
    id:           e.name || e.id,
    name:         e.name || e.id,
    date:         e.date,
    startTime:    e.start_time || e.startTime || '',
    endTime:      e.end_time   || e.endTime   || '',
    activityType: e.activity_type || e.activityType || '',
    project:      e.project || '',
    description:  e.description || '',
    status:       e.status || 'Draft',
    durationH:    e.duration || 0,
  }
}
