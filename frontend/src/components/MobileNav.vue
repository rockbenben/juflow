<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ tab: string }>()
const emit = defineEmits<{ (e: 'tab', value: string): void }>()

const { t } = useI18n()

function go(tab: string) {
  emit('tab', tab)
}
</script>

<template>
  <nav class="mobile-nav" :aria-label="t('settings.title')">
    <button :aria-current="tab === 'feed' ? 'page' : undefined" @click="go('feed')">📥 {{ t('sidebar.unread') }}</button>
    <button :aria-current="tab === 'favorites' ? 'page' : undefined" @click="go('favorites')">⭐ {{ t('sidebar.favorites') }}</button>
    <button :aria-current="tab === 'read_later' ? 'page' : undefined" @click="go('read_later')">🕐 {{ t('sidebar.readLater') }}</button>
    <router-link to="/settings">⚙️ {{ t('sidebar.settings') }}</router-link>
  </nav>
</template>

<style scoped>
.mobile-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-secondary); border-top: 1px solid var(--border); padding: 8px; justify-content: space-around; z-index: 50; }
@media (max-width: 768px) { .mobile-nav { display: flex; } }
button, .mobile-nav a { background: none; border: none; color: var(--text-secondary); font-size: 12px; font-family: inherit; cursor: pointer; padding: 8px 16px; text-decoration: none; }
button[aria-current="page"] { color: var(--accent-text); }
</style>
