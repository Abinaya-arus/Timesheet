<template>
  <div>
    <!-- Employee Overview -->
    <div class="section-title" style="margin-bottom:10px">Employee Overview</div>
    <div class="entry-list" style="margin-bottom:20px">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Department</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="employees.length === 0">
            <td colspan="2" style="text-align:center;color:var(--color-text-tertiary);padding:16px">
              Loading employees…
            </td>
          </tr>
          <tr v-for="(emp, i) in employees" :key="emp.id" @click="viewEmployee(emp, i)">
            <td>
              <div class="emp-cell">
                <div class="avatar"
                  :style="{ background: avatarColor(i).bg, color: avatarColor(i).color }"
                  style="width:24px;height:24px;font-size:10px">
                  {{ emp.initials }}
                </div>
                {{ emp.name }}
              </div>
            </td>
            <td style="color:var(--color-text-secondary)">{{ emp.dept }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { api } from '../api/index.js'

const { viewingEmployee } = useAuth()
const router = useRouter()

const employees = ref([])

onMounted(async () => {
  try {
    employees.value = await api.getEmployees() || []
  } catch (e) {
    console.error('getEmployees', e)
  }
})

const AVATAR_COLORS = [
  { bg:'#E6F1FB', color:'#185FA5' }, { bg:'#EAF3DE', color:'#3B6D11' },
  { bg:'#FAEEDA', color:'#854F0B' }, { bg:'#FCEBEB', color:'#A32D2D' },
  { bg:'#EEEDFE', color:'#534AB7' },
]
function avatarColor(i) { return AVATAR_COLORS[i % AVATAR_COLORS.length] }

function viewEmployee(emp, idx) {
  viewingEmployee.value = { name: emp.name, initials: emp.initials, id: emp.id }
  router.push('/dashboard')
}

</script>

<style scoped>
.emp-cell { @apply flex items-center gap-2; }
</style>
