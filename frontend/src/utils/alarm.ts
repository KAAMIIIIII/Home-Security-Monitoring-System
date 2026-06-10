// 后端英文告警类型 → 前端中文展示
export function alarmTypeZh(t: string): string {
  const key = String(t || '')
  const map: Record<string, string> = {
    Fire: '火灾',
    Smoke: '烟雾',
    Intrusion: '闯入',
    WeaponMove: '刀具/撬棍危险移动'
  }
  return map[key] || key || '-'
}
