<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'

interface PlatformHealth {
  platform: string
  total: number
  success_count: number
  success_rate: number
  avg_duration_ms: number
  last_error: string | null
}

const health = ref<PlatformHealth[]>([])
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/admin/health')
    health.value = Array.isArray(data) ? data : (data.platforms || [])
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
})

function successRate(p: PlatformHealth): number {
  return Math.round(p.success_rate * 100)
}

function rateBadgeClass(rate: number): string {
  if (rate >= 95) return 'badge-green'
  if (rate >= 80) return 'badge-yellow'
  return 'badge-red'
}
</script>

<template>
  <div class="health-dashboard">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="health.length === 0" class="empty">暂无监控数据</div>
    <div v-for="p in health" :key="p.platform" class="platform-card">
      <div class="card-top">
        <div class="platform-name">{{ p.platform }}</div>
        <span class="rate-badge" :class="rateBadgeClass(successRate(p))">
          {{ successRate(p) }}% 成功
        </span>
      </div>
      <div class="stats-row">
        <div class="stat">
          <span class="stat-label">总计</span>
          <span class="stat-value">{{ p.total }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">成功</span>
          <span class="stat-value success-val">{{ p.success_count }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">失败</span>
          <span class="stat-value error-val">{{ p.total - p.success_count }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">平均耗时</span>
          <span class="stat-value">{{ p.avg_duration_ms }}ms</span>
        </div>
      </div>
      <div v-if="p.last_error" class="last-error">
        <span class="error-label">最后错误：</span>{{ p.last_error }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.health-dashboard { display: flex; flex-direction: column; gap: 16px; }
.loading, .empty { color: var(--text-secondary); text-align: center; padding: 32px 0; }
.error { color: var(--error); text-align: center; padding: 16px 0; }
.platform-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.platform-name { color: var(--text-primary); font-size: 14px; font-weight: 600; text-transform: capitalize; }
.rate-badge { font-size: 12px; padding: 2px 10px; border-radius: 10px; font-weight: 600; }
.badge-green { background: color-mix(in srgb, var(--success) 20%, transparent); color: var(--success); }
.badge-yellow { background: color-mix(in srgb, #fdcb6e 20%, transparent); color: #fdcb6e; }
.badge-red { background: color-mix(in srgb, var(--error) 20%, transparent); color: var(--error); }
.stats-row { display: flex; gap: 20px; margin-bottom: 10px; flex-wrap: wrap; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-label { color: var(--text-muted); font-size: 11px; }
.stat-value { color: var(--text-primary); font-size: 14px; font-weight: 600; }
.success-val { color: var(--success); }
.error-val { color: var(--error); }
.last-error { color: var(--text-secondary); font-size: 12px; margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.error-label { color: var(--error); }
</style>
