import { useI18n } from 'vue-i18n'

// Backend error details that used to be shown verbatim in the UI. The API is
// language-neutral, the UI is not, so these are translated before they reach
// the screen.
const BACKEND_MESSAGES: Record<string, string> = {
  'Admin only': 'error.adminOnly',
  'Email or username already exists': 'error.emailTaken',
  'Invalid credentials': 'error.badCredentials',
  'Invalid authentication': 'error.unauthenticated',
  'Subscription not found': 'error.subscriptionMissing',
  'Group not found': 'error.groupMissing',
  'Tag not found': 'error.tagMissing',
  'Plugin not found': 'error.pluginMissing',
  'Cookie not found': 'error.cookieMissing',
}

// Messages that carry a variable part, so they are matched by prefix.
const BACKEND_PATTERNS: Array<[RegExp, string]> = [
  [/^Already subscribed/, 'error.alreadySubscribed'],
  [/^Cannot parse/, 'error.cannotParseUrl'],
  [/^File too large/, 'error.fileTooLarge'],
  [/manifest\.json/, 'error.pluginManifest'],
  [/^Invalid plugin name/, 'error.pluginName'],
  [/^Zip contains path traversal/, 'error.pluginUnsafe'],
]

// A detail that already contains Chinese is localized by the backend.
const HAS_CJK = /[一-鿿]/

export function useApiError() {
  const { t } = useI18n()

  /** Turn an axios error into a message the current locale can display. */
  function describe(err: any): string {
    const detail = err?.response?.data?.detail

    if (typeof detail === 'string') {
      const key = BACKEND_MESSAGES[detail]
      if (key) return t(key)
      const pattern = BACKEND_PATTERNS.find(([re]) => re.test(detail))
      if (pattern) return t(pattern[1])
      // Chinese details from the backend are shown as they are; anything else
      // is an untranslated server message and must not leak into the UI.
      if (HAS_CJK.test(detail)) return detail
      return t('error.requestFailed')
    }

    if (Array.isArray(detail)) {
      const parts = detail.map((d: any) => {
        const field = Array.isArray(d?.loc) ? d.loc[d.loc.length - 1] : ''
        const msg = String(d?.msg || '')
        if (field === 'password') {
          const n = /at least (\d+)/.exec(msg)?.[1]
          return n ? t('error.passwordTooShort', { n: Number(n) }) : t('error.invalidPassword')
        }
        if (field === 'email') return t('error.invalidEmail')
        if (field === 'username') return t('error.invalidUsername')
        return HAS_CJK.test(msg) ? msg : t('error.invalidField')
      })
      return parts.join('；')
    }

    return t('error.requestFailed')
  }

  return { describe }
}
