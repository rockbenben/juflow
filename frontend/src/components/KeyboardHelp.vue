<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
defineEmits<{ (e: 'close'): void }>()

const shortcuts = [
  { key: 'j / ↓', desc: 'keyboard.next' },
  { key: 'k / ↑', desc: 'keyboard.prev' },
  { key: 's', desc: 'keyboard.fav' },
  { key: 'l', desc: 'keyboard.later' },
  { key: 'm', desc: 'keyboard.read' },
  { key: 'v', desc: 'keyboard.original' },
  { key: '/', desc: 'keyboard.search' },
  { key: 'Esc', desc: 'keyboard.close' },
  { key: '?', desc: 'keyboard.help' },
]
</script>

<template>
  <div class="help-overlay" @click.self="$emit('close')">
    <div class="help-panel">
      <div class="help-header">
        <h2>{{ t('keyboard.title') }}</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      <div class="shortcuts-grid">
        <template v-for="s in shortcuts" :key="s.key">
          <kbd class="kbd">{{ s.key }}</kbd>
          <span class="desc">{{ t(s.desc) }}</span>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.help-overlay {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.help-panel {
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px; width: 380px; max-width: 95vw;
}
.help-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
h2 { color: var(--text-primary); font-size: 16px; margin: 0; }
.close-btn {
  background: none; border: none; color: var(--text-secondary);
  font-size: 16px; cursor: pointer; padding: 4px;
}
.close-btn:hover { color: var(--text-primary); }
.shortcuts-grid {
  display: grid; grid-template-columns: auto 1fr;
  gap: 10px 16px; align-items: center;
}
.kbd {
  display: inline-block; padding: 3px 8px;
  background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 4px; font-family: monospace; font-size: 12px;
  color: var(--text-primary); white-space: nowrap;
}
.desc { color: var(--text-secondary); font-size: 13px; }
</style>
