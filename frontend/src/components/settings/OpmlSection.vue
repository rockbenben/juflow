<script setup lang="ts">
import { ref } from 'vue'
import api from '../../api/client'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
interface SkippedItem { url: string; title: string; reason: string }
const importResult = ref<{ imported: number; skipped: SkippedItem[] } | null>(null)
const importError = ref('')

async function handleImport() {
  const file = fileInput.value?.files?.[0]
  if (!file) return

  uploading.value = true
  importResult.value = null
  importError.value = ''

  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await api.post('/opml/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    importResult.value = { imported: data.imported ?? 0, skipped: data.skipped ?? [] }
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    importError.value = err.response?.data?.detail || t('opml.importFailed')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function exportOpml() {
  // The export endpoint requires auth (Bearer/X-API-Key header). A plain <a href>
  // navigation can't send those, so fetch via the API client and download the blob.
  const { data } = await api.get('/opml/export', { responseType: 'blob' })
  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'juflow-subscriptions.opml'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="opml-section">
    <div class="card">
      <h3>{{ t('opml.importTitle') }}</h3>
      <p class="description">{{ t('opml.importDesc') }}</p>
      <div class="import-row">
        <input
          ref="fileInput"
          type="file"
          accept=".opml,.xml"
          class="file-input"
          id="opml-file"
        />
        <label for="opml-file" class="file-label">
          {{ t('opml.chooseFile') }}
        </label>
        <button class="import-btn" @click="handleImport" :disabled="uploading">
          {{ uploading ? t('opml.importing') : t('opml.uploadImport') }}
        </button>
      </div>

      <div v-if="importResult" class="result-box" role="status">
        <p class="result-imported">{{ t('opml.imported', { n: importResult.imported }) }}</p>
        <div v-if="importResult.skipped.length > 0" class="skipped-list">
          <p class="skipped-title">{{ t('opml.skipped', { n: importResult.skipped.length }) }}</p>
          <ul>
            <li v-for="(item, i) in importResult.skipped" :key="i">{{ item.title || item.url }} — {{ item.reason }}</li>
          </ul>
        </div>
      </div>
      <p v-if="importError" class="error-msg" role="alert">{{ importError }}</p>
    </div>

    <div class="card">
      <h3>{{ t('opml.exportTitle') }}</h3>
      <p class="description">{{ t('opml.exportDesc') }}</p>
      <button type="button" class="export-btn" @click="exportOpml">
        {{ t('opml.download') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.opml-section { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
h3 { color: var(--text-primary); font-size: 14px; margin: 0 0 8px; }
.description { color: var(--text-secondary); font-size: 13px; margin: 0 0 16px; }
.import-row { display: flex; align-items: center; gap: 10px; }
.file-input { display: none; }
.file-label {
  padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text-secondary); font-size: 13px; cursor: pointer; transition: border-color 0.2s; white-space: nowrap;
}
.file-label:hover { border-color: var(--accent); color: var(--text-primary); }
.import-btn {
  padding: 8px 20px; background: var(--accent-strong); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; transition: opacity 0.2s; white-space: nowrap;
}
.import-btn:hover:not(:disabled) { background: var(--accent-strong-hover); }
.import-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.result-box { margin-top: 16px; padding: 12px 16px; background: color-mix(in srgb, var(--success) 10%, var(--bg-secondary)); border: 1px solid color-mix(in srgb, var(--success) 30%, transparent); border-radius: 6px; }
.result-imported { color: var(--success); font-size: 13px; margin: 0 0 8px; }
.skipped-title { color: var(--text-primary); font-weight: 600; font-size: 12px; margin: 0 0 6px; }
.skipped-list ul { margin: 0; padding-left: 20px; }
.skipped-list li { color: var(--text-secondary); font-size: 12px; margin-bottom: 3px; }
.error-msg { color: var(--error); font-size: 13px; margin-top: 12px; }
.export-btn {
  display: inline-block; padding: 8px 20px; background: var(--bg-tertiary); border: 1px solid var(--accent);
  border-radius: 6px; color: var(--accent-text); font-size: 13px; font-family: inherit; text-decoration: none; transition: background 0.2s;
  cursor: pointer;
}
.export-btn:hover { background: var(--accent-strong); color: #fff; border-color: var(--accent-strong); }
</style>
