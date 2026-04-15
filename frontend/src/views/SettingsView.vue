<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import NotificationSettings from '../components/settings/NotificationSettings.vue'
import CookieManager from '../components/settings/CookieManager.vue'
import OpmlSection from '../components/settings/OpmlSection.vue'
import PluginManager from '../components/settings/PluginManager.vue'
import HealthDashboard from '../components/settings/HealthDashboard.vue'
import ApiKeySection from '../components/settings/ApiKeySection.vue'

const { t, locale } = useI18n()
const activeTab = ref('notifications')

function setLocale(lang: string) {
  locale.value = lang
  localStorage.setItem('locale', lang)
}
</script>

<template>
  <div class="settings-page">
    <div class="settings-header">
      <router-link to="/" class="back">← {{ t('settings.back') }}</router-link>
      <h1>{{ t('settings.title') }}</h1>
      <div class="lang-selector">
        <select :value="locale" @change="setLocale(($event.target as HTMLSelectElement).value)">
          <option value="zh-CN">中文</option>
          <option value="en">English</option>
        </select>
      </div>
    </div>
    <div class="tabs">
      <button :class="{ active: activeTab === 'notifications' }" @click="activeTab = 'notifications'">{{ t('settings.notifications') }}</button>
      <button :class="{ active: activeTab === 'cookies' }" @click="activeTab = 'cookies'">{{ t('settings.cookies') }}</button>
      <button :class="{ active: activeTab === 'opml' }" @click="activeTab = 'opml'">{{ t('settings.importExport') }}</button>
      <button :class="{ active: activeTab === 'plugins' }" @click="activeTab = 'plugins'">{{ t('settings.plugins') }}</button>
      <button :class="{ active: activeTab === 'api' }" @click="activeTab = 'api'">{{ t('settings.api') }}</button>
      <button :class="{ active: activeTab === 'monitor' }" @click="activeTab = 'monitor'">{{ t('settings.monitor') }}</button>
    </div>
    <NotificationSettings v-if="activeTab === 'notifications'" />
    <CookieManager v-if="activeTab === 'cookies'" />
    <OpmlSection v-if="activeTab === 'opml'" />
    <PluginManager v-if="activeTab === 'plugins'" />
    <ApiKeySection v-if="activeTab === 'api'" />
    <HealthDashboard v-if="activeTab === 'monitor'" />
  </div>
</template>

<style scoped>
.settings-page { max-width: 680px; margin: 0 auto; padding: 32px; min-height: 100vh; background: var(--bg-primary); }
.settings-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.back { color: var(--accent); text-decoration: none; font-size: 14px; }
h1 { color: var(--text-primary); font-size: 22px; margin: 0; flex: 1; }
.lang-selector select {
  background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text-primary); padding: 6px 10px; font-size: 13px; cursor: pointer; outline: none;
}
.tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
.tabs button { padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-secondary); cursor: pointer; font-size: 13px; transition: all 0.15s; }
.tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.tabs button:hover:not(.active) { border-color: var(--accent); color: var(--text-primary); }
</style>
