<script setup lang="ts">
import { ref } from 'vue'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useArticlesStore } from '../stores/articles'
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
    success.value = `已订阅 ${sub.source.display_name}（${sub.source.platform}）`
    url.value = ''
    await articles.load()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '添加失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ t('subscription.add') }}</h2>
        <button class="close-btn" @click="emit('close')">✕</button>
      </div>
      <p class="hint">{{ t('subscription.pasteUrl') }}</p>
      <form @submit.prevent="handleAdd">
        <input v-model="url" type="url" placeholder="https://xueqiu.com/u/1234567890" required autofocus />
        <div class="interval-row">
          <label>{{ t('subscription.interval') }}</label>
          <select v-model="fetchInterval">
            <option :value="60">每分钟</option>
            <option :value="120">每 2 分钟</option>
            <option :value="300">每 5 分钟</option>
            <option :value="600">每 10 分钟</option>
            <option :value="1800">每 30 分钟</option>
          </select>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
        <button type="submit" :disabled="loading">{{ loading ? t('subscription.adding') : t('subscription.add') }}</button>
      </form>
      <div class="supported"><span class="label">支持平台：</span>雪球 · 集思录 · 淘股吧 · 东方财富 · 同花顺 · 韭圈儿 · 有知有行 · 公众号 · 知乎 · 微博 · 小红书 · 掘金 · CSDN · V2EX</div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg-tertiary); border-radius: 12px; padding: 24px; width: 420px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.modal-header h2 { color: var(--text-primary); font-size: 18px; margin: 0; }
.close-btn { background: none; border: none; color: var(--text-secondary); font-size: 18px; cursor: pointer; }
.hint { color: var(--text-secondary); font-size: 13px; margin: 0 0 16px; }
input { width: 100%; padding: 10px 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 14px; box-sizing: border-box; margin-bottom: 12px; }
.interval-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.interval-row label { color: var(--text-secondary); font-size: 13px; }
.interval-row select { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); padding: 4px 8px; }
button[type="submit"] { width: 100%; padding: 10px; background: var(--accent); color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: var(--error); font-size: 13px; }
.success { color: var(--success); font-size: 13px; }
.supported { margin-top: 16px; color: var(--text-muted); font-size: 12px; }
.label { color: var(--text-secondary); }
</style>
