<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import { useArticlesStore } from '../stores/articles'
import { useI18n } from 'vue-i18n'

const articles = useArticlesStore()
const { t } = useI18n()
const colors: Record<string, string> = { csdn: '#e17055', xueqiu: '#00b894', zhihu: '#6c63ff' }

const sanitizedContent = computed(() => {
  if (!articles.selected?.content) return ''
  return DOMPurify.sanitize(articles.selected.content, { ADD_ATTR: ['target'] })
})

function formatDate(dateStr: string) { return new Date(dateStr).toLocaleString('zh-CN') }
</script>

<template>
  <div class="reading-pane">
    <div v-if="!articles.selected" class="empty"><p>{{ t('articles.selectToRead') }}</p></div>
    <article v-else class="article-content">
      <header>
        <h1>{{ articles.selected.title }}</h1>
        <div class="article-info">
          <div class="avatar" :style="{ background: colors[articles.selected.source.platform] || '#fdcb6e' }">
            {{ articles.selected.source.display_name.charAt(0) }}
          </div>
          <span>{{ articles.selected.source.display_name }}</span>
          <span class="sep">·</span>
          <span class="platform">{{ articles.selected.source.platform }}</span>
          <span class="sep">·</span>
          <span>{{ formatDate(articles.selected.published_at) }}</span>
        </div>
      </header>
      <div class="actions">
        <a :href="articles.selected.url" target="_blank" rel="noopener">🔗 {{ t('articles.original') }}</a>
        <span
          class="action-btn"
          @click="articles.toggleFavorite(articles.selected!.id)"
        >
          {{ articles.selected.is_favorited ? '⭐' : '☆' }} {{ t('articles.favorite') }}
        </span>
        <span
          class="action-btn"
          @click="articles.toggleReadLater(articles.selected!.id)"
        >
          {{ articles.selected.is_read_later ? '🕐' : '🕑' }} {{ t('articles.readLater') }}
        </span>
      </div>
      <div class="body" v-if="articles.selected.content" v-html="sanitizedContent"></div>
      <div class="body" v-else>
        <p>{{ articles.selected.summary }}</p>
        <p class="hint"><a :href="articles.selected.url" target="_blank">点击阅读原文 →</a></p>
      </div>
    </article>
  </div>
</template>

<style scoped>
.reading-pane { flex: 1; background: var(--bg-tertiary); overflow-y: auto; height: 100vh; }
.empty { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-muted); }
.article-content { max-width: 680px; margin: 0 auto; padding: 32px; }
header { margin-bottom: 24px; }
h1 { color: var(--text-primary); font-size: 22px; line-height: 1.4; margin: 0 0 12px; }
.article-info { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 13px; flex-wrap: wrap; }
.avatar { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #fff; }
.platform { color: var(--error); }
.sep { color: var(--border); }
.actions { display: flex; gap: 16px; padding: 12px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin-bottom: 24px; align-items: center; flex-wrap: wrap; }
.actions a { color: var(--text-secondary); font-size: 12px; text-decoration: none; }
.actions a:hover { color: var(--accent); }
.action-btn { color: var(--text-secondary); font-size: 12px; cursor: pointer; user-select: none; transition: color 0.15s; }
.action-btn:hover { color: var(--accent); }
.body { color: var(--text-primary); font-size: 15px; line-height: 1.8; }
.body :deep(p) { margin: 0 0 16px; }
.body :deep(a) { color: var(--accent); }
.hint { color: var(--text-secondary); }
.hint a { color: var(--accent); }
</style>
