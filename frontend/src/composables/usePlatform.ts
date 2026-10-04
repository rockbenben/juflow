export const PLATFORM_COLORS: Record<string, string> = {
  csdn: '#e17055',
  xueqiu: '#00b894',
  zhihu: '#5a52e0',
}

export function platformColor(platform: string): string {
  return PLATFORM_COLORS[platform] || '#fdcb6e'
}

function relLum(hex: string): number {
  const h = hex.replace('#', '')
  const [r, g, b] = [0, 2, 4]
    .map(i => parseInt(h.slice(i, i + 2), 16) / 255)
    .map(v => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

// White vs near-black: pick whichever passes 4.5:1 (or is closer) on the badge color.
export function onColor(bg: string): string {
  const l = relLum(bg)
  const white = 1.05 / (l + 0.05)
  const dark = (l + 0.05) / 0.0584
  return white >= dark ? '#ffffff' : '#1a1a2e'
}

export const INTERVAL_OPTIONS = [
  { value: 60, key: 'm1' },
  { value: 120, key: 'm2' },
  { value: 300, key: 'm5' },
  { value: 600, key: 'm10' },
  { value: 900, key: 'm15' },
  { value: 1800, key: 'm30' },
  { value: 3600, key: 'h1' },
  { value: 21600, key: 'h6' },
  { value: 86400, key: 'd1' },
] as const
