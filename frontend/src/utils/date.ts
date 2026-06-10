// 兼容解析 UTC 字符串或带时区的 ISO 字符串，缺少时区时默认当作 UTC
export function parseToBeijingDate(input: string | unknown): Date {
  const s = String(input || '')
  if (!s) return new Date(NaN)
  const hasTz = /Z$|[+\-]\d{2}:\d{2}$/.test(s)
  return new Date(hasTz ? s : `${s}Z`)
}

// 判断两个日期是否同一天
export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

// UTC 时间 → 本地时区 YYYY-MM-DD HH:mm:ss 字符串
export function fmt(s: string): string {
  const d = parseToBeijingDate(s)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(
    d.getMinutes()
  )}:${pad(d.getSeconds())}`
}
