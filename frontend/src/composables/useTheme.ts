import { ref, watchEffect } from 'vue'

type Theme = 'dark' | 'light' | 'system'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'dark')

function getSystemTheme(): 'dark' | 'light' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(t: Theme) {
  const resolved = t === 'system' ? getSystemTheme() : t
  document.documentElement.setAttribute('data-theme', resolved)
}

watchEffect(() => {
  applyTheme(theme.value)
  localStorage.setItem('theme', theme.value)
})

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (theme.value === 'system') applyTheme('system')
})

export function useTheme() {
  function setTheme(t: Theme) { theme.value = t }
  return { theme, setTheme }
}
