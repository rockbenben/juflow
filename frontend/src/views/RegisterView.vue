<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const auth = useAuthStore()
const { t } = useI18n()
const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')

async function handleRegister() {
  error.value = ''
  try {
    await auth.register(email.value, username.value, password.value)
  } catch (e: any) {
    const detail = e.response?.data?.detail
    error.value = Array.isArray(detail) ? detail.map((d: any) => d.msg).join('; ') : (detail || '注册失败')
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="logo">聚流</h1>
      <p class="subtitle">创建你的账号</p>
      <form @submit.prevent="handleRegister">
        <input v-model="email" type="email" :placeholder="t('auth.email')" required />
        <input v-model="username" type="text" :placeholder="t('auth.username')" required />
        <input v-model="password" type="password" :placeholder="t('auth.password')" required />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit">{{ t('auth.register') }}</button>
      </form>
      <p class="link">{{ t('auth.hasAccount') }}<router-link to="/login">{{ t('auth.login') }}</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg-primary); }
.auth-card { background: var(--bg-tertiary); border-radius: 12px; padding: 40px; width: 360px; }
.logo { color: var(--accent); font-size: 28px; text-align: center; margin: 0 0 4px; }
.subtitle { color: var(--text-muted); text-align: center; font-size: 13px; margin: 0 0 24px; }
input { width: 100%; padding: 10px 12px; margin-bottom: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 14px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background: var(--accent); color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
button:hover { background: var(--accent-hover); }
.error { color: var(--error); font-size: 13px; margin: 0 0 8px; }
.link { color: var(--text-secondary); font-size: 13px; text-align: center; margin-top: 16px; }
.link a { color: var(--accent); }
</style>
