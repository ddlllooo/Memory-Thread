<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as fabric from 'fabric'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)

let canvas: fabric.Canvas | null = null
let pageWidth = 794  // A4 宽度 (px at 96dpi)
let pageHeight = 1123 // A4 高度
const pagePadding = 60

// 当前选中的对象
const activeObject = ref<fabric.Object | null>(null)
const selectedType = ref<'text' | 'image' | null>(null)

// 文本格式状态
const isBold = ref(false)
const isItalic = ref(false)
const isUnderline = ref(false)
const textAlign = ref('left')
const fontSize = ref(16)
const fontFamily = ref('serif')

// 图片布局菜单
const showImageMenu = ref(false)
const imageMenuPos = ref({ top: 0, left: 0 })

onMounted(() => {
  initCanvas()
  loadContent(props.modelValue)
  // 监听键盘事件 - 使用捕获阶段确保能接收到
  document.addEventListener('keydown', onKeyDown, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeyDown, true)
  canvas?.dispose()
})

watch(() => props.modelValue, (val) => {
  if (canvas && val !== getHTML()) {
    loadContent(val)
  }
})

function initCanvas() {
  if (!canvasRef.value || !containerRef.value) return

  canvas = new fabric.Canvas(canvasRef.value, {
    width: pageWidth,
    height: pageHeight,
    backgroundColor: '#ffffff',
    selection: true,
    preserveObjectStacking: true,
  })

  // 绘制页面边框和阴影
  drawPageBackground()

  // 监听选择事件
  canvas.on('selection:created', onSelectionCreated)
  canvas.on('selection:updated', onSelectionUpdated)
  canvas.on('selection:cleared', onSelectionCleared)
  canvas.on('object:modified', onObjectModified)
  canvas.on('text:changed', onTextChanged)

  // 监听鼠标点击用于图片菜单
  canvas.on('mouse:down', onMouseDown)

  // 在 upper-canvas 上监听键盘事件（Fabric.js 的事件目标）
  const wrapperEl = canvas.wrapperEl
  if (wrapperEl) {
    wrapperEl.setAttribute('tabindex', '0')
    wrapperEl.style.outline = 'none'
    wrapperEl.addEventListener('keydown', onKeyDown)
  }
}

function drawPageBackground() {
  // 页面阴影通过 CSS 实现
}

function onSelectionCreated(e: any) {
  updateSelectionState(e.selected?.[0])
}

function onSelectionUpdated(e: any) {
  updateSelectionState(e.selected?.[0])
}

function onSelectionCleared() {
  activeObject.value = null
  selectedType.value = null
  showImageMenu.value = false
}

function updateSelectionState(obj: fabric.Object | undefined) {
  if (!obj) return
  activeObject.value = obj

  if (obj instanceof fabric.IText || obj instanceof fabric.Textbox) {
    selectedType.value = 'text'
    updateTextFormatState(obj)
  } else if (obj instanceof fabric.Image) {
    selectedType.value = 'image'
  }
}

function updateTextFormatState(textObj: fabric.IText | fabric.Textbox) {
  // 获取当前选中文本的样式
  const styles = textObj.getSelectionStyles()
  if (styles.length > 0) {
    isBold.value = styles[0].fontWeight === 'bold'
    isItalic.value = styles[0].fontStyle === 'italic'
    isUnderline.value = styles[0].underline === true
    fontSize.value = styles[0].fontSize || 16
    fontFamily.value = styles[0].fontFamily || 'serif'
  }
  textAlign.value = textObj.textAlign || 'left'
}

function onObjectModified() {
  emitContent()
}

function onTextChanged() {
  emitContent()
}

function onMouseDown(e: any) {
  if (!canvas || !canvasRef.value || !containerRef.value) return
  const target = e.target
  if (target instanceof fabric.Image) {
    // 确保图片被选中
    canvas.setActiveObject(target)
    activeObject.value = target
    selectedType.value = 'image'

    // 聚焦到 canvas wrapper 以便接收键盘事件
    canvas.wrapperEl.focus()

    // 获取图片边界（相对于 canvas 坐标）
    const bound = target.getBoundingRect()

    // canvas 在 container 中的位置
    const canvasEl = canvasRef.value
    const canvasLeft = canvasEl.offsetLeft
    const canvasTop = canvasEl.offsetTop

    const menuWidth = 200

    // 菜单紧贴图片上方居中
    imageMenuPos.value = {
      top: canvasTop + bound.top - 45,
      left: canvasLeft + bound.left + bound.width / 2 - menuWidth / 2,
    }
    showImageMenu.value = true
  } else {
    showImageMenu.value = false
  }
}

// 加载 HTML 内容
function loadContent(html: string) {
  if (!canvas) return

  // 清空画布（保留背景）
  canvas.getObjects().forEach((obj) => {
    if (!(obj as any).excludeFromExport) {
      canvas!.remove(obj)
    }
  })

  if (!html || html.trim() === '') {
    // 添加默认文本框
    addTextbox('', pagePadding, pagePadding, pageWidth - pagePadding * 2)
    return
  }

  // 解析 HTML 并添加到画布
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  let currentY = pagePadding

  Array.from(tempDiv.childNodes).forEach((node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent?.trim()
      if (text) {
        const textbox = addTextbox(text, pagePadding, currentY, pageWidth - pagePadding * 2)
        currentY += textbox.height! + 10
      }
    } else if (node instanceof HTMLElement) {
      const tagName = node.tagName.toLowerCase()
      if (tagName === 'img') {
        const src = node.getAttribute('src')
        if (src) {
          addImageFromURL(src, currentY)
          currentY += 300 // 估算图片高度
        }
      } else if (tagName === 'p' || tagName.startsWith('h')) {
        const text = node.textContent?.trim() || ''
        const options: Partial<fabric.TextboxProps> = {}

        if (tagName === 'h1') {
          options.fontSize = 32
          options.fontWeight = 'bold'
        } else if (tagName === 'h2') {
          options.fontSize = 24
          options.fontWeight = 'bold'
        } else if (tagName === 'h3') {
          options.fontSize = 20
          options.fontWeight = 'bold'
        }

        const textbox = addTextbox(text, pagePadding, currentY, pageWidth - pagePadding * 2, options)
        currentY += textbox.height! + 10
      } else if (tagName === 'blockquote') {
        const text = node.textContent?.trim() || ''
        const textbox = addTextbox(text, pagePadding + 20, currentY, pageWidth - pagePadding * 2 - 20, {
          fontStyle: 'italic',
          fill: '#8C7E74',
        })
        // 添加引用线
        const line = new fabric.Line([pagePadding + 5, currentY, pagePadding + 5, currentY + textbox.height!], {
          stroke: '#E07A5F',
          strokeWidth: 3,
          selectable: false,
        })
        canvas!.add(line)
        currentY += textbox.height! + 10
      }
    }
  })

  canvas.renderAll()
}

// 添加文本框
function addTextbox(
  text: string,
  left: number,
  top: number,
  width: number,
  options?: Partial<fabric.TextboxProps>
): fabric.Textbox {
  const textbox = new fabric.Textbox(text, {
    left,
    top,
    width,
    fontSize: 16,
    fontFamily: 'serif',
    lineHeight: 1.6,
    fill: '#2B221E',
    editable: true,
    splitByGrapheme: true,
    ...options,
  })

  canvas!.add(textbox)
  return textbox
}

// 从 URL 添加图片
function addImageFromURL(url: string, top: number) {
  const imgEl = new Image()
  imgEl.crossOrigin = 'anonymous'
  imgEl.onload = () => {
    const fabricImage = new fabric.Image(imgEl, {
      left: pagePadding,
      top,
      scaleX: 0.5,
      scaleY: 0.5,
      cornerStyle: 'circle',
      cornerColor: '#E07A5F',
      cornerStrokeColor: '#E07A5F',
      borderColor: '#E07A5F',
      transparentCorners: false,
      cornerSize: 10,
      padding: 5,
    })

    // 限制图片在页面内
    const maxWidth = pageWidth - pagePadding * 2
    if (fabricImage.width! * fabricImage.scaleX! > maxWidth) {
      fabricImage.scaleX = maxWidth / fabricImage.width!
      fabricImage.scaleY = fabricImage.scaleX
    }

    canvas!.add(fabricImage)
    canvas!.setActiveObject(fabricImage)
    canvas!.renderAll()
    emitContent()
  }
  imgEl.src = url
}

// 获取 HTML 内容
function getHTML(): string {
  if (!canvas) return ''

  let html = ''
  const objects = canvas.getObjects().filter((obj) => !(obj as any).excludeFromExport)

  objects.forEach((obj) => {
    if (obj instanceof fabric.Textbox) {
      const text = obj.text || ''
      const fontSize = obj.fontSize || 16
      const fontWeight = obj.fontWeight || 'normal'
      const fontStyle = obj.fontStyle || 'normal'

      let tag = 'p'
      let style = ''

      if (fontSize >= 30 && fontWeight === 'bold') {
        tag = 'h1'
      } else if (fontSize >= 22 && fontWeight === 'bold') {
        tag = 'h2'
      } else if (fontSize >= 18 && fontWeight === 'bold') {
        tag = 'h3'
      }

      if (fontStyle === 'italic') {
        style += 'font-style:italic;'
      }
      if (obj.fill === '#8C7E74') {
        style += 'color:#8C7E74;'
      }

      const styleAttr = style ? ` style="${style}"` : ''
      html += `<${tag}${styleAttr}>${text}</${tag}>\n`
    } else if (obj instanceof fabric.Image) {
      const src = (obj as any)._element?.src || ''
      html += `<img src="${src}" style="max-width:100%;" />\n`
    }
  })

  return html
}

function emitContent() {
  emit('update:modelValue', getHTML())
}

// 工具栏操作
function toggleBold() {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const textObj = activeObject.value as fabric.Textbox
  const newWeight = isBold.value ? 'normal' : 'bold'

  if (textObj.selectionStart !== textObj.selectionEnd) {
    // 有选中文本
    for (let i = textObj.selectionStart!; i < textObj.selectionEnd!; i++) {
      textObj.setSelectionStyles({ fontWeight: newWeight }, i, i + 1)
    }
  } else {
    // 无选中文本，设置当前样式
    textObj.set('fontWeight', newWeight)
  }
  isBold.value = !isBold.value
  canvas?.renderAll()
  emitContent()
}

function toggleItalic() {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const textObj = activeObject.value as fabric.Textbox
  const newStyle = isItalic.value ? 'normal' : 'italic'

  if (textObj.selectionStart !== textObj.selectionEnd) {
    for (let i = textObj.selectionStart!; i < textObj.selectionEnd!; i++) {
      textObj.setSelectionStyles({ fontStyle: newStyle }, i, i + 1)
    }
  } else {
    textObj.set('fontStyle', newStyle)
  }
  isItalic.value = !isItalic.value
  canvas?.renderAll()
  emitContent()
}

function toggleUnderline() {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const textObj = activeObject.value as fabric.Textbox

  if (textObj.selectionStart !== textObj.selectionEnd) {
    for (let i = textObj.selectionStart!; i < textObj.selectionEnd!; i++) {
      textObj.setSelectionStyles({ underline: !isUnderline.value }, i, i + 1)
    }
  } else {
    textObj.set('underline', !isUnderline.value)
  }
  isUnderline.value = !isUnderline.value
  canvas?.renderAll()
  emitContent()
}

function setTextAlign(align: string) {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  (activeObject.value as fabric.Textbox).set('textAlign', align)
  textAlign.value = align
  canvas?.renderAll()
  emitContent()
}

function setFontSize(size: number) {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const textObj = activeObject.value as fabric.Textbox

  if (textObj.selectionStart !== textObj.selectionEnd) {
    for (let i = textObj.selectionStart!; i < textObj.selectionEnd!; i++) {
      textObj.setSelectionStyles({ fontSize: size }, i, i + 1)
    }
  } else {
    textObj.set('fontSize', size)
  }
  fontSize.value = size
  canvas?.renderAll()
  emitContent()
}

function setHeading(level: number) {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const sizes: Record<number, number> = { 1: 32, 2: 24, 3: 20 }
  const textObj = activeObject.value as fabric.Textbox
  textObj.set({
    fontSize: sizes[level] || 16,
    fontWeight: 'bold',
  })
  fontSize.value = sizes[level] || 16
  isBold.value = true
  canvas?.renderAll()
  emitContent()
}

function setParagraph() {
  if (!activeObject.value || !(activeObject.value instanceof fabric.Textbox)) return
  const textObj = activeObject.value as fabric.Textbox
  textObj.set({
    fontSize: 16,
    fontWeight: 'normal',
  })
  fontSize.value = 16
  isBold.value = false
  canvas?.renderAll()
  emitContent()
}

// 插入图片
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
      // 找到当前文本框的底部位置
      let maxY = pagePadding
      canvas?.getObjects().forEach((obj) => {
        if (!(obj as any).excludeFromExport) {
          const bottom = obj.top! + (obj.height || 0) * (obj.scaleY || 1)
          if (bottom > maxY) maxY = bottom
        }
      })
      addImageFromURL(url, maxY + 10)
    }
    reader.readAsDataURL(file)
  }
  input.click()
}

// 插入图片链接
const showImageUrlDialog = ref(false)
const imageUrlInput = ref('')

function insertImageUrl() {
  imageUrlInput.value = ''
  showImageUrlDialog.value = true
}

function confirmInsertImageUrl() {
  if (imageUrlInput.value.trim()) {
    let maxY = pagePadding
    canvas?.getObjects().forEach((obj) => {
      if (!(obj as any).excludeFromExport) {
        const bottom = obj.top! + (obj.height || 0) * (obj.scaleY || 1)
        if (bottom > maxY) maxY = bottom
      }
    })
    addImageFromURL(imageUrlInput.value.trim(), maxY + 10)
  }
  showImageUrlDialog.value = false
  imageUrlInput.value = ''
}

// 移除选中对象
function removeSelected() {
  if (!canvas) return

  // 获取要移除的对象
  let targetObj: any = activeObject.value

  if (!targetObj) {
    targetObj = canvas.getActiveObject() ?? null
  }

  if (!targetObj) return

  // 使用 canvas.remove 移除对象
  canvas.remove(targetObj)

  canvas.discardActiveObject()
  activeObject.value = null
  selectedType.value = null
  showImageMenu.value = false
  canvas.renderAll()
  emitContent()
}

// 键盘事件处理
function onKeyDown(e: KeyboardEvent) {
  // 检查是否在编辑状态（Fabric.js 文本编辑中）
  if (canvas) {
    const activeObj = canvas.getActiveObject()
    if (activeObj instanceof fabric.IText && activeObj.isEditing) {
      return // 正在编辑文本时不处理
    }
  }

  // Delete 或 Backspace 键移除选中对象
  if (e.key === 'Delete' || e.key === 'Backspace') {
    const hasActive = canvas && (canvas.getActiveObjects().length > 0 || activeObject.value)
    if (hasActive) {
      e.preventDefault()
      removeSelected()
    }
  }
}

// 设置图片环绕方式
function setImageWrap(_type: 'inline' | 'square' | 'top-bottom') {
  // Fabric.js 中图片默认就是自由浮动的
  // 这里可以添加视觉提示或其他逻辑
  showImageMenu.value = false
}

// 添加新段落
function addParagraph() {
  if (!canvas) return
  let maxY = pagePadding
  canvas.getObjects().forEach((obj) => {
    if (!(obj as any).excludeFromExport) {
      const bottom = obj.top! + (obj.height || 0) * (obj.scaleY || 1)
      if (bottom > maxY) maxY = bottom
    }
  })
  const textbox = addTextbox('', pagePadding, maxY + 10, pageWidth - pagePadding * 2)
  canvas.setActiveObject(textbox)
  textbox.enterEditing()
  canvas.renderAll()
}
</script>

<template>
  <div class="canvas-editor">
    <!-- 工具栏 -->
    <div class="toolbar flex flex-wrap items-center gap-0.5 px-3 py-2 border-b" style="border-color: var(--border); background: rgba(255,255,255,0.4);">
      <!-- 标题 -->
      <button class="toolbar-btn text-xs px-2" @click="setHeading(1)" title="标题 1">H1</button>
      <button class="toolbar-btn text-xs px-2" @click="setHeading(2)" title="标题 2">H2</button>
      <button class="toolbar-btn text-xs px-2" @click="setHeading(3)" title="标题 3">H3</button>
      <button class="toolbar-btn text-xs px-2" @click="setParagraph" title="正文">正文</button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 字体大小 -->
      <select
        class="toolbar-select text-xs"
        :value="fontSize"
        @change="setFontSize(Number(($event.target as HTMLSelectElement).value))"
      >
        <option v-for="s in [12, 14, 16, 18, 20, 24, 28, 32, 36, 48]" :key="s" :value="s">{{ s }}</option>
      </select>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 加粗/斜体/下划线 -->
      <button :class="['toolbar-btn', isBold && 'toolbar-btn-active']" @click="toggleBold" title="加粗">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>
      </button>
      <button :class="['toolbar-btn', isItalic && 'toolbar-btn-active']" @click="toggleItalic" title="斜体">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
      </button>
      <button :class="['toolbar-btn', isUnderline && 'toolbar-btn-active']" @click="toggleUnderline" title="下划线">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4v6a6 6 0 0 0 12 0V4"/><line x1="4" y1="20" x2="20" y2="20"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 对齐 -->
      <button :class="['toolbar-btn', textAlign === 'left' && 'toolbar-btn-active']" @click="setTextAlign('left')" title="左对齐">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>
      </button>
      <button :class="['toolbar-btn', textAlign === 'center' && 'toolbar-btn-active']" @click="setTextAlign('center')" title="居中">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      </button>
      <button :class="['toolbar-btn', textAlign === 'right' && 'toolbar-btn-active']" @click="setTextAlign('right')" title="右对齐">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg>
      </button>

      <div class="w-px h-5 mx-1" style="background: var(--border);" />

      <!-- 插入图片 -->
      <button class="toolbar-btn" @click="insertImage" title="上传本地图片">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
      </button>
      <button class="toolbar-btn" @click="insertImageUrl" title="输入图片链接">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
      </button>
      <button class="toolbar-btn" @click="addParagraph" title="添加段落">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </button>
    </div>

    <!-- Canvas 容器 -->
    <div ref="containerRef" class="canvas-container overflow-auto" style="background: #f0f0f0; padding: 20px;" tabindex="0">
      <canvas ref="canvasRef" />

      <!-- 图片操作浮动菜单 -->
      <Transition name="menu">
        <div
          v-if="showImageMenu"
          class="image-menu absolute z-30 flex items-center gap-1 px-2 py-1.5 rounded-lg shadow-lg"
          :style="{ top: imageMenuPos.top + 'px', left: imageMenuPos.left + 'px', background: 'var(--card)', border: '1px solid var(--border)' }"
        >
          <button class="toolbar-btn text-xs" @click="setImageWrap('inline')" title="嵌入型">嵌入</button>
          <button class="toolbar-btn text-xs" @click="setImageWrap('square')" title="四周型">四周</button>
          <button class="toolbar-btn text-xs" @click="setImageWrap('top-bottom')" title="上下型">上下</button>
          <div class="w-px h-5 mx-0.5" style="background: var(--border);" />
          <button class="toolbar-btn hover:text-red-500" @click="removeSelected" title="移除">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          </button>
        </div>
      </Transition>
    </div>

    <!-- 图片链接对话框 -->
    <Transition name="menu">
      <div v-if="showImageUrlDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div class="bg-white rounded-xl p-6 shadow-xl w-96">
          <h3 class="text-lg font-semibold mb-4">插入图片链接</h3>
          <input
            v-model="imageUrlInput"
            class="w-full px-3 py-2 border rounded-lg mb-4"
            placeholder="请输入图片 URL"
            @keydown.enter="confirmInsertImageUrl"
          />
          <div class="flex justify-end gap-2">
            <button class="px-4 py-2 rounded-lg border" @click="showImageUrlDialog = false">取消</button>
            <button class="px-4 py-2 rounded-lg bg-[#E07A5F] text-white" @click="confirmInsertImageUrl">确认</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.canvas-editor {
  border-radius: 12px;
  overflow: hidden;
  background: var(--neu-bg);
  box-shadow: inset 3px 3px 6px 0 var(--neu-shadow-dark), inset -3px -3px 6px 0 var(--neu-shadow-light);
}

.canvas-container {
  max-height: 600px;
  display: flex;
  justify-content: center;
  position: relative;
}

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

.toolbar-select {
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--foreground);
  cursor: pointer;
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

/* Fabric.js 画布样式 */
:deep(.canvas-container canvas) {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style>
