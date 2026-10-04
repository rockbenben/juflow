<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/client'
import { useI18n } from 'vue-i18n'

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
const { t } = useI18n()
const categories = ref<Category[]>([])
const selected = ref<Set<string>>(new Set())
const subscribing = ref(false)
const done = ref(false)
const results = ref<{ url: string; ok: boolean; error?: string }[]>([])

const allUrls = computed(() => categories.value.flatMap(c => c.sources.map(s => s.url)))

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

function selectAll() {
  selected.value = new Set(allUrls.value)
}

function clearAll() {
  selected.value = new Set()
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
  <div class="overlay" role="dialog" aria-modal="true" :aria-label="t('onboarding.welcome')" @click.self="emit('close')" @keydown.esc.window="emit('close')">
    <div class="modal">
      <div v-if="!done">
        <h2>{{ t('onboarding.welcome') }}</h2>
        <p class="subtitle">{{ t('onboarding.subtitle') }}</p>

        <div class="select-row">
          <button type="button" class="link-btn" @click="selectAll">{{ t('onboarding.selectAll') }}</button>
          <span class="sep">/</span>
          <button type="button" class="link-btn" @click="clearAll">{{ t('onboarding.clearAll') }}</button>
        </div>

        <div v-for="cat in categories" :key="cat.category" class="category">
          <h3>{{ cat.category }}</h3>
          <button
            v-for="s in cat.sources" :key="s.url"
            type="button"
            class="source-item"
            :class="{ active: selected.has(s.url) }"
            :aria-pressed="selected.has(s.url)"
            @click="toggle(s.url)"
          >
            <span class="check">{{ selected.has(s.url) ? '✓' : '' }}</span>
            <span class="info">
              <span class="name">{{ s.name }}</span>
              <span class="platform-badge">{{ s.platform }}</span>
              <span class="desc">{{ s.description }}</span>
            </span>
          </button>
        </div>

        <div class="actions">
          <button class="skip-btn" @click="emit('close')">{{ t('onboarding.skip') }}</button>
          <button
            class="subscribe-btn"
            @click="subscribe"
            :disabled="selected.size === 0 || subscribing"
          >
            {{ subscribing ? t('onboarding.subscribing') : t('onboarding.subscribeN', { n: selected.size }) }}
          </button>
        </div>
      </div>

      <div v-else class="done-screen">
        <h2>{{ t('onboarding.done') }}</h2>
        <p>{{ t('onboarding.doneSummary', { n: successCount() }) }}</p>
        <button class="subscribe-btn" @click="emit('close')">{{ t('onboarding.startReading') }}</button>
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
  max-width: calc(100vw - 32px); max-height: 85vh; overflow-y: auto; border: 1px solid var(--border);
}
h2 { color: var(--text-primary); font-size: 20px; margin: 0 0 6px; }
.subtitle { color: var(--text-secondary); font-size: 13px; margin: 0 0 12px; }
.select-row { display: flex; gap: 6px; align-items: center; margin-bottom: 16px; font-size: 12px; color: var(--text-muted); }
.link-btn { background: none; border: none; padding: 0; color: var(--accent-text); font-size: 12px; font-family: inherit; cursor: pointer; }
.link-btn:hover { text-decoration: underline; }
.category { margin-bottom: 16px; }
h3 { color: var(--accent-text); font-size: 13px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.source-item {
  display: flex; gap: 10px; width: 100%; text-align: left; padding: 10px 12px; border-radius: 8px; cursor: pointer;
  background: none; font-family: inherit; border: 1px solid var(--border); margin-bottom: 6px; transition: all 0.15s;
}
.source-item:hover { border-color: var(--accent); }
.source-item.active { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
.check {
  width: 22px; height: 22px; border-radius: 4px; background: var(--bg-tertiary);
  display: flex; align-items: center; justify-content: center; font-size: 12px;
  color: var(--text-secondary); flex-shrink: 0; margin-top: 2px;
}
.source-item.active .check { background: var(--accent-strong); color: #fff; }
.info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.name { color: var(--text-primary); font-size: 14px; font-weight: 500; }
.platform-badge {
  font-size: 11px; color: var(--text-secondary); background: var(--bg-tertiary);
  padding: 1px 6px; border-radius: 3px; margin-top: 2px; align-self: flex-start;
}
.desc { color: var(--text-muted); font-size: 12px; margin-top: 2px; }
.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
.skip-btn {
  padding: 8px 20px; background: transparent; color: var(--text-secondary); border: 1px solid var(--border);
  border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit;
}
.skip-btn:hover { color: var(--text-primary); }
.subscribe-btn {
  padding: 8px 24px; background: var(--accent-strong); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit;
}
.subscribe-btn:hover:not(:disabled) { background: var(--accent-strong-hover); }
.subscribe-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.done-screen { text-align: center; padding: 20px 0; }
.done-screen p { color: var(--text-secondary); font-size: 14px; margin: 8px 0 20px; }
</style>
