<script setup lang="ts">
import { ref } from 'vue'
import api from '../../api/client'

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const importResult = ref<{ imported: number; skipped: string[] } | null>(null)
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
    importError.value = err.response?.data?.detail || '导入失败，请检查文件格式'
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function getExportUrl() {
  return '/api/v1/opml/export'
}
</script>

<template>
  <div class="opml-section">
    <div class="card">
      <h3>导入 OPML</h3>
      <p class="description">支持标准 OPML 格式的订阅列表文件（.opml 或 .xml）。</p>
      <div class="import-row">
        <input
          ref="fileInput"
          type="file"
          accept=".opml,.xml"
          class="file-input"
          id="opml-file"
        />
        <label for="opml-file" class="file-label">
          选择文件
        </label>
        <button class="import-btn" @click="handleImport" :disabled="uploading">
          {{ uploading ? '导入中...' : '上传导入' }}
        </button>
      </div>

      <div v-if="importResult" class="result-box">
        <p class="result-imported">成功导入 {{ importResult.imported }} 个订阅源</p>
        <div v-if="importResult.skipped.length > 0" class="skipped-list">
          <p class="skipped-title">跳过 {{ importResult.skipped.length }} 个（已存在或格式错误）：</p>
          <ul>
            <li v-for="(item, i) in importResult.skipped" :key="i">{{ item }}</li>
          </ul>
        </div>
      </div>
      <p v-if="importError" class="error-msg">{{ importError }}</p>
    </div>

    <div class="card">
      <h3>导出 OPML</h3>
      <p class="description">将当前所有订阅源导出为 OPML 文件，可用于备份或导入其他阅读器。</p>
      <a :href="getExportUrl()" class="export-btn" download="juflow-subscriptions.opml">
        下载 OPML 文件
      </a>
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
  color: #aaa; font-size: 13px; cursor: pointer; transition: border-color 0.2s; white-space: nowrap;
}
.file-label:hover { border-color: var(--accent); color: var(--text-primary); }
.import-btn {
  padding: 8px 20px; background: var(--accent); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; transition: opacity 0.2s; white-space: nowrap;
}
.import-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.result-box { margin-top: 16px; padding: 12px 16px; background: color-mix(in srgb, var(--success) 10%, var(--bg-secondary)); border: 1px solid color-mix(in srgb, var(--success) 30%, transparent); border-radius: 6px; }
.result-imported { color: var(--success); font-size: 13px; margin: 0 0 8px; }
.skipped-title { color: #fdcb6e; font-size: 12px; margin: 0 0 6px; }
.skipped-list ul { margin: 0; padding-left: 20px; }
.skipped-list li { color: var(--text-secondary); font-size: 12px; margin-bottom: 3px; }
.error-msg { color: var(--error); font-size: 13px; margin-top: 12px; }
.export-btn {
  display: inline-block; padding: 8px 20px; background: var(--bg-tertiary); border: 1px solid var(--accent);
  border-radius: 6px; color: var(--accent); font-size: 13px; text-decoration: none; transition: background 0.2s;
}
.export-btn:hover { background: var(--accent); color: #fff; }
</style>
