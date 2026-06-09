<template>
  <div>
    <div class="section-title">Notifications</div>
    <div class="notif-card" style="margin-top:10px">
      <div
        v-for="n in notifications"
        :key="n.id"
        class="notif-row"
        @click="markRead(n)"
      >
        <div class="notif-icon" :style="{ background: n.iconBg }">
          <i :class="`ti ti-${n.icon}`" :style="{ color: n.iconColor, fontSize: '16px' }" aria-hidden="true"></i>
        </div>
        <div style="flex:1">
          <div class="notif-title">{{ n.title }}</div>
          <div class="notif-body">{{ n.body }}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
          <div class="notif-time">{{ n.time }}</div>
          <div v-if="n.unread" class="unread-dot"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const notifications = ref([
  {
    id: 1, unread: false,
    icon: 'check', iconBg: '#EAF3DE', iconColor: '#3B6D11',
    title: 'Timesheet Approved',
    body: 'Your May 28 timesheet was approved by HR Admin',
    time: '2h ago',
  },
  {
    id: 2, unread: true,
    icon: 'x', iconBg: '#FCEBEB', iconColor: '#A32D2D',
    title: 'Timesheet Rejected',
    body: 'May 27 entry rejected: "Please add more detail to descriptions"',
    time: '5h ago',
  },
  {
    id: 3, unread: true,
    icon: 'bell', iconBg: '#FAEEDA', iconColor: '#854F0B',
    title: 'Submission Reminder',
    body: "Don't forget to submit today's timesheet before 6 PM",
    time: '1h ago',
  },
  {
    id: 4, unread: true,
    icon: 'alert-circle', iconBg: '#EEEDFE', iconColor: '#534AB7',
    title: 'Missing Timesheet',
    body: 'No entry found for May 26 (Monday). Please fill it in.',
    time: 'Yesterday',
  },
])

function markRead(n) {
  n.unread = false
}
</script>
