<script setup lang="ts">
import { ref } from 'vue'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useArticlesStore } from '../stores/articles'
import { INTERVAL_OPTIONS } from '../composables/usePlatform'
import { useI18n } from 'vue-i18n'

const emit = defineEmits<{ (e: 'close'): void }>()
const subs = useSubscriptionsStore()
const articles = useArticlesStore()
const { t } = useI18n()

const url = ref('')
const fetchInterval = ref(300)
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleAdd() {
  if (!url.value.trim()) return
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const sub = await subs.add(url.value.trim(), fetchInterval.value)
    success.value = t('subscription.subscribed', { name: sub.source.display_name, platform: sub.source.platform })
    url.value = ''
    await articles.load()
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('subscription.addFailed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" role="dialog" aria-modal="true" :aria-label="t('subscription.add')" @click.self="emit('close')" @keydown.esc.window="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ t('subscription.add') }}</h2>
        <button class="close-btn" :aria-label="t('keyboard.close')" @click="emit('close')">✕</button>
      </div>
      <p class="hint">{{ t('subscription.pasteUrl') }}</p>
      <form @submit.prevent="handleAdd">
        <input v-model="url" type="url" placeholder="https://xueqiu.com/u/1234567890" :aria-label="t('subscription.pasteUrl')" required autofocus />
        <div class="interval-row">
          <label for="add-interval">{{ t('subscription.interval') }}</label>
          <select id="add-interval" v-model="fetchInterval">
            <option v-for="opt in INTERVAL_OPTIONS" :key="opt.value" :value="opt.value">
              {{ t(`subscription.intervals.${opt.key}`) }}
            </option>
          </select>
        </div>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <p v-if="success" class="success" role="status">{{ success }}</p>
        <button type="submit" :disabled="loading">{{ loading ? t('subscription.adding') : t('subscription.add') }}</button>
      </form>
      <div class="supported"><span class="label">{{ t('subscription.supportedIntro') }}</span>{{ t('platforms.list') }}</div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 24px; width: 420px; max-width: calc(100vw - 32px); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.modal-header h2 { color: var(--text-primary); font-size: 18px; margin: 0; }
.close-btn { background: none; border: none; color: var(--text-secondary); font-size: 18px; cursor: pointer; padding: 4px; }
.close-btn:hover { color: var(--text-primary); }
.hint { color: var(--text-secondary); font-size: 13px; margin: 0 0 16px; }
input { width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 14px; box-sizing: border-box; margin-bottom: 12px; }
input::placeholder { color: var(--text-muted); }
.interval-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.interval-row label { color: var(--text-secondary); font-size: 13px; }
.interval-row select { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); padding: 4px 8px; font-size: 13px; }
button[type="submit"] { width: 100%; padding: 10px; background: var(--accent-strong); color: white; border: none; border-radius: 6px; font-size: 14px; font-family: inherit; cursor: pointer; }
button[type="submit"]:hover:not(:disabled) { background: var(--accent-strong-hover); }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: var(--error); font-size: 13px; }
.success { color: var(--success); font-size: 13px; }
.supported { margin-top: 16px; color: var(--text-muted); font-size: 12px; line-height: 1.6; }
.label { color: var(--text-secondary); }
</style>
