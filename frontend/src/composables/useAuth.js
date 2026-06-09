import { ref, computed } from 'vue'
import { api } from '../api/index.js'

const currentUser = ref({
  name: '',
  email: '',
  initials: '',
  role: 'employee',   // 'employee' | 'admin'
  loaded: false,
})

const viewingEmployee = ref(null)

// Fetch logged-in user from Frappe on first call
let fetchPromise = null
export async function loadCurrentUser() {
  if (currentUser.value.loaded) return
  if (fetchPromise) return fetchPromise

  fetchPromise = api.getCurrentUser().then(user => {
    currentUser.value = {
      name:     user.full_name || user.name,
      email:    user.name,
      initials: initials(user.full_name || user.name),
      role:     user.is_admin ? 'admin' : 'employee',
      loaded:   true,
    }
  }).catch(() => {
    // Dev fallback — check localStorage for role override
    const devRole = localStorage.getItem('dev_role') || 'employee'
    currentUser.value = {
      name:     devRole === 'admin' ? 'HR Admin' : 'John Dev',
      email:    devRole === 'admin' ? 'admin@example.com' : 'john@example.com',
      initials: devRole === 'admin' ? 'HA' : 'JD',
      role:     devRole,
      loaded:   true,
    }
  })
  return fetchPromise
}

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

export function useAuth() {
  const isAdmin    = () => currentUser.value.role === 'admin'
  const isEmployee = () => currentUser.value.role === 'employee'

  const showEmployeeNav = computed(() =>
    currentUser.value.role === 'employee' || viewingEmployee.value !== null
  )

  return { currentUser, isAdmin, isEmployee, viewingEmployee, showEmployeeNav }
}
