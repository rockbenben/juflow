import { createI18n } from 'vue-i18n'
import { watch } from 'vue'
import zhCN from './zh-CN.json'
import en from './en.json'

const initial = localStorage.getItem('locale') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: initial,
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': zhCN, en },
})

document.documentElement.lang = initial
watch(i18n.global.locale, (l: string) => { document.documentElement.lang = l })

export default i18n
