<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../../api/client'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const apiKey = ref<string | null>(null)
const hasFullKey = ref(false)
const loading = ref(false)
const copied = ref(false)
const regenerating = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/settings/api-key')
    if (data.has_key) {
      apiKey.value = data.api_key  // Backend returns masked "first8***"
      hasFullKey.value = false
    }
  } catch {
    // No key yet
  } finally {
    loading.value = false
  }
})

const displayKey = computed(() => {
  if (!apiKey.value) return null
  if (hasFullKey.value) {
    // Full key just generated: show first 8 + dots + last 4
    return apiKey.value.slice(0, 8) + '••••••••••••••••' + apiKey.value.slice(-4)
  }
  // Already masked from backend, show as-is
  return apiKey.value
})

async function copyKey() {
  if (!apiKey.value || !hasFullKey.value) return
  try {
    await navigator.clipboard.writeText(apiKey.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback
  }
}

async function regenerate() {
  if (!confirm(t('apiKey.confirmRegenerate'))) return
  regenerating.value = true
  try {
    const { data } = await api.post('/settings/api-key/regenerate')
    apiKey.value = data.api_key
    hasFullKey.value = true
  } catch {
    // ignore
  } finally {
    regenerating.value = false
  }
}

async function createKey() {
  loading.value = true
  try {
    const { data } = await api.post('/settings/api-key/regenerate')
    apiKey.value = data.api_key
    hasFullKey.value = true
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="api-key-section">
    <div class="card">
      <h3>{{ t('apiKey.title') }}</h3>
      <p class="description">{{ t('apiKey.desc') }}</p>

      <div v-if="loading" class="loading-text" role="status">{{ t('apiKey.loading') }}</div>

      <div v-else-if="!apiKey" class="no-key">
        <p class="hint">{{ t('apiKey.noKey') }}</p>
        <button class="create-btn" @click="createKey">{{ t('apiKey.create') }}</button>
      </div>

      <div v-else class="key-display">
        <div class="key-row">
          <code class="key-code">{{ displayKey }}</code>
          <button
            class="copy-btn"
            @click="copyKey"
            :class="{ copied }"
            :disabled="!hasFullKey"
            :title="hasFullKey ? '' : t('apiKey.copyFullOnly')"
          >
            {{ copied ? t('apiKey.copied') : t('apiKey.copy') }}
          </button>
        </div>
        <div class="key-actions">
          <button class="regen-btn" @click="regenerate" :disabled="regenerating">
            {{ regenerating ? t('apiKey.regenerating') : t('apiKey.regenerate') }}
          </button>
        </div>
        <p class="warning">{{ t('apiKey.warning') }}</p>
      </div>
    </div>

    <div class="card">
      <h3>{{ t('apiKey.usage') }}</h3>
      <pre class="code-example">X-API-Key: &lt;your-api-key&gt;</pre>
      <p class="description">{{ t('apiKey.usageDesc', { docs: '/docs' }) }}</p>
    </div>
  </div>
</template>

<style scoped>
.api-key-section { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
h3 { color: var(--text-primary); font-size: 14px; margin: 0 0 8px; }
.description { color: var(--text-secondary); font-size: 13px; margin: 0 0 16px; }
.loading-text { color: var(--text-secondary); font-size: 13px; }
.no-key .hint { color: var(--text-secondary); font-size: 13px; margin: 0 0 12px; }
.create-btn {
  padding: 8px 20px; background: var(--accent-strong); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit;
}
.create-btn:hover { background: var(--accent-strong-hover); }
.key-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.key-code {
  flex: 1; padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; font-family: monospace; font-size: 13px; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.copy-btn {
  padding: 6px 14px; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-secondary); cursor: pointer; font-size: 12px; font-family: inherit;
  white-space: nowrap; transition: all 0.2s;
}
.copy-btn.copied { border-color: var(--success); color: var(--success); }
.copy-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent-text); }
.copy-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.key-actions { margin-bottom: 10px; }
.regen-btn {
  padding: 6px 14px; background: transparent; color: var(--error); border: 1px solid var(--error);
  border-radius: 6px; cursor: pointer; font-size: 12px; font-family: inherit; transition: opacity 0.2s;
}
.regen-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.warning { color: var(--text-muted); font-size: 12px; margin: 0; }
.code-example {
  background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;
  padding: 10px 14px; font-family: monospace; font-size: 12px; color: var(--text-primary);
  margin: 0 0 8px; overflow-x: auto;
}
</style>
