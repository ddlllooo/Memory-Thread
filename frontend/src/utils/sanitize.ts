import DOMPurify from 'dompurify'

/**
 * 消毒 HTML 内容，防止 XSS 攻击
 */
export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'ul', 'ol', 'li',
      'blockquote', 'pre', 'code',
      'a', 'img', 'video', 'source',
      'strong', 'em', 'u', 's', 'mark', 'sub', 'sup',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span', 'figure', 'figcaption',
      'details', 'summary',
    ],
    ALLOWED_ATTR: [
      'href', 'target', 'rel',
      'src', 'alt', 'width', 'height',
      'class', 'id',
      'title', 'colspan', 'rowspan',
    ],
    ALLOW_DATA_ATTR: false,
  })
}
