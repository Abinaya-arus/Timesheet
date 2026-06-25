<template>
  <div>
    <!-- Add new project -->
    <div class="add-row">
      <input
        class="form-input"
        v-model="newProject"
        placeholder="New project name…"
        @keyup.enter="handleAdd"
        style="max-width:300px"
      >
      <button class="btn btn-primary" @click="handleAdd">
        <i class="ti ti-plus" aria-hidden="true"></i> Add Project
      </button>
    </div>

    <!-- Project list -->
    <div v-if="projects.length === 0" class="empty-entries">
      <i class="ti ti-briefcase-off" aria-hidden="true"></i> No projects yet.
    </div>
    <div v-else class="entry-list">
      <div class="project-row" v-for="p in projects" :key="p">
        <div v-if="editingProject !== p" class="proj-name-cell">
          <i class="ti ti-briefcase" aria-hidden="true" style="color:var(--color-text-tertiary);font-size:15px"></i>
          <span>{{ p }}</span>
        </div>
        <input
          v-else
          class="form-input"
          v-model="editName"
          style="flex:1;max-width:300px"
          @keyup.enter="saveEdit(p)"
          @keyup.escape="cancelEdit"
        >
        <div class="proj-actions">
          <template v-if="editingProject !== p">
            <button class="proj-btn edit-btn" @click="startEdit(p)" title="Rename">
              <i class="ti ti-pencil" aria-hidden="true"></i>
            </button>
            <button class="proj-btn del-btn" @click="handleDelete(p)" title="Delete">
              <i class="ti ti-trash" aria-hidden="true"></i>
            </button>
          </template>
          <template v-else>
            <button class="proj-btn save-btn" @click="saveEdit(p)">
              <i class="ti ti-check" aria-hidden="true"></i>
            </button>
            <button class="proj-btn cancel-btn" @click="cancelEdit">
              <i class="ti ti-x" aria-hidden="true"></i>
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProjects } from '../stores/projects.js'

const { projects, fetchProjects, addProject, deleteProject, renameProject } = useProjects()
onMounted(fetchProjects)

const newProject     = ref('')
const editingProject = ref(null)
const editName       = ref('')

function handleAdd() {
  if (!newProject.value.trim()) return
  addProject(newProject.value)
  newProject.value = ''
}
function handleDelete(name) {
  if (confirm(`Delete project "${name}"?`)) deleteProject(name)
}
function startEdit(name) { editingProject.value = name; editName.value = name }
function saveEdit(oldName) {
  const t = editName.value.trim()
  if (t && t !== oldName) renameProject(oldName, t)
  editingProject.value = null
}
function cancelEdit() { editingProject.value = null }
</script>

<style scoped>
.add-row { @apply flex items-center gap-[10px] mb-4; }
.project-row {
  @apply flex items-center justify-between px-[14px] py-[10px] gap-3;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.project-row:last-child { border-bottom: none; }
.proj-name-cell { @apply flex items-center gap-[10px] flex-1 text-[13px]; color: var(--color-text-primary); }
.proj-actions   { @apply flex gap-[5px] flex-shrink-0; }
.proj-btn {
  @apply w-[26px] h-[26px] rounded-[5px] flex items-center justify-center cursor-pointer text-[13px] transition-opacity duration-150;
  border: 0.5px solid var(--color-border-tertiary);
  background: var(--color-background-secondary);
  color: var(--color-text-secondary);
}
.proj-btn:hover  { @apply opacity-75; }
.edit-btn        { @apply text-[#185FA5] bg-[#E6F1FB] border-[#b3d4f7]; }
.del-btn         { @apply text-[#A32D2D] bg-[#FCEBEB] border-[#F7C1C1]; }
.save-btn        { @apply text-[#3B6D11] bg-[#EAF3DE] border-[#C0DD97]; }
.cancel-btn      { @apply text-[#854F0B] bg-[#FAEEDA] border-[#f0cc9a]; }
.empty-entries {
  @apply rounded-lg p-7 text-center text-[12px] flex items-center justify-center gap-2;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  color: var(--color-text-tertiary);
}
</style>
