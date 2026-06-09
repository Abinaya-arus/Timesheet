const BASE = '/api/method/timesheet_manager'

async function call(method, params = {}) {
  const csrf = window.csrf_token
    || document.cookie.split('; ').find(r => r.startsWith('csrf_token='))?.split('=')[1]
    || 'fetch'
  const res = await fetch(`${BASE}.${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': csrf,
    },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data.exc) throw new Error(data.exc)
  return data.message
}

async function get(method, params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).map(([k, v]) => [k, typeof v === 'object' ? JSON.stringify(v) : v])
    )
  ).toString()
  const res = await fetch(`${BASE}.${method}${query ? '?' + query : ''}`, {
    method: 'GET',
    headers: { 'X-Frappe-CSRF-Token': window.csrf_token || 'fetch' },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data.exc) throw new Error(data.exc)
  return data.message
}

export const api = {
  // ── Auth ──────────────────────────────────────────────────
  getCurrentUser: ()                    => get('api.get_current_user'),

  // ── Timesheet entries ─────────────────────────────────────
  getEntries:     (filters = {})        => get('api.get_entries', filters),
  createEntry:    (entry)               => call('api.create_entry', entry),
  updateEntry:    (name, data)          => call('api.update_entry', { name, ...data }),
  submitEntry:    (name)                => call('api.submit_entry', { name }),
  submitDay:      (date)                => call('api.submit_day', { date }),
  approveDay:     (date, employee)      => call('api.approve_day', { date, employee }),
  deleteEntry:    (name)                => call('api.delete_entry', { name }),

  // ── Dashboard stats ───────────────────────────────────────
  getDashboardStats: (date, employee)   => get('api.get_dashboard_stats', { date, employee: employee || '' }),

  // ── Analytics ─────────────────────────────────────────────
  getAnalytics:   (period, date)        => get('api.get_analytics', { period, date }),

  // ── Admin ─────────────────────────────────────────────────
  getEmployees:   ()                    => get('api.get_employees'),
  getAdminOverview: ()                  => get('api.get_admin_overview'),
  getPendingApprovals: ()               => get('api.get_pending_approvals'),

  // ── Notifications ─────────────────────────────────────────
  getNotifications: ()                  => get('api.get_notifications'),
  markRead:       (name)                => call('api.mark_notification_read', { name }),

  // ── Projects ─────────────────────────────────────────────
  getProjects:    ()                    => get('api.get_projects'),
  addProject:     (name)                => call('api.add_project', { name }),
  deleteProject:  (name)                => call('api.delete_project', { name }),
  renameProject:  (old_name, new_name)  => call('api.rename_project', { old_name, new_name }),
  getProjectHours: ()                   => get('api.get_project_hours'),
}
