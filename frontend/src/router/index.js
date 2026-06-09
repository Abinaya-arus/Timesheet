import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import NewEntry from '../views/NewEntry.vue'
import Analytics from '../views/Analytics.vue'
import Notifications from '../views/Notifications.vue'
import AdminPanel from '../views/AdminPanel.vue'
import Approvals from '../views/Approvals.vue'
import Projects from '../views/Projects.vue'
import ProjectList from '../views/ProjectList.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard',     component: Dashboard,     meta: { title: 'Dashboard' } },
    { path: '/entry',         component: NewEntry,      meta: { title: 'New Entry' } },
    { path: '/analytics',     component: Analytics,     meta: { title: 'Analytics' } },
    { path: '/notifications', component: Notifications, meta: { title: 'Notifications' } },
    { path: '/admin',         component: AdminPanel,    meta: { title: 'Admin Panel' } },
    { path: '/approvals',     component: Approvals,     meta: { title: 'Approvals' } },
    { path: '/project-hours', component: Projects,     meta: { title: 'Project Hours' } },
    { path: '/projects',      component: ProjectList,  meta: { title: 'Projects' } },
  ],
})
