/**
 * 格式化日期为中文格式
 */
export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('zh-CN')
}

/**
 * 去除 HTML 标签并截断文本
 */
export function stripHtml(html: string, maxLength: number = 150): string {
  const text = html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}
