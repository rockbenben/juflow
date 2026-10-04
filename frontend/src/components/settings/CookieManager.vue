<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'
import { useI18n } from 'vue-i18n'

interface CookieEntry {
  platform: string
  cookie_string: string
  status: 'valid' | 'invalid' | 'unknown'
}

// Only scraper-based platforms actually use the user's cookie (scraper_base sets
// the Cookie header). RSSHub-based platforms (雪球/微博/小红书) ignore it, so
// listing them here would just be dead config.
const PLATFORMS = ['jisilu', 'taoguba', 'tonghuashun', 'jiuquaner', 'youzhiyouxing'] as const

const { t } = useI18n()
const cookies = ref<Record<string, CookieEntry>>({})
const saving = ref<Record<string, boolean>>({})
const messages = ref<Record<string, string>>({})

onMounted(async () => {
  PLATFORMS.forEach(p => {
    cookies.value[p] = { platform: p, cookie_string: '', status: 'unknown' }
    saving.value[p] = false
    messages.value[p] = ''
  })
  try {
    const { data } = await api.get('/cookies/')
    if (Array.isArray(data)) {
      data.forEach((entry: { platform: string; is_valid: boolean; last_validated_at: string | null }) => {
        if (cookies.value[entry.platform]) {
          cookies.value[entry.platform].cookie_string = t('cookie.savedLabel')
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
    messages.value[platform] = t('cookie.saved')
  } catch {
    messages.value[platform] = t('cookie.saveFailed')
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
    messages.value[platform] = t('cookie.deleted')
  } catch {
    messages.value[platform] = t('cookie.deleteFailed')
  } finally {
    setTimeout(() => { messages.value[platform] = '' }, 3000)
  }
}
</script>

<template>
  <div class="cookie-manager">
    <p class="description">{{ t('cookie.desc') }}</p>
    <div v-for="p in PLATFORMS" :key="p" class="cookie-card">
      <div class="card-header">
        <span class="platform-name">{{ t(`cookie.platforms.${p}`) }}</span>
        <span class="status-badge" :class="cookies[p]?.status">
          {{ cookies[p]?.status === 'valid' ? `✅ ${t('cookie.valid')}` : cookies[p]?.status === 'invalid' ? `❌ ${t('cookie.invalid')}` : `⚪ ${t('cookie.unset')}` }}
        </span>
      </div>
      <textarea
        v-model="cookies[p].cookie_string"
        :placeholder="t('cookie.paste', { label: t(`cookie.platforms.${p}`) })"
        :aria-label="t('cookie.paste', { label: t(`cookie.platforms.${p}`) })"
        class="cookie-input"
        rows="3"
      ></textarea>
      <div class="card-actions">
        <button class="save-btn" @click="saveCookie(p)" :disabled="saving[p]">
          {{ saving[p] ? t('cookie.saving') : t('cookie.save') }}
        </button>
        <button class="delete-btn" @click="deleteCookie(p)" :disabled="!cookies[p]?.cookie_string">
          {{ t('cookie.delete') }}
        </button>
        <span v-if="messages[p]" class="msg" role="status">{{ messages[p] }}</span>
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
  font-family: monospace; resize: vertical; transition: border-color 0.2s;
}
.cookie-input::placeholder { color: var(--text-muted); }
.cookie-input:focus { border-color: var(--accent); }
.card-actions { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.save-btn {
  padding: 6px 16px; background: var(--accent-strong); color: #fff; border: none;
  border-radius: 5px; cursor: pointer; font-size: 12px; font-family: inherit; transition: opacity 0.2s;
}
.save-btn:hover:not(:disabled) { background: var(--accent-strong-hover); }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.delete-btn {
  padding: 6px 16px; background: transparent; color: var(--error); border: 1px solid var(--error);
  border-radius: 5px; cursor: pointer; font-size: 12px; font-family: inherit; transition: opacity 0.2s;
}
.delete-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.msg { color: var(--success); font-size: 12px; }
</style>
