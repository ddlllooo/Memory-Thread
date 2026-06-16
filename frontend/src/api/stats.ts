import client from './client'

export interface DailyVisit {
  date: string
  count: number
}

export interface VisitorStats {
  total_visits: number
  today_visits: number
  total_posts: number
  published_posts: number
  total_images: number
  running_days: number
  daily_visits: DailyVisit[]
  years: number[]
}

export const statsApi = {
  /** 记录一次页面访问 */
  recordVisit(): Promise<void> {
    return client.post('/stats/visit').then(res => res.data)
  },

  /** 获取站点统计数据 */
  getStats(year?: number): Promise<VisitorStats> {
    return client.get('/stats', { params: year ? { year } : {} }).then(res => res.data)
  },
}
