import { ref } from 'vue'
import { api } from '../api/index.js'

const projects = ref([])
let loaded = false

export function useProjects() {
  async function fetchProjects() {
    if (loaded) return
    try {
      const data = await api.getProjects()
      projects.value = data || []
      loaded = true
    } catch (e) {
      console.error('fetchProjects', e)
    }
  }

  async function addProject(name) {
    const trimmed = name.trim()
    if (!trimmed || projects.value.includes(trimmed)) return
    await api.addProject(trimmed)
    projects.value.push(trimmed)
  }

  async function deleteProject(name) {
    await api.deleteProject(name)
    projects.value = projects.value.filter(p => p !== name)
  }

  async function renameProject(oldName, newName) {
    const trimmed = newName.trim()
    if (!trimmed || projects.value.includes(trimmed)) return
    await api.renameProject(oldName, trimmed)
    const idx = projects.value.indexOf(oldName)
    if (idx !== -1) projects.value[idx] = trimmed
  }

  return { projects, fetchProjects, addProject, deleteProject, renameProject }
}
