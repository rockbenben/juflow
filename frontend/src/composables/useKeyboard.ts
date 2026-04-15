import { onMounted, onUnmounted, ref } from 'vue'
import { useArticlesStore } from '../stores/articles'

export function useKeyboard() {
  const articles = useArticlesStore()
  const showHelp = ref(false)

  function isInputFocused(): boolean {
    const el = document.activeElement
    if (!el) return false
    const tag = el.tagName.toLowerCase()
    return tag === 'input' || tag === 'textarea' || tag === 'select' || el.getAttribute('contenteditable') === 'true'
  }

  function handleKeydown(e: KeyboardEvent) {
    if (isInputFocused()) return
    switch (e.key) {
      case 'j': case 'ArrowDown': articles.selectNext(); e.preventDefault(); break
      case 'k': case 'ArrowUp': articles.selectPrev(); e.preventDefault(); break
      case 's': if (articles.selected) articles.toggleFavorite(articles.selected.id); break
      case 'l': if (articles.selected) articles.toggleReadLater(articles.selected.id); break
      case 'm': if (articles.selected) articles.markRead(articles.selected.id, !articles.selected.is_read); break
      case 'v': if (articles.selected) window.open(articles.selected.url, '_blank'); break
      case '/': e.preventDefault(); document.querySelector<HTMLInputElement>('.search-input')?.focus(); break
      case 'Escape': showHelp.value = false; document.querySelector<HTMLInputElement>('.search-input')?.blur(); break
      case '?': showHelp.value = !showHelp.value; break
    }
  }

  onMounted(() => document.addEventListener('keydown', handleKeydown))
  onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
  return { showHelp }
}
