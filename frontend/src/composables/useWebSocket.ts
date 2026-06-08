import { onMounted, onUnmounted, ref } from 'vue'
import { useArticlesStore } from '../stores/articles'

export const toastMessage = ref<string | null>(null)
let toastTimer: number | null = null

function showToast(msg: string, duration = 6000) {
  toastMessage.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => { toastMessage.value = null }, duration)
}

export function useWebSocket() {
  const articles = useArticlesStore()
  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null

  function connect() {
    const token = localStorage.getItem('token')
    if (!token) return

    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = import.meta.env.VITE_WS_URL
      ? `${import.meta.env.VITE_WS_URL}/ws?token=${token}`
      : `${proto}//${location.host}/ws?token=${token}`
    ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_article') {
        articles.prependArticle(data.article)
      } else if (data.type === 'cookie_expired') {
        showToast(data.message)
        if (Notification.permission === 'granted') {
          new Notification('聚流', { body: data.message })
        }
      }
    }

    ws.onclose = (event) => {
      // Don't reconnect on auth failure (4001) or missing token
      if (event.code === 4001 || !localStorage.getItem('token')) return
      reconnectTimer = window.setTimeout(connect, 5000)
    }
  }

  onMounted(connect)
  onUnmounted(() => {
    if (ws) {
      // Detach onclose first: close() dispatches its event asynchronously,
      // so leaving the handler attached would schedule a reconnect that
      // outlives the component (a zombie, self-reconnecting socket).
      ws.onclose = null
      ws.close()
    }
    if (reconnectTimer) clearTimeout(reconnectTimer)
  })
}
