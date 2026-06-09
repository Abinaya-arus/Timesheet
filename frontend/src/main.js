import { createApp } from 'vue'
import router from './router/index.js'
import App from './App.vue'
import { loadCurrentUser } from './composables/useAuth.js'
import '@tabler/icons-webfont/dist/tabler-icons.css'
import './style.css'

loadCurrentUser().finally(() => {
  createApp(App).use(router).mount('#app')
})
