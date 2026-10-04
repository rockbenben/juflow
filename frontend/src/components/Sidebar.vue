<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useArticlesStore } from '../stores/articles'
import { useAuthStore } from '../stores/auth'
import { useGroupsStore } from '../stores/groups'
import { useTagsStore } from '../stores/tags'
import { useTheme } from '../composables/useTheme'
import { platformColor, onColor } from '../composables/usePlatform'
import { useI18n } from 'vue-i18n'

const subs = useSubscriptionsStore()
const articles = useArticlesStore()
const auth = useAuthStore()
const groups = useGroupsStore()
const tags = useTagsStore()
const { theme, setTheme } = useTheme()
const { t } = useI18n()

const unreadCount = computed(() => articles.articles.filter(a => !a.is_read).length)
const groupsOpen = ref(true)
const tagsOpen = ref(true)
const activeNav = computed(() => articles.filter)

const emit = defineEmits<{
  (e: 'add-subscription'): void
  (e: 'edit-subscription', id: string): void
}>()

onMounted(async () => {
  await Promise.all([groups.load(), tags.load()])
})

async function loadAll() {
  await articles.load()
}

async function loadFavorites() {
  await articles.loadFavorites()
}

async function loadReadLater() {
  await articles.loadReadLater()
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo-section">
      <h1 class="logo">聚流</h1>
      <span class="version">JuFlow</span>
    </div>
    <nav class="nav" :aria-label="t('settings.title')">
      <button class="nav-item" :class="{ active: activeNav === 'all' }" :aria-pressed="activeNav === 'all'" @click="loadAll">
        <span class="nav-label">📥 {{ t('sidebar.unread') }}</span>
        <span v-if="unreadCount" class="badge">{{ unreadCount }}</span>
      </button>
      <button class="nav-item" :class="{ active: activeNav === 'favorites' }" :aria-pressed="activeNav === 'favorites'" @click="loadFavorites">
        <span class="nav-label">⭐ {{ t('sidebar.favorites') }}</span>
      </button>
      <button class="nav-item" :class="{ active: activeNav === 'read_later' }" :aria-pressed="activeNav === 'read_later'" @click="loadReadLater">
        <span class="nav-label">🕐 {{ t('sidebar.readLater') }}</span>
      </button>
    </nav>

    <button class="section-label section-collapsible" :aria-expanded="groupsOpen" @click="groupsOpen = !groupsOpen">
      {{ t('sidebar.groups') }} <span class="chevron">{{ groupsOpen ? '▾' : '▸' }}</span>
    </button>
    <div v-if="groupsOpen" class="groups-list">
      <div v-if="groups.groups.length === 0" class="empty-hint">{{ t('sidebar.emptyGroups') }}</div>
      <div v-for="group in groups.groups" :key="group.id" class="group-item">
        <span class="group-icon">{{ group.icon || '📁' }}</span>
        <span class="group-name">{{ group.name }}</span>
        <span v-if="group.subscription_count" class="group-count">{{ group.subscription_count }}</span>
      </div>
    </div>

    <button class="section-label section-collapsible" :aria-expanded="tagsOpen" @click="tagsOpen = !tagsOpen">
      {{ t('sidebar.tags') }} <span class="chevron">{{ tagsOpen ? '▾' : '▸' }}</span>
    </button>
    <div v-if="tagsOpen" class="tags-list">
      <div v-if="tags.tags.length === 0" class="empty-hint">{{ t('sidebar.emptyTags') }}</div>
      <span
        v-for="tag in tags.tags"
        :key="tag.id"
        class="tag-pill"
      >
        <span class="tag-dot" :style="{ background: tag.color || 'var(--accent)' }"></span>
        {{ tag.name }}
      </span>
    </div>

    <div class="section-label">{{ t('sidebar.sources') }}</div>
    <div class="sources">
      <button
        v-for="sub in subs.subscriptions"
        :key="sub.id"
        class="source-item"
        @click="emit('edit-subscription', sub.id)"
      >
        <span class="avatar" :style="{ background: platformColor(sub.source.platform), color: onColor(platformColor(sub.source.platform)) }">
          {{ sub.source.display_name.charAt(0) }}
        </span>
        <span class="source-info">
          <span class="source-name">{{ sub.custom_name || sub.source.display_name }}</span>
          <span class="source-platform">{{ sub.source.platform }}</span>
        </span>
      </button>
    </div>
    <div class="sidebar-bottom">
      <button class="add-btn" @click="emit('add-subscription')">+ {{ t('sidebar.addSubscription') }}</button>
      <router-link to="/settings" class="settings-link" :aria-label="t('settings.title')">⚙️</router-link>
      <button class="logout-btn" @click="auth.logout()">{{ t('sidebar.logout') }}</button>
    </div>
    <div class="theme-toggle" role="group" :aria-label="t('settings.theme')">
      <button @click="setTheme('dark')" :aria-pressed="theme === 'dark'" :title="t('sidebar.themeDark')" :aria-label="t('sidebar.themeDark')">🌙</button>
      <button @click="setTheme('light')" :aria-pressed="theme === 'light'" :title="t('sidebar.themeLight')" :aria-label="t('sidebar.themeLight')">☀️</button>
      <button @click="setTheme('system')" :aria-pressed="theme === 'system'" :title="t('sidebar.themeSystem')" :aria-label="t('sidebar.themeSystem')">💻</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar { width: 220px; background: var(--bg-secondary); border-right: 1px solid var(--border); display: flex; flex-direction: column; height: 100vh; flex-shrink: 0; overflow-y: auto; }
.logo-section { padding: 16px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
.logo { color: var(--accent-text); font-size: 18px; margin: 0; }
.version { color: var(--text-muted); font-size: 11px; }
.nav { padding: 12px 0; flex-shrink: 0; }
.nav-item { display: flex; width: 100%; align-items: center; justify-content: space-between; padding: 8px 16px; background: none; border: none; border-right: 3px solid transparent; color: var(--text-secondary); font-size: 13px; cursor: pointer; text-align: left; transition: background 0.15s; font-family: inherit; }
.nav-label { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.active { color: var(--text-primary); background: color-mix(in srgb, var(--accent) 20%, transparent); border-right-color: var(--accent); }
.badge { background: var(--accent-strong); color: #fff; border-radius: 10px; padding: 1px 8px; font-size: 11px; flex-shrink: 0; }
.section-label { display: flex; width: 100%; padding: 8px 16px; background: none; border: none; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; text-align: left; font-family: inherit; flex-shrink: 0; }
.section-collapsible { cursor: pointer; justify-content: space-between; align-items: center; user-select: none; }
.section-collapsible:hover { color: var(--text-secondary); }
.chevron { font-size: 10px; }
.groups-list { padding: 0 8px 8px; flex-shrink: 0; }
.group-item { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 5px; }
.group-item:hover { background: var(--bg-tertiary); }
.group-icon { font-size: 14px; }
.group-name { color: var(--text-secondary); font-size: 12px; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.group-count { color: var(--text-muted); font-size: 11px; }
.tags-list { padding: 0 12px 12px; display: flex; flex-wrap: wrap; gap: 6px; flex-shrink: 0; }
.tag-pill { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; border-radius: 10px; font-size: 11px; border: 1px solid var(--border); color: var(--text-primary); }
.tag-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.empty-hint { color: var(--text-muted); font-size: 11px; padding: 4px 8px; }
.sources { flex: 1; overflow-y: auto; }
.source-item { display: flex; width: 100%; align-items: center; gap: 8px; padding: 6px 16px; background: none; border: none; text-align: left; color: var(--text-secondary); font-size: 12px; cursor: pointer; font-family: inherit; }
.source-item:hover { background: var(--bg-tertiary); }
.avatar { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; }
.source-info { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.source-name { color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.source-platform { color: var(--text-muted); font-size: 10px; }
.sidebar-bottom { padding: 12px 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.add-btn { flex: 1; padding: 6px; background: var(--accent-strong); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-family: inherit; }
.add-btn:hover { background: var(--accent-strong-hover); }
.settings-link { padding: 6px 8px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 4px; font-size: 14px; text-decoration: none; display: flex; align-items: center; }
.settings-link:hover { color: var(--accent-text); border-color: var(--accent); }
.logout-btn { padding: 6px 10px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 4px; cursor: pointer; font-size: 12px; font-family: inherit; }
.logout-btn:hover { color: var(--text-primary); }
.theme-toggle { display: flex; justify-content: center; gap: 4px; padding: 8px 16px; border-top: 1px solid var(--border); flex-shrink: 0; }
.theme-toggle button { background: transparent; border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 13px; color: var(--text-secondary); transition: all 0.15s; }
.theme-toggle button[aria-pressed="true"] { background: color-mix(in srgb, var(--accent) 20%, transparent); border-color: var(--accent); }
.theme-toggle button:hover { border-color: var(--accent); }
</style>
