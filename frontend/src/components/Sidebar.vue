<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSubscriptionsStore } from '../stores/subscriptions'
import { useArticlesStore } from '../stores/articles'
import { useAuthStore } from '../stores/auth'
import { useGroupsStore } from '../stores/groups'
import { useTagsStore } from '../stores/tags'
import { useTheme } from '../composables/useTheme'
import { useI18n } from 'vue-i18n'

const subs = useSubscriptionsStore()
const articles = useArticlesStore()
const auth = useAuthStore()
const groups = useGroupsStore()
const tags = useTagsStore()
const router = useRouter()
const { theme, setTheme } = useTheme()
const { t } = useI18n()

const unreadCount = computed(() => articles.articles.filter(a => !a.is_read).length)
const groupsOpen = ref(true)
const tagsOpen = ref(true)
const activeNav = ref('all')

const colors: Record<string, string> = { csdn: '#e17055', xueqiu: '#00b894', zhihu: '#6c63ff' }
function platformColor(platform: string) { return colors[platform] || '#fdcb6e' }

const emit = defineEmits<{
  (e: 'add-subscription'): void
  (e: 'edit-subscription', id: string): void
}>()

onMounted(async () => {
  await Promise.all([groups.load(), tags.load()])
})

async function loadAll() {
  activeNav.value = 'all'
  await articles.load()
}

async function loadFavorites() {
  activeNav.value = 'favorites'
  await articles.loadFavorites()
}

async function loadReadLater() {
  activeNav.value = 'read_later'
  await articles.loadReadLater()
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo-section">
      <h1 class="logo">聚流</h1>
      <span class="version">JuFlow</span>
    </div>
    <nav class="nav">
      <div class="nav-item" :class="{ active: activeNav === 'all' }" @click="loadAll">
        📥 {{ t('sidebar.unread') }}
        <span v-if="unreadCount" class="badge">{{ unreadCount }}</span>
      </div>
      <div class="nav-item" :class="{ active: activeNav === 'favorites' }" @click="loadFavorites">
        ⭐ {{ t('sidebar.favorites') }}
      </div>
      <div class="nav-item" :class="{ active: activeNav === 'read_later' }" @click="loadReadLater">
        🕐 {{ t('sidebar.readLater') }}
      </div>
    </nav>

    <div class="section-label section-collapsible" @click="groupsOpen = !groupsOpen">
      {{ t('sidebar.groups') }} <span class="chevron">{{ groupsOpen ? '▾' : '▸' }}</span>
    </div>
    <div v-if="groupsOpen" class="groups-list">
      <div v-if="groups.groups.length === 0" class="empty-hint">暂无分组</div>
      <div v-for="group in groups.groups" :key="group.id" class="group-item">
        <span class="group-icon">{{ group.icon || '📁' }}</span>
        <span class="group-name">{{ group.name }}</span>
        <span v-if="group.subscription_count" class="group-count">{{ group.subscription_count }}</span>
      </div>
    </div>

    <div class="section-label section-collapsible" @click="tagsOpen = !tagsOpen">
      {{ t('sidebar.tags') }} <span class="chevron">{{ tagsOpen ? '▾' : '▸' }}</span>
    </div>
    <div v-if="tagsOpen" class="tags-list">
      <div v-if="tags.tags.length === 0" class="empty-hint">暂无标签</div>
      <span
        v-for="tag in tags.tags"
        :key="tag.id"
        class="tag-pill"
        :style="{ background: tag.color ? tag.color + '33' : 'color-mix(in srgb, var(--accent) 20%, transparent)', borderColor: tag.color || 'var(--accent)', color: tag.color || 'var(--accent)' }"
      >
        {{ tag.name }}
      </span>
    </div>

    <div class="section-label">{{ t('sidebar.sources') }}</div>
    <div class="sources">
      <div
        v-for="sub in subs.subscriptions"
        :key="sub.id"
        class="source-item"
        @click="emit('edit-subscription', sub.id)"
      >
        <div class="avatar" :style="{ background: platformColor(sub.source.platform) }">
          {{ sub.source.display_name.charAt(0) }}
        </div>
        <div class="source-info">
          <span class="source-name">{{ sub.custom_name || sub.source.display_name }}</span>
          <span class="source-platform">{{ sub.source.platform }}</span>
        </div>
      </div>
    </div>
    <div class="sidebar-bottom">
      <button class="add-btn" @click="emit('add-subscription')">+ {{ t('sidebar.addSubscription') }}</button>
      <router-link to="/settings" class="settings-link">⚙️</router-link>
      <button class="logout-btn" @click="auth.logout(); router.push('/login')">{{ t('sidebar.logout') }}</button>
    </div>
    <div class="theme-toggle">
      <button @click="setTheme('dark')" :class="{ active: theme === 'dark' }" title="Dark">🌙</button>
      <button @click="setTheme('light')" :class="{ active: theme === 'light' }" title="Light">☀️</button>
      <button @click="setTheme('system')" :class="{ active: theme === 'system' }" title="System">💻</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar { width: 220px; background: var(--bg-secondary); border-right: 1px solid var(--border); display: flex; flex-direction: column; height: 100vh; flex-shrink: 0; overflow-y: auto; }
.logo-section { padding: 16px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
.logo { color: var(--accent); font-size: 18px; margin: 0; }
.version { color: var(--text-muted); font-size: 11px; }
.nav { padding: 12px 0; flex-shrink: 0; }
.nav-item { padding: 8px 16px; color: #aaa; font-size: 13px; display: flex; justify-content: space-between; cursor: pointer; border-right: 3px solid transparent; transition: background 0.15s; }
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.active { color: var(--text-primary); background: color-mix(in srgb, var(--accent) 20%, transparent); border-right-color: var(--accent); }
.badge { background: var(--accent); color: var(--text-primary); border-radius: 10px; padding: 1px 8px; font-size: 11px; }
.section-label { padding: 8px 16px; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; flex-shrink: 0; }
.section-collapsible { cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }
.section-collapsible:hover { color: #aaa; }
.chevron { font-size: 10px; }
.groups-list { padding: 0 8px 8px; flex-shrink: 0; }
.group-item { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 5px; cursor: pointer; }
.group-item:hover { background: var(--bg-tertiary); }
.group-icon { font-size: 14px; }
.group-name { color: #ccc; font-size: 12px; flex: 1; }
.group-count { color: var(--text-muted); font-size: 11px; }
.tags-list { padding: 0 12px 12px; display: flex; flex-wrap: wrap; gap: 6px; flex-shrink: 0; }
.tag-pill { display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 11px; border: 1px solid; cursor: pointer; transition: opacity 0.15s; }
.tag-pill:hover { opacity: 0.8; }
.empty-hint { color: #444; font-size: 11px; padding: 4px 8px; }
.sources { flex: 1; overflow-y: auto; }
.source-item { padding: 6px 16px; display: flex; align-items: center; gap: 8px; color: #ccc; font-size: 12px; cursor: pointer; }
.source-item:hover { background: var(--bg-tertiary); }
.avatar { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff; flex-shrink: 0; }
.source-info { display: flex; flex-direction: column; }
.source-name { color: var(--text-primary); }
.source-platform { color: var(--text-muted); font-size: 10px; }
.sidebar-bottom { padding: 12px 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.add-btn { flex: 1; padding: 6px; background: var(--accent); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
.settings-link { padding: 6px 8px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 4px; font-size: 14px; text-decoration: none; display: flex; align-items: center; }
.settings-link:hover { color: var(--accent); border-color: var(--accent); }
.logout-btn { padding: 6px 10px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border); border-radius: 4px; cursor: pointer; font-size: 12px; }
.theme-toggle { display: flex; justify-content: center; gap: 4px; padding: 8px 16px; border-top: 1px solid var(--border); flex-shrink: 0; }
.theme-toggle button { background: transparent; border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 13px; color: var(--text-secondary); transition: all 0.15s; }
.theme-toggle button.active { background: color-mix(in srgb, var(--accent) 20%, transparent); border-color: var(--accent); }
.theme-toggle button:hover { border-color: var(--accent); }
</style>
