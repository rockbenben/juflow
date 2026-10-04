<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'
import { useI18n } from 'vue-i18n'

interface NotificationSettingsData {
  notify_defaults: string[]
  dnd_enabled: boolean
  dnd_start: string
  dnd_end: string
  email_digest: string
  wechat_webhook: string
  telegram_bot_token: string
  telegram_chat_id: string
  email_address: string
}

const { t } = useI18n()

const settings = ref<NotificationSettingsData>({
  notify_defaults: [],
  dnd_enabled: false,
  dnd_start: '22:00',
  dnd_end: '08:00',
  email_digest: 'instant',
  wechat_webhook: '',
  telegram_bot_token: '',
  telegram_chat_id: '',
  email_address: '',
})

const saving = ref(false)
const saveMessage = ref('')
const saveFailed = ref(false)

const channels = ['web_push', 'wechat', 'telegram', 'email'] as const

function toggleChannel(key: string) {
  const idx = settings.value.notify_defaults.indexOf(key)
  if (idx >= 0) {
    settings.value.notify_defaults.splice(idx, 1)
  } else {
    settings.value.notify_defaults.push(key)
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/notifications/settings')
    Object.assign(settings.value, data)
  } catch {
    // Use defaults if no settings yet
  }
})

async function save() {
  saving.value = true
  saveMessage.value = ''
  saveFailed.value = false
  try {
    await api.put('/notifications/settings', settings.value)
    saveMessage.value = t('notif.saved')
  } catch {
    saveMessage.value = t('notif.saveFailed')
    saveFailed.value = true
  } finally {
    saving.value = false
    setTimeout(() => { saveMessage.value = '' }, 3000)
  }
}
</script>

<template>
  <div class="notification-settings">
    <div class="card">
      <h3>{{ t('notif.channels') }}</h3>
      <div class="checkbox-group">
        <label v-for="ch in channels" :key="ch" class="checkbox-label">
          <input
            type="checkbox"
            :checked="settings.notify_defaults.includes(ch)"
            @change="toggleChannel(ch)"
          />
          <span>{{ t(`channels.${ch}`) }}</span>
        </label>
      </div>
    </div>

    <div class="card">
      <h3>{{ t('notif.dnd') }}</h3>
      <div class="field-row">
        <button type="button" class="toggle-label" @click="settings.dnd_enabled = !settings.dnd_enabled">
          <span>{{ t('notif.dndEnable') }}</span>
          <span class="toggle" :class="{ on: settings.dnd_enabled }" role="switch" :aria-checked="settings.dnd_enabled">
            <span class="toggle-knob"></span>
          </span>
        </button>
      </div>
      <div class="field-row" v-if="settings.dnd_enabled">
        <label>
          <span class="label-text">{{ t('notif.dndStart') }}</span>
          <input type="time" v-model="settings.dnd_start" class="time-input" />
        </label>
        <label>
          <span class="label-text">{{ t('notif.dndEnd') }}</span>
          <input type="time" v-model="settings.dnd_end" class="time-input" />
        </label>
      </div>
    </div>

    <div class="card">
      <h3>{{ t('notif.emailDigest') }}</h3>
      <div class="field">
        <label class="label-text" for="digest-mode">{{ t('notif.digestMode') }}</label>
        <select id="digest-mode" v-model="settings.email_digest" class="select-input">
          <option value="instant">{{ t('notif.digestInstant') }}</option>
          <option value="hourly">{{ t('notif.digestHourly') }}</option>
          <option value="daily">{{ t('notif.digestDaily') }}</option>
        </select>
      </div>
      <div class="field">
        <label class="label-text" for="digest-email">{{ t('notif.emailAddress') }}</label>
        <input id="digest-email" type="email" v-model="settings.email_address" placeholder="your@email.com" class="text-input" />
      </div>
    </div>

    <div class="card">
      <h3>{{ t('notif.wechat') }}</h3>
      <div class="field">
        <label class="label-text" for="wechat-webhook">{{ t('notif.wechatWebhook') }}</label>
        <input id="wechat-webhook" type="url" v-model="settings.wechat_webhook" placeholder="https://qyapi.weixin.qq.com/..." class="text-input" />
      </div>
    </div>

    <div class="card">
      <h3>{{ t('notif.telegram') }}</h3>
      <div class="field">
        <label class="label-text" for="tg-token">{{ t('notif.botToken') }}</label>
        <input id="tg-token" type="text" v-model="settings.telegram_bot_token" placeholder="123456:ABCdef..." class="text-input" />
      </div>
      <div class="field">
        <label class="label-text" for="tg-chat">{{ t('notif.chatId') }}</label>
        <input id="tg-chat" type="text" v-model="settings.telegram_chat_id" placeholder="-100..." class="text-input" />
      </div>
    </div>

    <div class="save-row">
      <button class="save-btn" @click="save" :disabled="saving">
        {{ saving ? t('notif.saving') : t('notif.save') }}
      </button>
      <span v-if="saveMessage" class="save-msg" :class="{ fail: saveFailed }" role="status">{{ saveMessage }}</span>
    </div>
  </div>
</template>

<style scoped>
.notification-settings { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
h3 { color: var(--text-primary); font-size: 14px; margin: 0 0 16px; }
.checkbox-group { display: flex; flex-direction: column; gap: 10px; }
.checkbox-label { display: flex; align-items: center; gap: 10px; color: var(--text-secondary); font-size: 13px; cursor: pointer; }
.checkbox-label input[type="checkbox"] { accent-color: var(--accent); width: 16px; height: 16px; cursor: pointer; }
.field-row { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.toggle-label { display: flex; align-items: center; justify-content: space-between; width: 100%; background: none; border: none; padding: 0; color: var(--text-secondary); font-size: 13px; font-family: inherit; cursor: pointer; }
.toggle { width: 40px; height: 22px; background: var(--border); border-radius: 11px; position: relative; transition: background 0.2s; display: inline-block; }
.toggle.on { background: var(--accent-strong); }
.toggle-knob { width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
.toggle.on .toggle-knob { left: 20px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.field:last-child { margin-bottom: 0; }
.label-text { color: var(--text-secondary); font-size: 12px; }
.text-input, .select-input, .time-input {
  background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text-primary); padding: 8px 12px; font-size: 13px;
  transition: border-color 0.2s;
}
.text-input { width: 100%; box-sizing: border-box; }
.text-input::placeholder { color: var(--text-muted); }
.text-input:focus, .select-input:focus, .time-input:focus { border-color: var(--accent); }
.select-input { cursor: pointer; }
.save-row { display: flex; align-items: center; gap: 12px; }
.save-btn {
  padding: 10px 24px; background: var(--accent-strong); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; transition: opacity 0.2s;
}
.save-btn:hover:not(:disabled) { background: var(--accent-strong-hover); }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.save-msg { color: var(--success); font-size: 13px; }
.save-msg.fail { color: var(--error); }
</style>
