<script setup lang="ts">
import { computed, ref } from 'vue'
import { useArticlesStore } from '../stores/articles'
import { platformColor, onColor } from '../composables/usePlatform'
import { useI18n } from 'vue-i18n'

const articles = useArticlesStore()
const { t } = useI18n()
const searchQuery = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

const filterTitle = computed(() => {
  switch (articles.filter) {
    case 'favorites': return t('sidebar.favorites')
    case 'read_later': return t('sidebar.readLater')
    case 'search': return t('articles.search').replace('…', '')
    default: return t('articles.allUnread')
  }
})

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return t('articles.justNow')
  if (mins < 60) return t('articles.minutesAgo', { n: mins })
  const hours = Math.floor(mins / 60)
  if (hours < 24) return t('articles.hoursAgo', { n: hours })
  return t('articles.daysAgo', { n: Math.floor(hours / 24) })
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    const q = searchQuery.value.trim()
    if (q) {
      await articles.search(q)
    } else {
      await articles.load()
    }
  }, 300)
}
</script>

<template>
  <div class="article-list">
    <div class="list-header">
      <span class="title">{{ filterTitle }}</span>
    </div>
    <div class="search-bar">
      <input
        class="search-input"
        v-model="searchQuery"
        @input="onSearch"
        type="search"
        :placeholder="t('articles.search')"
        :aria-label="t('articles.searchAria')"
      />
    </div>
    <div v-if="articles.loading" class="loading" role="status">{{ t('articles.loading') }}</div>
    <div v-else-if="articles.articles.length === 0" class="empty">
      <template v-if="searchQuery.trim()">{{ t('articles.noMatch') }}</template>
      <template v-else>
        <p class="empty-title">{{ t('articles.noArticles') }}</p>
        <p class="empty-hint">{{ t('articles.emptyHint') }}</p>
      </template>
    </div>
    <div
      v-for="article in articles.articles" :key="article.id"
      class="article-item"
      role="button"
      tabindex="0"
      :class="{ selected: articles.selected?.id === article.id, read: article.is_read }"
      :aria-pressed="articles.selected?.id === article.id"
      @click="articles.select(article)"
      @keydown.enter.prevent="articles.select(article)"
      @keydown.space.prevent="articles.select(article)"
    >
      <div class="article-meta">
        <span class="avatar" :style="{ background: platformColor(article.source.platform), color: onColor(platformColor(article.source.platform)) }">
          {{ article.source.display_name.charAt(0) }}
        </span>
        <span class="meta-text">{{ article.source.display_name }} · {{ article.source.platform }} · {{ timeAgo(article.published_at) }}</span>
        <span v-if="article.is_favorited" class="fav-badge" :title="t('articles.favorite')">⭐</span>
        <span v-if="article.is_read_later" class="rl-badge" :title="t('articles.readLater')">🕐</span>
      </div>
      <div class="article-title">{{ article.title }}</div>
      <div v-if="article.summary" class="article-summary">{{ article.summary }}</div>
    </div>
  </div>
</template>

<style scoped>
.article-list { width: 340px; background: var(--bg-secondary); border-right: 1px solid var(--border); flex-shrink: 0; overflow-y: auto; height: 100vh; display: flex; flex-direction: column; }
.list-header { padding: 14px 16px 8px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
.title { color: var(--text-primary); font-weight: bold; font-size: 14px; }
.search-bar { padding: 8px 12px; flex-shrink: 0; }
.search-input {
  width: 100%; box-sizing: border-box; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-primary); padding: 7px 12px; font-size: 13px;
  transition: border-color 0.2s;
}
.search-input:focus-visible { border-color: var(--accent); outline: 2px solid var(--accent-text); outline-offset: 1px; }
.search-input::placeholder { color: var(--text-muted); }
.loading, .empty { padding: 20px; color: var(--text-secondary); text-align: center; }
.empty-title { margin: 0; }
.empty-hint { margin: 8px 0 0; font-size: 12px; color: var(--text-muted); line-height: 1.6; text-align: left; }
.article-item { padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; flex-shrink: 0; }
.article-item:hover { background: var(--bg-tertiary); }
.article-item.selected { background: var(--bg-tertiary); }
.article-item.read .article-title { color: var(--text-secondary); }
.article-meta { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: nowrap; }
.avatar { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; }
.meta-text { color: var(--text-secondary); font-size: 11px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-badge, .rl-badge { font-size: 11px; flex-shrink: 0; }
.article-title { color: var(--text-primary); font-size: 14px; margin-bottom: 4px; }
.article-summary {
  color: var(--text-muted); font-size: 12px; line-height: 1.5;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
}
</style>
