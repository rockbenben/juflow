<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/client'

interface RecommendedSource {
  name: string
  url: string
  platform: string
  description: string
}
interface Category {
  category: string
  sources: RecommendedSource[]
}

const emit = defineEmits<{ (e: 'close'): void }>()
const categories = ref<Category[]>([])
const selected = ref<Set<string>>(new Set())
const subscribing = ref(false)
const done = ref(false)
const results = ref<{ url: string; ok: boolean; error?: string }[]>([])

onMounted(async () => {
  const { data } = await api.get('/onboarding/recommended')
  categories.value = data
  // Pre-select all
  for (const cat of data) {
    for (const s of cat.sources) {
      selected.value.add(s.url)
    }
  }
})

function toggle(url: string) {
  if (selected.value.has(url)) selected.value.delete(url)
  else selected.value.add(url)
}

async function subscribe() {
  subscribing.value = true
  try {
    const { data } = await api.post('/onboarding/batch-subscribe', [...selected.value])
    results.value = data.results
    done.value = true
  } finally {
    subscribing.value = false
  }
}

const successCount = () => results.value.filter(r => r.ok).length
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <div v-if="!done">
        <h2>欢迎使用聚流 🎉</h2>
        <p class="subtitle">选择你感兴趣的博主，一键订阅开始阅读。</p>

        <div v-for="cat in categories" :key="cat.category" class="category">
          <h3>{{ cat.category }}</h3>
          <div
            v-for="s in cat.sources" :key="s.url"
            class="source-item"
            :class="{ active: selected.has(s.url) }"
            @click="toggle(s.url)"
          >
            <div class="check">{{ selected.has(s.url) ? '✓' : '' }}</div>
            <div class="info">
              <span class="name">{{ s.name }}</span>
              <span class="platform-badge">{{ s.platform }}</span>
              <p class="desc">{{ s.description }}</p>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="skip-btn" @click="emit('close')">跳过</button>
          <button
            class="subscribe-btn"
            @click="subscribe"
            :disabled="selected.size === 0 || subscribing"
          >
            {{ subscribing ? '订阅中...' : `订阅 ${selected.size} 个源` }}
          </button>
        </div>
      </div>

      <div v-else class="done-screen">
        <h2>订阅完成 ✓</h2>
        <p>成功订阅 {{ successCount() }} 个源，文章将在几分钟内开始出现。</p>
        <button class="subscribe-btn" @click="emit('close')">开始阅读</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--bg-secondary); border-radius: 12px; padding: 28px; width: 480px;
  max-height: 80vh; overflow-y: auto; border: 1px solid var(--border);
}
h2 { color: var(--text-primary); font-size: 20px; margin: 0 0 6px; }
.subtitle { color: var(--text-secondary); font-size: 13px; margin: 0 0 20px; }
.category { margin-bottom: 16px; }
h3 { color: var(--accent); font-size: 13px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.source-item {
  display: flex; gap: 10px; padding: 10px 12px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--border); margin-bottom: 6px; transition: all 0.15s;
}
.source-item:hover { border-color: var(--accent); }
.source-item.active { border-color: var(--accent); background: rgba(108,99,255,0.08); }
.check {
  width: 22px; height: 22px; border-radius: 4px; background: var(--bg-tertiary);
  display: flex; align-items: center; justify-content: center; font-size: 12px;
  color: var(--accent); flex-shrink: 0; margin-top: 2px;
}
.source-item.active .check { background: var(--accent); color: #fff; }
.info { flex: 1; min-width: 0; }
.name { color: var(--text-primary); font-size: 14px; font-weight: 500; }
.platform-badge {
  font-size: 11px; color: var(--text-secondary); background: var(--bg-tertiary);
  padding: 1px 6px; border-radius: 3px; margin-left: 6px;
}
.desc { color: var(--text-muted); font-size: 12px; margin: 2px 0 0; }
.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
.skip-btn {
  padding: 8px 20px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border);
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.subscribe-btn {
  padding: 8px 24px; background: var(--accent); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.subscribe-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.done-screen { text-align: center; padding: 20px 0; }
.done-screen p { color: var(--text-secondary); font-size: 14px; margin: 8px 0 20px; }
</style>
