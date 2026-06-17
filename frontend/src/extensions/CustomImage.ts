import Image from '@tiptap/extension-image'

export const CustomImage = Image.extend({
  name: 'customImage',

  addAttributes() {
    return {
      ...this.parent?.(),
      'data-layout': {
        default: 'inline',
        parseHTML: (element) => element.getAttribute('data-layout') || 'inline',
        renderHTML: (attributes) => {
          if (attributes['data-layout']) {
            return { 'data-layout': attributes['data-layout'] }
          }
          return {}
        },
      },
      width: {
        default: null,
        parseHTML: (element) => element.getAttribute('width') || element.style.width || null,
        renderHTML: (attributes) => {
          if (attributes.width) {
            return { width: attributes.width }
          }
          return {}
        },
      },
      height: {
        default: null,
        parseHTML: (element) => element.getAttribute('height') || element.style.height || null,
        renderHTML: (attributes) => {
          if (attributes.height) {
            return { height: attributes.height }
          }
          return {}
        },
      },
      // 使用 ProseMirror attrs 存储位置
      'data-x': {
        default: null,
        parseHTML: (element) => {
          const x = element.getAttribute('data-x')
          return x ? parseInt(x) : null
        },
        renderHTML: (attributes) => {
          if (attributes['data-x'] !== null && attributes['data-x'] !== undefined) {
            return { 'data-x': attributes['data-x'].toString() }
          }
          return {}
        },
      },
      'data-y': {
        default: null,
        parseHTML: (element) => {
          const y = element.getAttribute('data-y')
          return y ? parseInt(y) : null
        },
        renderHTML: (attributes) => {
          if (attributes['data-y'] !== null && attributes['data-y'] !== undefined) {
            return { 'data-y': attributes['data-y'].toString() }
          }
          return {}
        },
      },
    }
  },

  // 使用 NodeView 来完全控制渲染
  addNodeView() {
    return ({ node }) => {
      const dom = document.createElement('div')
      dom.style.position = 'relative'
      dom.style.display = 'inline-block'

      const img = document.createElement('img')
      img.src = node.attrs.src
      img.style.maxWidth = '100%'
      img.style.height = 'auto'
      img.style.borderRadius = '8px'
      img.style.cursor = 'move'

      // 从 attrs 恢复位置
      const layout = node.attrs['data-layout']
      const x = node.attrs['data-x']
      const y = node.attrs['data-y']

      if (layout === 'absolute' && x !== null && y !== null) {
        dom.style.position = 'absolute'
        dom.style.left = `${x}px`
        dom.style.top = `${y}px`
        dom.style.zIndex = '10'
      } else if (layout === 'square' || layout === 'through') {
        img.style.float = 'left'
        img.style.margin = '0 1em 1em 0'
      } else if (layout === 'top-bottom') {
        img.style.display = 'block'
        img.style.margin = '1em auto'
      }

      if (node.attrs.width) {
        img.style.width = node.attrs.width
      }
      if (node.attrs.height) {
        img.style.height = node.attrs.height
      }

      dom.appendChild(img)

      return {
        dom,
        img,
        update(updatedNode) {
          if (updatedNode.type.name !== 'customImage') return false

          img.src = updatedNode.attrs.src

          // 从 attrs 恢复位置
          const layout = updatedNode.attrs['data-layout']
          const x = updatedNode.attrs['data-x']
          const y = updatedNode.attrs['data-y']

          if (layout === 'absolute' && x !== null && y !== null) {
            dom.style.position = 'absolute'
            dom.style.left = `${x}px`
            dom.style.top = `${y}px`
          }

          if (updatedNode.attrs.width) {
            img.style.width = updatedNode.attrs.width
          }
          if (updatedNode.attrs.height) {
            img.style.height = updatedNode.attrs.height
          }

          return true
        },
      }
    }
  },
})
