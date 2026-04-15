<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'

interface Plugin {
  name: string
  display_name: string
  version: string
  author: string
  description: string
  adapter_class: string
  enabled: boolean
  installed_at: string
}

const plugins = ref<Plugin[]>([])
const gitUrl = ref('')
const installing = ref(false)
const installError = ref('')
const installSuccess = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/plugins/')
    plugins.value = data
  } catch {
    // Backend may not have plugin endpoint yet
  }
})

async function installFromGit() {
  if (!gitUrl.value.trim()) return
  installing.value = true
  installError.value = ''
  installSuccess.value = ''
  try {
    const { data } = await api.post('/plugins/install/git', { url: gitUrl.value.trim() })
    plugins.value.push(data as Plugin)
    installSuccess.value = `已安装插件 ${data.display_name}`
    gitUrl.value = ''
    // Reload full list to get complete fields
    const { data: all } = await api.get('/plugins/')
    plugins.value = all
  } catch (e: any) {
    installError.value = e.response?.data?.detail || '安装失败'
  } finally {
    installing.value = false
    setTimeout(() => { installSuccess.value = '' }, 3000)
  }
}

async function installFromZip() {
  const file = fileInput.value?.files?.[0]
  if (!file) return
  installing.value = true
  installError.value = ''
  installSuccess.value = ''
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { data } = await api.post('/plugins/install/zip', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    installSuccess.value = `已安装插件 ${data.display_name}`
    const { data: all } = await api.get('/plugins/')
    plugins.value = all
  } catch (e: any) {
    installError.value = e.response?.data?.detail || 'ZIP 安装失败'
  } finally {
    installing.value = false
    if (fileInput.value) fileInput.value.value = ''
    setTimeout(() => { installSuccess.value = '' }, 3000)
  }
}

async function togglePlugin(plugin: Plugin) {
  const action = plugin.enabled ? 'disable' : 'enable'
  try {
    const { data } = await api.post(`/plugins/${plugin.name}/${action}`)
    plugin.enabled = data.enabled
  } catch {
    // ignore
  }
}

async function uninstall(plugin: Plugin) {
  if (!confirm(`确定卸载插件 ${plugin.display_name}？`)) return
  try {
    await api.delete(`/plugins/${plugin.name}`)
    plugins.value = plugins.value.filter(p => p.name !== plugin.name)
  } catch {
    // ignore
  }
}
</script>

<template>
  <div class="plugin-manager">
    <div class="card">
      <h3>安装插件</h3>
      <div class="install-row">
        <input
          v-model="gitUrl"
          type="url"
          placeholder="Git 仓库 URL (https://github.com/...)"
          class="url-input"
        />
        <button class="install-btn" @click="installFromGit" :disabled="installing">
          {{ installing ? '安装中...' : '从 Git 安装' }}
        </button>
      </div>
      <div class="install-row zip-row">
        <input ref="fileInput" type="file" accept=".zip" class="file-input" id="plugin-zip" />
        <label for="plugin-zip" class="file-label">选择 ZIP 文件</label>
        <button class="install-btn" @click="installFromZip" :disabled="installing">
          从 ZIP 安装
        </button>
      </div>
      <p v-if="installError" class="error">{{ installError }}</p>
      <p v-if="installSuccess" class="success">{{ installSuccess }}</p>
    </div>

    <div class="card">
      <h3>已安装插件</h3>
      <div v-if="plugins.length === 0" class="empty">暂无安装的插件</div>
      <div v-for="plugin in plugins" :key="plugin.name" class="plugin-item">
        <div class="plugin-info">
          <div class="plugin-name">{{ plugin.display_name }}</div>
          <div class="plugin-meta">v{{ plugin.version }} · {{ plugin.author }}</div>
          <div class="plugin-desc">{{ plugin.description }}</div>
        </div>
        <div class="plugin-actions">
          <div
            class="toggle"
            :class="{ on: plugin.enabled }"
            @click="togglePlugin(plugin)"
            :title="plugin.enabled ? '已启用' : '已禁用'"
          >
            <div class="toggle-knob"></div>
          </div>
          <button class="uninstall-btn" @click="uninstall(plugin)">卸载</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plugin-manager { display: flex; flex-direction: column; gap: 16px; }
.card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
h3 { color: var(--text-primary); font-size: 14px; margin: 0 0 16px; }
.install-row { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
.zip-row { margin-top: 4px; }
.url-input {
  flex: 1; padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-primary); font-size: 13px; outline: none;
  transition: border-color 0.2s;
}
.url-input:focus { border-color: var(--accent); }
.install-btn {
  padding: 8px 16px; background: var(--accent); color: #fff; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px; white-space: nowrap;
  transition: opacity 0.2s;
}
.install-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.file-input { display: none; }
.file-label {
  padding: 8px 14px; background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-secondary); font-size: 13px; cursor: pointer;
  white-space: nowrap; transition: border-color 0.2s;
}
.file-label:hover { border-color: var(--accent); color: var(--text-primary); }
.error { color: var(--error); font-size: 13px; margin-top: 8px; }
.success { color: var(--success); font-size: 13px; margin-top: 8px; }
.empty { color: var(--text-secondary); font-size: 13px; text-align: center; padding: 16px 0; }
.plugin-item {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 12px 0; border-bottom: 1px solid var(--border);
}
.plugin-item:last-child { border-bottom: none; padding-bottom: 0; }
.plugin-info { flex: 1; }
.plugin-name { color: var(--text-primary); font-size: 14px; font-weight: 600; margin-bottom: 2px; }
.plugin-meta { color: var(--text-secondary); font-size: 11px; margin-bottom: 4px; }
.plugin-desc { color: var(--text-muted); font-size: 12px; }
.plugin-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; margin-left: 16px; }
.toggle { width: 40px; height: 22px; background: var(--border); border-radius: 11px; position: relative; cursor: pointer; transition: background 0.2s; }
.toggle.on { background: var(--accent); }
.toggle-knob { width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
.toggle.on .toggle-knob { left: 20px; }
.uninstall-btn {
  padding: 4px 10px; background: transparent; color: var(--error);
  border: 1px solid var(--error); border-radius: 4px; cursor: pointer; font-size: 12px;
  transition: opacity 0.2s;
}
.uninstall-btn:hover { opacity: 0.8; }
</style>
