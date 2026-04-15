import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export interface ArticleSource {
  platform: string
  display_name: string
}

export interface Article {
  id: string
  title: string
  summary: string
  content: string | null
  url: string
  cover_image: string | null
  published_at: string
  source: ArticleSource
  is_read: boolean
  is_favorited: boolean
  is_read_later: boolean
}

export const useArticlesStore = defineStore('articles', () => {
  const articles = ref<Article[]>([])
  const total = ref(0)
  const selected = ref<Article | null>(null)
  const loading = ref(false)

  async function load(unreadOnly = false, limit = 50, offset = 0) {
    loading.value = true
    try {
      const { data } = await api.get('/articles/', { params: { unread_only: unreadOnly, limit, offset } })
      articles.value = data.articles
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  function select(article: Article) {
    selected.value = article
    if (!article.is_read) {
      markRead(article.id, true)
    }
  }

  async function markRead(id: string, isRead: boolean) {
    await api.patch(`/articles/${id}/read`, { is_read: isRead })
    const a = articles.value.find(a => a.id === id)
    if (a) a.is_read = isRead
  }

  function prependArticle(article: Article) {
    if (!articles.value.find(a => a.id === article.id)) {
      articles.value.unshift(article)
      total.value++
    }
  }

  async function search(q: string) {
    loading.value = true
    try {
      const { data } = await api.get('/articles/', { params: { q } })
      articles.value = data.articles
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function loadFavorites() {
    loading.value = true
    try {
      const { data } = await api.get('/articles/', { params: { filter: 'favorited' } })
      articles.value = data.articles
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function loadReadLater() {
    loading.value = true
    try {
      const { data } = await api.get('/articles/', { params: { filter: 'read_later' } })
      articles.value = data.articles
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(id: string) {
    const a = articles.value.find(a => a.id === id)
    const current = a?.is_favorited ?? false
    await api.patch(`/articles/${id}/favorite`, { is_favorited: !current })
    if (a) a.is_favorited = !current
    if (selected.value?.id === id) selected.value.is_favorited = !current
  }

  async function toggleReadLater(id: string) {
    const a = articles.value.find(a => a.id === id)
    const current = a?.is_read_later ?? false
    await api.patch(`/articles/${id}/read-later`, { is_read_later: !current })
    if (a) a.is_read_later = !current
    if (selected.value?.id === id) selected.value.is_read_later = !current
  }

  function selectNext() {
    const idx = articles.value.findIndex(a => a.id === selected.value?.id)
    if (idx < articles.value.length - 1) select(articles.value[idx + 1])
    else if (idx === -1 && articles.value.length > 0) select(articles.value[0])
  }

  function selectPrev() {
    const idx = articles.value.findIndex(a => a.id === selected.value?.id)
    if (idx > 0) select(articles.value[idx - 1])
  }

  return { articles, total, selected, loading, load, select, markRead, prependArticle, search, loadFavorites, loadReadLater, toggleFavorite, toggleReadLater, selectNext, selectPrev }
})
