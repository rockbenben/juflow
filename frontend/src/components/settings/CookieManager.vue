<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'

interface CookieEntry {
  platform: string
  label: string
  cookie_string: string
  status: 'valid' | 'invalid' | 'unknown'
}

// Only scraper-based platforms actually use the user's cookie (scraper_base sets
// the Cookie header). RSSHub-based platforms (雪球/微博/小红书) ignore it, so
// listing them here would just be dead config.
const PLATFORMS = [
  { key: 'jisilu', label: '集思录' },
  { key: 'taoguba', label: '淘股吧' },
  { key: 'tonghuashun', label: '同花顺' },
  { key: 'jiuquaner', label: '韭圈儿' },
  { key: 'youzhiyouxing', label: '有知有行' },
]

const cookies = ref<Record<string, CookieEntry>>({})
const saving = ref<Record<string, boolean>>({})
const messages = ref<Record<string, string>>({})

onMounted(async () => {
  PLATFORMS.forEach(p => {
    cookies.value[p.key] = { platform: p.key, label: p.label, cookie_string: '', status: 'unknown' }
    saving.value[p.key] = false
    messages.value[p.key] = ''
  })
  try {
    const { data } = await api.get('/cookies/')
    if (Array.isArray(data)) {
      data.forEach((entry: { platform: string; is_valid: boolean; last_validated_at: string | null }) => {
        if (cookies.value[entry.platform]) {
          cookies.value[entry.platform].cookie_string = '(已保存)'
          cookies.value[entry.platform].status = entry.is_valid ? 'valid' : 'invalid'
        }
      })
    }
  } catch {
    // Ignore if no cookies loaded
  }
})

async function saveCookie(platform: string) {
  saving.value[platform] = true
  messages.value[platform] = ''
  try {
    await api.post('/cookies/', {
      platform,
      cookie_string: cookies.value[platform].cookie_string,
    })
    cookies.value[platform].status = 'valid'
    messages.value[platform] = '已保存'
  } catch {
    messages.value[platform] = '保存失败'
  } finally {
    saving.value[platform] = false
    setTimeout(() => { messages.value[platform] = '' }, 3000)
  }
}

async function deleteCookie(platform: string) {
  try {
    await api.delete(`/cookies/${platform}`)
    cookies.value[platform].cookie_string = ''
    cookies.value[platform].status = 'unknown'
    messages.value[platform] = '已删除'
  } catch {
    messages.value[platform] = '删除失败'
  } finally {
    setTimeout(() => { messages.value[platform] = '' }, 3000)
  }
}
</script>

<template>
  <div class="cookie-manager">
    <p class="description">为需要登录的平台配置 Cookie，以获取完整内容。</p>
    <div v-for="p in PLATFORMS" :key="p.key" class="cookie-card">
      <div class="card-header">
        <span class="platform-name">{{ p.label }}</span>
        <span class="status-badge" :class="cookies[p.key]?.status">
          {{ cookies[p.key]?.status === 'valid' ? '✅ 有效' : cookies[p.key]?.status === 'invalid' ? '❌ 无效' : '⚪ 未设置' }}
        </span>
      </div>
      <textarea
        v-model="cookies[p.key].cookie_string"
        :placeholder="`粘贴 ${p.label} 的 Cookie 字符串...`"
        class="cookie-input"
        rows="3"
      ></textarea>
      <div class="card-actions">
        <button class="save-btn" @click="saveCookie(p.key)" :disabled="saving[p.key]">
          {{ saving[p.key] ? '保存中...' : '保存' }}
        </button>
        <button class="delete-btn" @click="deleteCookie(p.key)" :disabled="!cookies[p.key]?.cookie_string">
          删除
        </button>
        <span v-if="messages[p.key]" class="msg">{{ messages[p.key] }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cookie-manager { display: flex; flex-direction: column; gap: 16px; }
.description { color: var(--text-secondary); font-size: 13px; margin: 0 0 4px; }
.cookie-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.platform-name { color: var(--text-primary); font-size: 14px; font-weight: 600; }
.status-badge { font-size: 12px; color: var(--text-secondary); }
.status-badge.valid { color: var(--success); }
.status-badge.invalid { color: var(--error); }
.cookie-input {
  width: 100%; box-sizing: border-box; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-primary); padding: 8px 12px; font-size: 12px;
  font-family: monospace; resize: vertical; outline: none; transition: border-color 0.2s;
}
.cookie-input:focus { border-color: var(--accent); }
.card-actions { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.save-btn {
  padding: 6px 16px; background: var(--accent); color: #fff; border: none;
  border-radius: 5px; cursor: pointer; font-size: 12px; transition: opacity 0.2s;
}
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.delete-btn {
  padding: 6px 16px; background: transparent; color: var(--error); border: 1px solid var(--error);
  border-radius: 5px; cursor: pointer; font-size: 12px; transition: opacity 0.2s;
}
.delete-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.msg { color: var(--success); font-size: 12px; }
</style>
