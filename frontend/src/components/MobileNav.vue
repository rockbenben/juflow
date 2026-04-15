<script setup lang="ts">
import { useRouter } from 'vue-router'

defineProps<{ tab: string }>()
defineEmits<{ (e: 'tab', value: string): void }>()

const router = useRouter()
</script>

<template>
  <nav class="mobile-nav">
    <button :class="{ active: tab === 'feed' }" @click="$emit('tab', 'feed')">📥 未读</button>
    <button :class="{ active: tab === 'favorites' }" @click="$emit('tab', 'favorites')">⭐ 收藏</button>
    <button @click="router.push('/settings')">⚙️ 设置</button>
  </nav>
</template>

<style scoped>
.mobile-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-secondary); border-top: 1px solid var(--border); padding: 8px; justify-content: space-around; z-index: 50; }
@media (max-width: 768px) { .mobile-nav { display: flex; } }
button { background: none; border: none; color: var(--text-secondary); font-size: 12px; cursor: pointer; padding: 8px 16px; }
button.active { color: var(--accent); }
</style>
