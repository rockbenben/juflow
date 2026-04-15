<script setup lang="ts">
import { ref } from 'vue'
import { useArticlesStore } from '../stores/articles'
import { useI18n } from 'vue-i18n'

const articles = useArticlesStore()
const { t } = useI18n()
const searchQuery = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

const colors: Record<string, string> = { csdn: '#e17055', xueqiu: '#00b894', zhihu: '#6c63ff' }

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
      <span class="title">{{ t('articles.allUnread') }}</span>
    </div>
    <div class="search-bar">
      <input
        class="search-input"
        v-model="searchQuery"
        @input="onSearch"
        :placeholder="t('articles.search')"
      />
    </div>
    <div v-if="articles.loading" class="loading">{{ t('articles.loading') }}</div>
    <div v-else-if="articles.articles.length === 0" class="empty">{{ t('articles.noArticles') }}</div>
    <div
      v-for="article in articles.articles" :key="article.id"
      class="article-item"
      :class="{ selected: articles.selected?.id === article.id, read: article.is_read }"
      @click="articles.select(article)"
    >
      <div class="article-meta">
        <div class="avatar" :style="{ background: colors[article.source.platform] || '#fdcb6e' }">
          {{ article.source.display_name.charAt(0) }}
        </div>
        <span class="meta-text">{{ article.source.display_name }} · {{ article.source.platform }} · {{ timeAgo(article.published_at) }}</span>
        <span v-if="article.is_favorited" class="fav-badge">⭐</span>
        <span v-if="article.is_read_later" class="rl-badge">🕐</span>
      </div>
      <div class="article-title">{{ article.title }}</div>
      <div class="article-summary">{{ article.summary?.slice(0, 120) }}</div>
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
  border-radius: 6px; color: var(--text-primary); padding: 7px 12px; font-size: 13px; outline: none;
  transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--accent); }
.search-input::placeholder { color: var(--text-secondary); }
.loading, .empty { padding: 20px; color: var(--text-secondary); text-align: center; }
.article-item { padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; flex-shrink: 0; }
.article-item:hover { background: var(--bg-tertiary); }
.article-item.selected { background: var(--bg-tertiary); }
.article-item.read { opacity: 0.6; }
.article-meta { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: nowrap; }
.avatar { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff; flex-shrink: 0; }
.meta-text { color: var(--text-secondary); font-size: 11px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-badge, .rl-badge { font-size: 11px; flex-shrink: 0; }
.article-title { color: var(--text-primary); font-size: 14px; margin-bottom: 4px; }
.article-summary { color: var(--text-muted); font-size: 12px; line-height: 1.5; }
</style>
