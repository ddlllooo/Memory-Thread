<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import { CustomImage } from '@/extensions/CustomImage'
import Placeholder from '@tiptap/extension-placeholder'
import Highlight from '@tiptap/extension-highlight'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const showColorPicker = ref(false)
const showHeadingMenu = ref(false)

// 图片 URL 对话框
const showImageDialog = ref(false)
const imageUrlInput = ref('')

// 图片操作状态
const selectedImage = ref<{ pos: number; node: any; el: HTMLElement } | null>(null)
const showImageMenu = ref(false)
const imageMenuPos = ref({ top: 0, left: 0 })
const imageOverlay = ref<{ top: number; left: number; width: number; height: number } | null>(null)

// 拖拽状态
const isDragging = ref(false)
const dragHandle = ref<string | null>(null)
const dragStart = ref({ x: 0, y: 0, width: 0, height: 0 })

// 图片拖拽移动状态
const isMoving = ref(false)
const moveStart = ref({ x: 0, y: 0, left: 0, top: 0 })

// 图片布局类型
type ImageLayout = 'inline' | 'square' | 'top-bottom' | 'through' | 'absolute'
const currentLayout = ref<ImageLayout>('inline')

const presetColors = [
  '#2B221E', '#8C7E74', '#E07A5F', '#8A9A86',
  '#C4453E', '#D4A574', '#5B7B6A', '#6B7FA0',
]

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
    }),
    Underline,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    TextStyle,
    Color,
    CustomImage.configure({
      inline: true,
      allowBase64: true,
    }),
    Placeholder.configure({
      placeholder: '开始写文章内容...',
    }),
    Highlight.configure({
      multicolor: true,
    }),
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  editorProps: {
    attributes: {
      class: 'prose-editor focus:outline-none min-h-[300px] px-4 py-3',
    },
  },
})

watch(() => props.modelValue, (val) => {
  if (editor.value && val !== editor.value.getHTML()) {
    editor.value.commands.setContent(val, { emitUpdate: false })
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

function toggleBold() { editor.value?.chain().focus().toggleBold().run() }
function toggleItalic() { editor.value?.chain().focus().toggleItalic().run() }
function toggleUnderline() { editor.value?.chain().focus().toggleUnderline().run() }
function toggleStrike() { editor.value?.chain().focus().toggleStrike().run() }
function toggleHighlight() { editor.value?.chain().focus().toggleHighlight({ color: '#fef3c7' }).run() }
function setAlign(align: 'left' | 'center' | 'right' | 'justify') {
  editor.value?.chain().focus().setTextAlign(align).run()
}
function toggleBulletList() { editor.value?.chain().focus().toggleBulletList().run() }
function toggleOrderedList() { editor.value?.chain().focus().toggleOrderedList().run() }
function toggleBlockquote() { editor.value?.chain().focus().toggleBlockquote().run() }
function setHorizontalRule() { editor.value?.chain().focus().setHorizontalRule().run() }
function undo() { editor.value?.chain().focus().undo().run() }
function redo() { editor.value?.chain().focus().redo().run() }

function setHeading(level: 1 | 2 | 3) {
  editor.value?.chain().focus().toggleHeading({ level }).run()
  showHeadingMenu.value = false
}

function setParagraph() {
  editor.value?.chain().focus().setParagraph().run()
  showHeadingMenu.value = false
}

function setColor(color: string) {
  editor.value?.chain().focus().setColor(color).run()
  showColorPicker.value = false
}

function resetColor() {
  editor.value?.chain().focus().unsetColor().run()
  showColorPicker.value = false
}

function insertImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = () => {
    const file = input.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => {
      const url = e.target?.result as string
      editor.value?.chain().focus().setImage({ src: url }).run()
    }
    reader.readAsDataURL(file)
  }
  input.click()
}

function insertImageUrl() {
  imageUrlInput.value = ''
  showImageDialog.value = true
}

function confirmInsertImage() {
  if (imageUrlInput.value.trim()) {
    editor.value?.chain().focus().setImage({ src: imageUrlInput.value.trim() }).run()
  }
  showImageDialog.value = false
  imageUrlInput.value = ''
}

function isActive(name: string, attrs?: Record<string, any>) {
  return editor.value?.isActive(name, attrs) ?? false
}

// 图片操作
function handleEditorClick(event: MouseEvent) {
  const target = event.target as HTMLElement

  // 检查点击的是否是图片或图片菜单
  const isImageClick = target.tagName === 'IMG'
  const isNodeViewClick = target.closest('.custom-image-node')
  const isOverlayClick = target.closest('.image-resize-overlay')
  const isMenuClick = target.closest('.image-menu')
  const isToolbarClick = target.closest('.toolbar-btn')

  if ((isImageClick || isNodeViewClick) && editor.value) {
    const imgEl = isImageClick ? target : (isNodeViewClick as HTMLElement).querySelector('img') || target
    const pos = editor.value.view.posAtDOM(imgEl, 0)
    const node = editor.value.view.state.doc.nodeAt(pos)
    if (node && node.type.name === 'customImage') {
      selectedImage.value = { pos, node, el: imgEl }
      currentLayout.value = (node.attrs['data-layout'] as ImageLayout) || 'inline'
      const rect = imgEl.getBoundingClientRect()
      const editorRect = (event.currentTarget as HTMLElement).getBoundingClientRect()
      // 显示选中框
      imageOverlay.value = {
        top: rect.top - editorRect.top - 2,
        left: rect.left - editorRect.left - 2,
        width: rect.width + 4,
        height: rect.height + 4,
      }
      // 显示操作菜单
      imageMenuPos.value = {
        top: rect.top - editorRect.top - 44,
        left: rect.left - editorRect.left + rect.width / 2 - 120,
      }
      showImageMenu.value = true
    }
  } else if (!isOverlayClick && !isMenuClick && !isToolbarClick) {
    showImageMenu.value = false
    selectedImage.value = null
    imageOverlay.value = null
  }
}

function setImageAlign(align: string) {
  if (!selectedImage.value || !editor.value) return
  const { pos, node } = selectedImage.value
  const display = align === 'center' ? 'block' : 'inline-block'
  const margin = align === 'center' ? '0 auto' : align === 'right' ? '0 0 0 auto' : '0'

  const { view } = editor.value
  const attrs = { ...node.attrs, style: `display:${display};margin:${margin};` }
  const tr = view.state.tr.setNodeMarkup(pos, undefined, attrs)
  view.dispatch(tr)
  showImageMenu.value = false
}

function deleteImage() {
  if (!selectedImage.value || !editor.value) return
  const { pos, node } = selectedImage.value
  const { view } = editor.value
  const tr = view.state.tr.delete(pos, pos + node.nodeSize)
  view.dispatch(tr)
  showImageMenu.value = false
  selectedImage.value = null
  imageOverlay.value = null
}

// 设置图片布局
function setImageLayout(layout: ImageLayout) {
  if (!selectedImage.value || !editor.value) return
  const { pos, node } = selectedImage.value

  // 清除位置数据（如果不是绝对定位）
  const attrs: Record<string, any> = {
    ...node.attrs,
    'data-layout': layout,
  }

  if (layout !== 'absolute') {
    // 切换到非绝对定位布局时，清除位置数据
    attrs['data-x'] = null
    attrs['data-y'] = null
  }

  // 直接通过 view.dispatch 更新节点
  const { view } = editor.value
  const tr = view.state.tr.setNodeMarkup(pos, undefined, attrs)
  view.dispatch(tr)

  // 重新获取节点引用
  const newNode = view.state.doc.nodeAt(pos)
  if (newNode) {
    selectedImage.value = { ...selectedImage.value, node: newNode }
  }

  currentLayout.value = layout

  // 更新选中框位置
  setTimeout(() => {
    updateOverlay()
  }, 50)
}

// 获取当前图片布局
// 更新选中框位置
function updateOverlay() {
  if (!selectedImage.value) return
  const { el } = selectedImage.value
  const editorEl = el.closest('.tiptap')?.parentElement
  if (!editorEl) return
  const editorRect = editorEl.getBoundingClientRect()
  const imgRect = el.getBoundingClientRect()
  imageOverlay.value = {
    top: imgRect.top - editorRect.top - 2,
    left: imgRect.left - editorRect.left - 2,
    width: imgRect.width + 4,
    height: imgRect.height + 4,
  }
  imageMenuPos.value = {
    top: imgRect.top - editorRect.top - 44,
    left: imgRect.left - editorRect.left + imgRect.width / 2 - 120,
  }
}

// 拖拽移动图片
function startMove(event: MouseEvent) {
  if (!selectedImage.value) return
  // 忽略拖拽手柄的点击
  if ((event.target as HTMLElement).closest('.resize-handle')) return
  event.preventDefault()
  event.stopPropagation()
  isMoving.value = true

  const { node, el } = selectedImage.value
  const imgEl = el.tagName === 'IMG' ? el : el.querySelector('img') || el
  const parentEl = el.closest('.tiptap') || el.parentElement
  if (!parentEl) return

  const parentRect = parentEl.getBoundingClientRect()
  const imgRect = imgEl.getBoundingClientRect()

  // 从 attrs 获取当前位置，或使用 DOM 位置
  const currentX = node.attrs['data-x'] !== null ? node.attrs['data-x'] : imgRect.left - parentRect.left
  const currentY = node.attrs['data-y'] !== null ? node.attrs['data-y'] : imgRect.top - parentRect.top

  moveStart.value = {
    x: event.clientX,
    y: event.clientY,
    left: currentX,
    top: currentY,
  }

  document.addEventListener('mousemove', onMove, { passive: false })
  document.addEventListener('mouseup', stopMove)
}

function onMove(event: MouseEvent) {
  if (!isMoving.value || !selectedImage.value || !editor.value) return
  event.preventDefault()

  const dx = event.clientX - moveStart.value.x
  const dy = event.clientY - moveStart.value.y
  const newX = moveStart.value.left + dx
  const newY = moveStart.value.top + dy

  // 直接更新节点属性（ProseMirror 方式）
  const { pos, node } = selectedImage.value
  const { view } = editor.value

  const attrs = {
    ...node.attrs,
    'data-x': newX,
    'data-y': newY,
    'data-layout': 'absolute',
  }
  const tr = view.state.tr.setNodeMarkup(pos, undefined, attrs)
  view.dispatch(tr)

  // 重新获取节点引用（因为 dispatch 后节点已更新）
  const newNode = view.state.doc.nodeAt(pos)
  if (newNode) {
    selectedImage.value = { ...selectedImage.value, node: newNode }
  }

  updateOverlay()
}

function stopMove() {
  if (!isMoving.value || !editor.value) return
  isMoving.value = false
  document.removeEventListener('mousemove', onMove)
  document.removeEventListener('mouseup', stopMove)

  // 最终位置已经在 onMove 中通过 transaction 保存
  updateOverlay()
}

// 拖拽调整大小
function startResize(handle: string, event: MouseEvent) {
  if (!selectedImage.value) return
  event.preventDefault()
  isDragging.value = true
  dragHandle.value = handle
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: selectedImage.value.el.offsetWidth,
    height: selectedImage.value.el.offsetHeight,
  }
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}

function onResize(event: MouseEvent) {
  if (!isDragging.value || !selectedImage.value || !imageOverlay.value) return
  const dx = event.clientX - dragStart.value.x
  const dy = event.clientY - dragStart.value.y
  let newWidth = dragStart.value.width
  let newHeight = dragStart.value.height

  const aspectRatio = dragStart.value.width / dragStart.value.height

  switch (dragHandle.value) {
    case 'se':
      newWidth = Math.max(80, dragStart.value.width + dx)
      newHeight = newWidth / aspectRatio
      break
    case 'sw':
      newWidth = Math.max(80, dragStart.value.width - dx)
      newHeight = newWidth / aspectRatio
      break
    case 'ne':
      newWidth = Math.max(80, dragStart.value.width + dx)
      newHeight = newWidth / aspectRatio
      break
    case 'nw':
      newWidth = Math.max(80, dragStart.value.width - dx)
      newHeight = newWidth / aspectRatio
      break
    case 'n':
      newHeight = Math.max(60, dragStart.value.height - dy)
      newWidth = newHeight * aspectRatio
      break
    case 's':
      newHeight = Math.max(60, dragStart.value.height + dy)
      newWidth = newHeight * aspectRatio
      break
    case 'e':
      newWidth = Math.max(80, dragStart.value.width + dx)
      newHeight = newWidth / aspectRatio
      break
    case 'w':
      newWidth = Math.max(80, dragStart.value.width - dx)
      newHeight = newWidth / aspectRatio
      break
  }

  // 直接设置图片尺寸
  selectedImage.value.el.style.width = `${newWidth}px`
  selectedImage.value.el.style.height = `${newHeight}px`

  // 更新选中框
  updateOverlay()
}

function stopResize() {
  if (!isDragging.value || !selectedImage.value || !editor.value) return
  isDragging.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)

  // 更新节点属性
  const { pos, node, el } = selectedImage.value
  const width = `${el.offsetWidth}px`
  const height = `${el.offsetHeight}px`

  const { view } = editor.value
  const attrs = { ...node.attrs, width, height }
  const tr = view.state.tr.setNodeMarkup(pos, undefined, attrs)
  view.dispatch(tr)

  // 更新选中框
  updateOverlay()
  dragHandle.value = null
}

function isAlignActive(align: string) {
  return editor.value?.isActive({ textAlign: align }) ?? false
}

// 关闭下拉菜单
function closeMenus(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.heading-menu-wrap')) showHeadingMenu.value = false
  if (!target.closest('.color-menu-wrap')) showColorPicker.value = false
}

if (typeof window !== 'undefined') {
  document.addEventListener('click', closeMenus)
}
</script>

<template>
  <div class="rich-editor rounded-xl" style="background: var(--neu-bg); box-shadow: inset 3px 3px 6px 0 var(--neu-shadow-dark), inset -3px -3px 6px 0 var(--neu-shadow-light); overflow: visible;">
    <!-- 工具栏 -->
    <div
      v-if="editor"
      class="flex flex-wrap items-center gap-0.5 px-3 py-2 border-b"
      style="border-color: var(--border); background: rgba(255,255,255,0.4);"
    >
      <!-- 撤销/重做 -->
      <button class="toolbar-btn" @click="undo" title="撤销">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
      </button>
      <button class="toolbar-btn" @click="redo" title="重做">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 标题选择 -->
      <div class="heading-menu-wrap relative">
        <button
          class="toolbar-btn text-xs px-2 min-w-[60px]"
          @click.stop="showHeadingMenu = !showHeadingMenu"
        >
          {{ isActive('heading', { level: 1 }) ? 'H1' : isActive('heading', { level: 2 }) ? 'H2' : isActive('heading', { level: 3 }) ? 'H3' : '正文' }}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ml-1"><path d="m6 9 6 6 6-6"/></svg>
        </button>
        <Transition name="menu">
          <div
            v-if="showHeadingMenu"
            class="absolute top-full left-0 mt-1 py-1 rounded-lg shadow-lg z-20 min-w-[100px]"
            style="background: var(--card); border: 1px solid var(--border);"
          >
            <button class="menu-item" @click="setParagraph">正文</button>
            <button class="menu-item" @click="setHeading(1)">标题 1</button>
            <button class="menu-item" @click="setHeading(2)">标题 2</button>
            <button class="menu-item" @click="setHeading(3)">标题 3</button>
          </div>
        </Transition>
      </div>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 加粗/斜体/下划线/删除线/高亮 -->
      <button :class="['toolbar-btn', isActive('bold') && 'toolbar-btn-active']" @click="toggleBold" title="加粗">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>
      </button>
      <button :class="['toolbar-btn', isActive('italic') && 'toolbar-btn-active']" @click="toggleItalic" title="斜体">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
      </button>
      <button :class="['toolbar-btn', isActive('underline') && 'toolbar-btn-active']" @click="toggleUnderline" title="下划线">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4v6a6 6 0 0 0 12 0V4"/><line x1="4" y1="20" x2="20" y2="20"/></svg>
      </button>
      <button :class="['toolbar-btn', isActive('strike') && 'toolbar-btn-active']" @click="toggleStrike" title="删除线">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4H9a3 3 0 0 0-3 3v0a3 3 0 0 0 3 3h6a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3H8"/><line x1="4" y1="12" x2="20" y2="12"/></svg>
      </button>
      <button :class="['toolbar-btn', isActive('highlight') && 'toolbar-btn-active']" @click="toggleHighlight" title="高亮">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 11-6 6v3h9l3-3"/><path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 文字颜色 -->
      <div class="color-menu-wrap relative">
        <button
          class="toolbar-btn"
          @click.stop="showColorPicker = !showColorPicker"
          title="文字颜色"
        >
          <span class="text-xs font-bold" style="border-bottom: 2px solid currentColor; padding-bottom: 1px;">A</span>
        </button>
        <Transition name="menu">
          <div
            v-if="showColorPicker"
            class="absolute top-full left-0 mt-1 p-3 rounded-lg shadow-lg z-20"
            style="background: var(--card); border: 1px solid var(--border);"
          >
            <div class="grid grid-cols-4 gap-2 mb-2">
              <button
                v-for="color in presetColors"
                :key="color"
                class="w-6 h-6 rounded-full border-2 border-transparent hover:scale-110 transition-transform"
                :style="{ background: color }"
                @click="setColor(color)"
              />
            </div>
            <button class="text-xs w-full text-center py-1 hover:opacity-70" style="color: var(--muted-foreground);" @click="resetColor">
              重置颜色
            </button>
          </div>
        </Transition>
      </div>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 对齐 -->
      <button :class="['toolbar-btn', isAlignActive('left') && 'toolbar-btn-active']" @click="setAlign('left')" title="左对齐">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>
      </button>
      <button :class="['toolbar-btn', isAlignActive('center') && 'toolbar-btn-active']" @click="setAlign('center')" title="居中">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      </button>
      <button :class="['toolbar-btn', isAlignActive('right') && 'toolbar-btn-active']" @click="setAlign('right')" title="右对齐">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg>
      </button>
      <button :class="['toolbar-btn', isAlignActive('justify') && 'toolbar-btn-active']" @click="setAlign('justify')" title="两端对齐">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 列表 -->
      <button :class="['toolbar-btn', isActive('bulletList') && 'toolbar-btn-active']" @click="toggleBulletList" title="无序列表">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="20" y2="12"/><line x1="9" y1="18" x2="20" y2="18"/><circle cx="4" cy="6" r="1" fill="currentColor"/><circle cx="4" cy="12" r="1" fill="currentColor"/><circle cx="4" cy="18" r="1" fill="currentColor"/></svg>
      </button>
      <button :class="['toolbar-btn', isActive('orderedList') && 'toolbar-btn-active']" @click="toggleOrderedList" title="有序列表">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><text x="3" y="8" font-size="7" fill="currentColor" stroke="none">1</text><text x="3" y="14" font-size="7" fill="currentColor" stroke="none">2</text><text x="3" y="20" font-size="7" fill="currentColor" stroke="none">3</text></svg>
      </button>
      <button :class="['toolbar-btn', isActive('blockquote') && 'toolbar-btn-active']" @click="toggleBlockquote" title="引用">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/></svg>
      </button>
      <button class="toolbar-btn" @click="setHorizontalRule" title="分割线">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 插入图片 -->
      <button class="toolbar-btn" @click="insertImage" title="上传本地图片">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
      </button>
      <button class="toolbar-btn" @click="insertImageUrl" title="输入图片链接">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
      </button>
    </div>

    <!-- 编辑区域 -->
    <div class="relative min-h-[300px]" @click="handleEditorClick" style="overflow: visible;">
      <EditorContent :editor="editor" />

      <!-- 图片选中框和拖拽手柄 -->
      <div
        v-if="imageOverlay"
        class="image-resize-overlay absolute pointer-events-none"
        :style="{
          top: imageOverlay.top + 'px',
          left: imageOverlay.left + 'px',
          width: imageOverlay.width + 'px',
          height: imageOverlay.height + 'px',
          border: '2px solid #E07A5F',
          borderRadius: '10px',
          zIndex: 25,
        }"
        @mousedown.stop="startMove"
      >
        <!-- 四角拖拽手柄 -->
        <div
          class="resize-handle absolute w-3 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-nw-resize"
          style="top: -6px; left: -6px;"
          @mousedown.stop="startResize('nw', $event)"
        />
        <div
          class="resize-handle absolute w-3 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-ne-resize"
          style="top: -6px; right: -6px;"
          @mousedown.stop="startResize('ne', $event)"
        />
        <div
          class="resize-handle absolute w-3 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-sw-resize"
          style="bottom: -6px; left: -6px;"
          @mousedown.stop="startResize('sw', $event)"
        />
        <div
          class="resize-handle absolute w-3 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-se-resize"
          style="bottom: -6px; right: -6px;"
          @mousedown.stop="startResize('se', $event)"
        />

        <!-- 四边拖拽手柄 -->
        <div
          class="resize-handle absolute w-3 h-2 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-n-resize"
          style="top: -5px; left: 50%; transform: translateX(-50%);"
          @mousedown.stop="startResize('n', $event)"
        />
        <div
          class="resize-handle absolute w-3 h-2 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-s-resize"
          style="bottom: -5px; left: 50%; transform: translateX(-50%);"
          @mousedown.stop="startResize('s', $event)"
        />
        <div
          class="resize-handle absolute w-2 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-e-resize"
          style="top: 50%; right: -5px; transform: translateY(-50%);"
          @mousedown.stop="startResize('e', $event)"
        />
        <div
          class="resize-handle absolute w-2 h-3 bg-white border-2 border-[#E07A5F] rounded-full pointer-events-auto cursor-w-resize"
          style="top: 50%; left: -5px; transform: translateY(-50%);"
          @mousedown.stop="startResize('w', $event)"
        />
      </div>

      <!-- 图片操作浮动菜单 -->
      <Transition name="menu">
        <div
          v-if="showImageMenu"
          class="image-menu absolute z-30 flex flex-col gap-1.5 px-3 py-2 rounded-lg shadow-lg"
          :style="{ top: imageMenuPos.top + 'px', left: imageMenuPos.left + 'px', background: 'var(--card)', border: '1px solid var(--border)', minWidth: '240px' }"
          @click.stop
        >
          <!-- 布局选项 -->
          <div class="flex items-center gap-1">
            <span class="text-xs mr-1" style="color: var(--muted-foreground);">布局:</span>
            <button
              :class="['toolbar-btn text-xs px-1.5 h-7', currentLayout === 'inline' && 'toolbar-btn-active']"
              @click="setImageLayout('inline')"
              title="嵌入型"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="12" x2="21" y2="12"/></svg>
            </button>
            <button
              :class="['toolbar-btn text-xs px-1.5 h-7', currentLayout === 'square' && 'toolbar-btn-active']"
              @click="setImageLayout('square')"
              title="四周型环绕"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="10" height="10" rx="1"/><line x1="16" y1="5" x2="21" y2="5"/><line x1="16" y1="9" x2="21" y2="9"/><line x1="5" y1="16" x2="19" y2="16"/><line x1="5" y1="20" x2="19" y2="20"/></svg>
            </button>
            <button
              :class="['toolbar-btn text-xs px-1.5 h-7', currentLayout === 'top-bottom' && 'toolbar-btn-active']"
              @click="setImageLayout('top-bottom')"
              title="上下型环绕"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="3" x2="19" y2="3"/><line x1="5" y1="7" x2="19" y2="7"/><rect x="7" y="10" width="10" height="6" rx="1"/><line x1="5" y1="20" x2="19" y2="20"/></svg>
            </button>
            <button
              :class="['toolbar-btn text-xs px-1.5 h-7', currentLayout === 'through' && 'toolbar-btn-active']"
              @click="setImageLayout('through')"
              title="穿越型环绕"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 5h4l2 4H3"/><path d="M3 13h4l2 4H3"/><rect x="11" y="3" width="10" height="8" rx="1"/><path d="M3 5h4l2 4H3"/><path d="M3 13h8l2 4H3"/><line x1="14" y1="15" x2="21" y2="15"/><line x1="14" y1="19" x2="21" y2="19"/></svg>
            </button>
          </div>

          <div class="h-px" style="background: var(--border);" />

          <!-- 对齐和删除 -->
          <div class="flex items-center gap-1">
            <span class="text-xs mr-1" style="color: var(--muted-foreground);">操作:</span>
            <button class="toolbar-btn" @click="setImageAlign('left')" title="左对齐">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>
            </button>
            <button class="toolbar-btn" @click="setImageAlign('center')" title="居中">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
            </button>
            <button class="toolbar-btn" @click="setImageAlign('right')" title="右对齐">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg>
            </button>

            <div class="w-px h-5 mx-0.5" style="background: var(--border);" />

            <button class="toolbar-btn hover:text-red-500" @click="deleteImage" title="删除图片">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>

  <!-- 图片 URL 对话框 -->
  <Dialog v-model:open="showImageDialog">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>插入图片链接</DialogTitle>
      </DialogHeader>
      <div class="py-4">
        <Input
          v-model="imageUrlInput"
          placeholder="请输入图片 URL"
          @keydown.enter="confirmInsertImage"
        />
      </div>
      <DialogFooter>
        <Button variant="outline" @click="showImageDialog = false">取消</Button>
        <Button @click="confirmInsertImage">确认插入</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: var(--foreground);
  opacity: 0.7;
  transition: all 0.2s ease;
  cursor: pointer;
  background: transparent;
  border: none;
  flex-shrink: 0;
}

.toolbar-btn:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.05);
}

.toolbar-btn-active {
  opacity: 1;
  background: rgba(224, 122, 95, 0.1);
  color: #E07A5F;
}

.menu-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 6px 12px;
  font-size: 0.8rem;
  color: var(--foreground);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}

.menu-item:hover {
  background: var(--secondary);
}

.menu-enter-active {
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.menu-leave-active {
  transition: all 0.15s ease;
}
.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 编辑器内容样式 */
:deep(.tiptap) {
  min-height: 300px;
  padding: 1rem;
  outline: none;
  font-family: var(--font-sans);
  font-size: 0.9375rem;
  line-height: 1.8;
  color: var(--foreground);
  position: relative;
}

:deep(.tiptap p) {
  margin-bottom: 0.75em;
}

:deep(.tiptap h1) {
  font-family: var(--font-serif);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 1.5em 0 0.5em;
}

:deep(.tiptap h2) {
  font-family: var(--font-serif);
  font-size: 1.375rem;
  font-weight: 600;
  margin: 1.25em 0 0.5em;
}

:deep(.tiptap h3) {
  font-family: var(--font-serif);
  font-size: 1.125rem;
  font-weight: 600;
  margin: 1em 0 0.5em;
}

:deep(.tiptap ul) {
  list-style-type: disc;
  padding-left: 1.5em;
  margin-bottom: 0.75em;
}

:deep(.tiptap ol) {
  list-style-type: decimal;
  padding-left: 1.5em;
  margin-bottom: 0.75em;
}

:deep(.tiptap li) {
  margin-bottom: 0.25em;
}

:deep(.tiptap blockquote) {
  border-left: 3px solid #E07A5F;
  padding-left: 1em;
  margin: 1em 0;
  color: #8C7E74;
  font-style: italic;
}

:deep(.tiptap hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5em 0;
}

:deep(.tiptap img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em 0;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

:deep(.tiptap img:hover) {
  box-shadow: 0 0 0 2px rgba(224, 122, 95, 0.3);
}

/* 四周型环绕 */
:deep(.tiptap img[data-layout="square"]) {
  float: left;
  margin: 0 1em 1em 0;
  shape-outside: margin-box;
}

/* 上下型环绕 */
:deep(.tiptap img[data-layout="top-bottom"]) {
  display: block;
  margin: 1em auto;
  float: none;
  clear: both;
}

/* 穿越型环绕 */
:deep(.tiptap img[data-layout="through"]) {
  float: left;
  margin: 0 1em 1em 0;
  shape-outside: margin-box;
}

/* 绝对定位（自由拖拽后） */
:deep(.tiptap div[data-layout="absolute"]) {
  position: absolute;
  z-index: 10;
}

/* 清除浮动 */
:deep(.tiptap::after) {
  content: '';
  display: table;
  clear: both;
}

:deep(.tiptap mark) {
  border-radius: 2px;
  padding: 0 2px;
}

:deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #BFB3A3;
  pointer-events: none;
  height: 0;
}
</style>
