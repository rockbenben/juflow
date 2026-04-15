<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/client'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useGroupsStore } from '../stores/groups'
import { useTagsStore } from '../stores/tags'

const props = defineProps<{ subscriptionId: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const subs = useSubscriptionsStore()
const groups = useGroupsStore()
const tags = useTagsStore()

const subscription = computed(() => subs.subscriptions.find(s => s.id === props.subscriptionId))

const form = ref({
  custom_name: '',
  fetch_interval: 300,
  group_ids: [] as string[],
  tag_ids: [] as string[],
  notify_channels: [] as string[],
  dnd_exempt: false,
})

const saving = ref(false)
const error = ref('')

const INTERVALS = [
  { value: 60, label: '每分钟' },
  { value: 300, label: '每5分钟' },
  { value: 900, label: '每15分钟' },
  { value: 1800, label: '每30分钟' },
  { value: 3600, label: '每小时' },
  { value: 21600, label: '每6小时' },
  { value: 86400, label: '每天' },
]

const CHANNELS = [
  { key: 'web_push', label: 'Web Push' },
  { key: 'wechat', label: '微信' },
  { key: 'telegram', label: 'Telegram' },
  { key: 'email', label: '邮件' },
]

onMounted(async () => {
  await Promise.all([groups.load(), tags.load()])
  if (subscription.value) {
    form.value.custom_name = subscription.value.custom_name || ''
    form.value.fetch_interval = subscription.value.fetch_interval
    form.value.notify_channels = [...(subscription.value.notify_channels || [])]
    // Load extended fields if available
    try {
      const { data } = await api.get(`/subscriptions/${props.subscriptionId}`)
      form.value.group_ids = data.group_ids || []
      form.value.tag_ids = data.tag_ids || []
      form.value.dnd_exempt = data.dnd_exempt || false
    } catch {
      // Use defaults
    }
  }
})

function toggleGroupId(id: string) {
  const i = form.value.group_ids.indexOf(id)
  if (i >= 0) form.value.group_ids.splice(i, 1)
  else form.value.group_ids.push(id)
}

function toggleTagId(id: string) {
  const i = form.value.tag_ids.indexOf(id)
  if (i >= 0) form.value.tag_ids.splice(i, 1)
  else form.value.tag_ids.push(id)
}

function toggleChannel(key: string) {
  const i = form.value.notify_channels.indexOf(key)
  if (i >= 0) form.value.notify_channels.splice(i, 1)
  else form.value.notify_channels.push(key)
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    await api.put(`/subscriptions/${props.subscriptionId}`, form.value)
    // Update local store
    const sub = subs.subscriptions.find(s => s.id === props.subscriptionId)
    if (sub) {
      sub.custom_name = form.value.custom_name || null
      sub.fetch_interval = form.value.fetch_interval
      sub.notify_channels = form.value.notify_channels
    }
    emit('close')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail || '保存失败，请重试'
  } finally {
    saving.value = false
  }
}

async function unsubscribe() {
  if (!confirm('确定取消订阅？')) return
  await subs.remove(props.subscriptionId)
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑订阅</h2>
        <button class="close-btn" @click="emit('close')">✕</button>
      </div>

      <div v-if="subscription" class="modal-body">
        <div class="source-info">
          <strong>{{ subscription.source.display_name }}</strong>
          <span class="platform">{{ subscription.source.platform }}</span>
        </div>

        <div class="field">
          <label class="label">自定义名称</label>
          <input
            v-model="form.custom_name"
            type="text"
            :placeholder="subscription.source.display_name"
            class="input"
          />
        </div>

        <div class="field">
          <label class="label">抓取间隔</label>
          <select v-model="form.fetch_interval" class="select">
            <option v-for="opt in INTERVALS" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <div class="field" v-if="groups.groups.length > 0">
          <label class="label">所属分组</label>
          <div class="checkbox-group">
            <label v-for="g in groups.groups" :key="g.id" class="checkbox-label">
              <input
                type="checkbox"
                :checked="form.group_ids.includes(g.id)"
                @change="toggleGroupId(g.id)"
              />
              <span>{{ g.icon || '📁' }} {{ g.name }}</span>
            </label>
          </div>
        </div>

        <div class="field" v-if="tags.tags.length > 0">
          <label class="label">标签</label>
          <div class="tag-select">
            <span
              v-for="t in tags.tags"
              :key="t.id"
              class="tag-chip"
              :class="{ selected: form.tag_ids.includes(t.id) }"
              :style="t.color ? { borderColor: t.color, color: form.tag_ids.includes(t.id) ? '#fff' : t.color, background: form.tag_ids.includes(t.id) ? t.color : 'transparent' } : {}"
              @click="toggleTagId(t.id)"
            >
              {{ t.name }}
            </span>
          </div>
        </div>

        <div class="field">
          <label class="label">通知渠道</label>
          <div class="checkbox-group">
            <label v-for="ch in CHANNELS" :key="ch.key" class="checkbox-label">
              <input
                type="checkbox"
                :checked="form.notify_channels.includes(ch.key)"
                @change="toggleChannel(ch.key)"
              />
              <span>{{ ch.label }}</span>
            </label>
          </div>
        </div>

        <div class="field">
          <label class="toggle-label">
            <span>勿扰豁免（此订阅源始终推送）</span>
            <div class="toggle" :class="{ on: form.dnd_exempt }" @click="form.dnd_exempt = !form.dnd_exempt">
              <div class="toggle-knob"></div>
            </div>
          </label>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
      </div>

      <div class="modal-footer">
        <button class="unsubscribe-btn" @click="unsubscribe">取消订阅</button>
        <div class="footer-right">
          <button class="cancel-btn" @click="emit('close')">取消</button>
          <button class="save-btn" @click="save" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: #00000088; z-index: 100; display: flex; align-items: center; justify-content: center; }
.modal { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; width: 480px; max-width: 95vw; max-height: 90vh; display: flex; flex-direction: column; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid var(--border); }
h2 { color: var(--text-primary); font-size: 16px; margin: 0; }
.close-btn { background: none; border: none; color: var(--text-secondary); font-size: 16px; cursor: pointer; padding: 4px; }
.close-btn:hover { color: var(--text-primary); }
.modal-body { padding: 20px 24px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 16px; }
.source-info { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: var(--bg-tertiary); border-radius: 6px; }
.source-info strong { color: var(--text-primary); font-size: 14px; }
.platform { color: var(--text-secondary); font-size: 12px; }
.field { display: flex; flex-direction: column; gap: 8px; }
.label { color: var(--text-secondary); font-size: 12px; }
.input, .select {
  background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text-primary); padding: 8px 12px; font-size: 13px; outline: none;
  transition: border-color 0.2s;
}
.input:focus, .select:focus { border-color: var(--accent); }
.select { cursor: pointer; }
.checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
.checkbox-label { display: flex; align-items: center; gap: 6px; color: #aaa; font-size: 13px; cursor: pointer; }
.checkbox-label input[type="checkbox"] { accent-color: var(--accent); }
.tag-select { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-chip { padding: 3px 12px; border-radius: 12px; border: 1px solid var(--border); color: var(--text-secondary); font-size: 12px; cursor: pointer; transition: all 0.15s; }
.tag-chip.selected { background: var(--accent); border-color: var(--accent); color: #fff; }
.toggle-label { display: flex; align-items: center; justify-content: space-between; color: #aaa; font-size: 13px; cursor: pointer; }
.toggle { width: 40px; height: 22px; background: var(--border); border-radius: 11px; position: relative; cursor: pointer; transition: background 0.2s; flex-shrink: 0; }
.toggle.on { background: var(--accent); }
.toggle-knob { width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
.toggle.on .toggle-knob { left: 20px; }
.error { color: var(--error); font-size: 13px; margin: 0; }
.modal-footer { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-top: 1px solid var(--border); }
.footer-right { display: flex; gap: 10px; }
.unsubscribe-btn { padding: 8px 16px; background: transparent; color: var(--error); border: 1px solid var(--error); border-radius: 6px; cursor: pointer; font-size: 13px; }
.cancel-btn { padding: 8px 16px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; font-size: 13px; }
.save-btn { padding: 8px 20px; background: var(--accent); color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
