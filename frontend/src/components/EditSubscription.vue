<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/client'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useGroupsStore } from '../stores/groups'
import { useTagsStore } from '../stores/tags'
import { INTERVAL_OPTIONS } from '../composables/usePlatform'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ subscriptionId: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const subs = useSubscriptionsStore()
const groups = useGroupsStore()
const tags = useTagsStore()
const { t } = useI18n()

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

const CHANNELS = ['web_push', 'wechat', 'telegram', 'email'] as const

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
    error.value = err.response?.data?.detail || t('subscription.saveFailed')
  } finally {
    saving.value = false
  }
}

async function unsubscribe() {
  if (!confirm(t('subscription.confirmUnsubscribe'))) return
  await subs.remove(props.subscriptionId)
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" role="dialog" aria-modal="true" :aria-label="t('subscription.edit')" @click.self="emit('close')" @keydown.esc.window="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ t('subscription.edit') }}</h2>
        <button class="close-btn" :aria-label="t('keyboard.close')" @click="emit('close')">✕</button>
      </div>

      <div v-if="subscription" class="modal-body">
        <div class="source-info">
          <strong>{{ subscription.source.display_name }}</strong>
          <span class="platform">{{ subscription.source.platform }}</span>
        </div>

        <div class="field">
          <label class="label" for="edit-custom-name">{{ t('subscription.customName') }}</label>
          <input
            id="edit-custom-name"
            v-model="form.custom_name"
            type="text"
            :placeholder="subscription.source.display_name"
            class="input"
          />
        </div>

        <div class="field">
          <label class="label" for="edit-interval">{{ t('subscription.interval') }}</label>
          <select id="edit-interval" v-model="form.fetch_interval" class="select">
            <option v-for="opt in INTERVAL_OPTIONS" :key="opt.value" :value="opt.value">
              {{ t(`subscription.intervals.${opt.key}`) }}
            </option>
          </select>
        </div>

        <div class="field" v-if="groups.groups.length > 0">
          <span class="label">{{ t('subscription.groupsField') }}</span>
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
          <span class="label">{{ t('subscription.tagsField') }}</span>
          <div class="tag-select">
            <button
              v-for="tg in tags.tags"
              :key="tg.id"
              type="button"
              class="tag-chip"
              :class="{ selected: form.tag_ids.includes(tg.id) }"
              :aria-pressed="form.tag_ids.includes(tg.id)"
              @click="toggleTagId(tg.id)"
            >
              {{ tg.name }}
            </button>
          </div>
        </div>

        <div class="field">
          <span class="label">{{ t('subscription.channelsField') }}</span>
          <div class="checkbox-group">
            <label v-for="ch in CHANNELS" :key="ch" class="checkbox-label">
              <input
                type="checkbox"
                :checked="form.notify_channels.includes(ch)"
                @change="toggleChannel(ch)"
              />
              <span>{{ t(`channels.${ch}`) }}</span>
            </label>
          </div>
        </div>

        <div class="field">
          <button
            type="button"
            class="toggle-label"
            @click="form.dnd_exempt = !form.dnd_exempt"
          >
            <span>{{ t('subscription.dndExempt') }}</span>
            <span class="toggle" :class="{ on: form.dnd_exempt }" role="switch" :aria-checked="form.dnd_exempt">
              <span class="toggle-knob"></span>
            </span>
          </button>
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>
      </div>

      <div class="modal-footer">
        <button class="unsubscribe-btn" @click="unsubscribe">{{ t('subscription.unsubscribe') }}</button>
        <div class="footer-right">
          <button class="cancel-btn" @click="emit('close')">{{ t('subscription.cancel') }}</button>
          <button class="save-btn" @click="save" :disabled="saving">
            {{ saving ? t('subscription.saving') : t('subscription.save') }}
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
  color: var(--text-primary); padding: 8px 12px; font-size: 13px;
  transition: border-color 0.2s;
}
.input::placeholder { color: var(--text-muted); }
.input:focus, .select:focus { border-color: var(--accent); }
.select { cursor: pointer; }
.checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
.checkbox-label { display: flex; align-items: center; gap: 6px; color: var(--text-secondary); font-size: 13px; cursor: pointer; }
.checkbox-label input[type="checkbox"] { accent-color: var(--accent); }
.tag-select { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-chip { padding: 3px 12px; border-radius: 12px; border: 1px solid var(--border); background: none; color: var(--text-secondary); font-size: 12px; font-family: inherit; cursor: pointer; transition: all 0.15s; }
.tag-chip.selected { background: var(--accent-strong); border-color: var(--accent-strong); color: #fff; }
.toggle-label { display: flex; align-items: center; justify-content: space-between; width: 100%; background: none; border: none; padding: 0; color: var(--text-secondary); font-size: 13px; font-family: inherit; cursor: pointer; }
.toggle { width: 40px; height: 22px; background: var(--border); border-radius: 11px; position: relative; transition: background 0.2s; flex-shrink: 0; display: inline-block; }
.toggle.on { background: var(--accent-strong); }
.toggle-knob { width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
.toggle.on .toggle-knob { left: 20px; }
.error { color: var(--error); font-size: 13px; margin: 0; }
.modal-footer { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-top: 1px solid var(--border); }
.footer-right { display: flex; gap: 10px; }
.unsubscribe-btn { padding: 8px 16px; background: transparent; color: var(--error); border: 1px solid var(--error); border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; }
.cancel-btn { padding: 8px 16px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; }
.cancel-btn:hover { color: var(--text-primary); }
.save-btn { padding: 8px 20px; background: var(--accent-strong); color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; }
.save-btn:hover:not(:disabled) { background: var(--accent-strong-hover); }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
