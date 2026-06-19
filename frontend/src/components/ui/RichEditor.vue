<script setup lang="ts">
import { watch, onBeforeUnmount, ref } from "vue";
import { imagesApi } from "@/api/images";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import Image from "@tiptap/extension-image";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";

const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const updatingFromProps = ref(false);

// 提示消息
const toastMessage = ref("");
const toastType = ref<"success" | "error">("success");
const showToast = ref(false);
let toastTimer: ReturnType<typeof setTimeout> | null = null;

function displayToast(message: string, type: "success" | "error" = "error") {
  toastMessage.value = message;
  toastType.value = type;
  showToast.value = true;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    showToast.value = false;
  }, 3000);
}

const editor = useEditor({
  content: props.modelValue || "",
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
    }),
    Placeholder.configure({
      placeholder: "开始撰写文章内容...",
    }),
    Image.configure({
      inline: false,
    }),
    Underline,
    TextAlign.configure({
      types: ["heading", "paragraph"],
    }),
  ],
  editorProps: {
    attributes: {
      class: "editor-content",
    },
  },
  onUpdate: ({ editor }) => {
    if (!updatingFromProps.value) {
      emit("update:modelValue", editor.getHTML());
    }
  },
});

watch(
  () => props.modelValue,
  (val) => {
    if (!editor.value) return;
    const current = editor.value.getHTML();
    // 跳过相同内容或空值场景
    if (val === current) return;
    if (!val && current === "<p></p>") return;
    updatingFromProps.value = true;
    editor.value.commands.setContent(val || "", { emitUpdate: false });
    updatingFromProps.value = false;
  },
);

onBeforeUnmount(() => {
  editor.value?.destroy();
});

function toggleBold() {
  editor.value?.chain().focus().toggleBold().run();
}
function toggleItalic() {
  editor.value?.chain().focus().toggleItalic().run();
}
function toggleUnderline() {
  editor.value?.chain().focus().toggleUnderline().run();
}
function toggleStrike() {
  editor.value?.chain().focus().toggleStrike().run();
}
function toggleCode() {
  editor.value?.chain().focus().toggleCode().run();
}
function setHeading(level: 1 | 2 | 3 | 4 | 5 | 6) {
  editor.value?.chain().focus().toggleHeading({ level }).run();
}
function setParagraph() {
  editor.value?.chain().focus().setParagraph().run();
}
function toggleBulletList() {
  editor.value?.chain().focus().toggleBulletList().run();
}
function toggleOrderedList() {
  editor.value?.chain().focus().toggleOrderedList().run();
}
function toggleBlockquote() {
  editor.value?.chain().focus().toggleBlockquote().run();
}
function toggleCodeBlock() {
  editor.value?.chain().focus().toggleCodeBlock().run();
}
function setHorizontalRule() {
  editor.value?.chain().focus().setHorizontalRule().run();
}
function setTextAlign(align: "left" | "center" | "right") {
  editor.value?.chain().focus().setTextAlign(align).run();
}

function insertImage() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = async () => {
    const file = input.files?.[0];
    if (!file) return;
    try {
      const result = await imagesApi.uploadImage(file);
      editor.value?.chain().focus().setImage({ src: result.url }).run();
    } catch {
      displayToast("图片上传失败");
    }
  };
  input.click();
}

function insertImageUrl() {
  const url = prompt("请输入图片链接:");
  if (url?.trim()) {
    editor.value?.chain().focus().setImage({ src: url.trim() }).run();
  }
}

function isActive(name: string, attrs?: Record<string, any>) {
  return editor.value?.isActive(name, attrs) ?? false;
}
</script>

<template>
  <div class="rich-editor">
    <!-- 工具栏 -->
    <div class="toolbar" v-if="editor">
      <div class="toolbar-group">
        <button
          :class="['tb', isActive('heading', { level: 1 }) && 'tb-active']"
          @click="setHeading(1)"
          title="标题 1"
        >
          H1
        </button>
        <button
          :class="['tb', isActive('heading', { level: 2 }) && 'tb-active']"
          @click="setHeading(2)"
          title="标题 2"
        >
          H2
        </button>
        <button
          :class="['tb', isActive('heading', { level: 3 }) && 'tb-active']"
          @click="setHeading(3)"
          title="标题 3"
        >
          H3
        </button>
        <button
          :class="[
            'tb',
            !isActive('heading') && isActive('paragraph') && 'tb-active',
          ]"
          @click="setParagraph"
          title="正文"
        >
          P
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          :class="['tb', isActive('bold') && 'tb-active']"
          @click="toggleBold"
          title="加粗 (Ctrl+B)"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
            <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
          </svg>
        </button>
        <button
          :class="['tb', isActive('italic') && 'tb-active']"
          @click="toggleItalic"
          title="斜体 (Ctrl+I)"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="19" y1="4" x2="10" y2="4" />
            <line x1="14" y1="20" x2="5" y2="20" />
            <line x1="15" y1="4" x2="9" y2="20" />
          </svg>
        </button>
        <button
          :class="['tb', isActive('underline') && 'tb-active']"
          @click="toggleUnderline"
          title="下划线 (Ctrl+U)"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M6 4v6a6 6 0 0 0 12 0V4" />
            <line x1="4" y1="20" x2="20" y2="20" />
          </svg>
        </button>
        <button
          :class="['tb', isActive('strike') && 'tb-active']"
          @click="toggleStrike"
          title="删除线"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M16 4H9a3 3 0 0 0 0 6h6a3 3 0 0 1 0 6H8" />
            <line x1="4" y1="12" x2="20" y2="12" />
          </svg>
        </button>
        <button
          :class="['tb', isActive('code') && 'tb-active']"
          @click="toggleCode"
          title="行内代码"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="16 18 22 12 16 6" />
            <polyline points="8 6 2 12 8 18" />
          </svg>
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          :class="['tb', isActive('bulletList') && 'tb-active']"
          @click="toggleBulletList"
          title="无序列表"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <circle cx="4" cy="6" r="1" fill="currentColor" />
            <circle cx="4" cy="12" r="1" fill="currentColor" />
            <circle cx="4" cy="18" r="1" fill="currentColor" />
          </svg>
        </button>
        <button
          :class="['tb', isActive('orderedList') && 'tb-active']"
          @click="toggleOrderedList"
          title="有序列表"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="10" y1="6" x2="21" y2="6" />
            <line x1="10" y1="12" x2="21" y2="12" />
            <line x1="10" y1="18" x2="21" y2="18" />
            <text x="4" y="8" font-size="7" fill="currentColor" stroke="none">
              1
            </text>
            <text x="4" y="14" font-size="7" fill="currentColor" stroke="none">
              2
            </text>
            <text x="4" y="20" font-size="7" fill="currentColor" stroke="none">
              3
            </text>
          </svg>
        </button>
        <button
          :class="['tb', isActive('blockquote') && 'tb-active']"
          @click="toggleBlockquote"
          title="引用"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"
            />
            <path
              d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"
            />
          </svg>
        </button>
        <button
          :class="['tb', isActive('codeBlock') && 'tb-active']"
          @click="toggleCodeBlock"
          title="代码块"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="m10 8-3 4 3 4" />
            <path d="m14 8 3 4-3 4" />
          </svg>
        </button>
        <button class="tb" @click="setHorizontalRule" title="分割线">
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="12" x2="21" y2="12" />
          </svg>
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          :class="[
            'tb',
            isActive('textAlign', { textAlign: 'left' }) && 'tb-active',
          ]"
          @click="setTextAlign('left')"
          title="左对齐"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="15" y2="12" />
            <line x1="3" y1="18" x2="18" y2="18" />
          </svg>
        </button>
        <button
          :class="[
            'tb',
            isActive('textAlign', { textAlign: 'center' }) && 'tb-active',
          ]"
          @click="setTextAlign('center')"
          title="居中"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="6" y1="12" x2="18" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </svg>
        </button>
        <button
          :class="[
            'tb',
            isActive('textAlign', { textAlign: 'right' }) && 'tb-active',
          ]"
          @click="setTextAlign('right')"
          title="右对齐"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="9" y1="12" x2="21" y2="12" />
            <line x1="6" y1="18" x2="21" y2="18" />
          </svg>
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button class="tb" @click="insertImage" title="上传本地图片">
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <path d="m21 15-5-5L5 21" />
          </svg>
        </button>
        <button class="tb" @click="insertImageUrl" title="输入图片链接">
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"
            />
            <path
              d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 编辑区域 -->
    <EditorContent :editor="editor" class="editor-wrap" />

    <!-- 提示弹窗 -->
    <Transition name="toast">
      <div v-if="showToast" class="toast-overlay">
        <div
          class="toast-box"
          :style="{
            background: toastType === 'success' ? '#8A9A86' : '#C4453E',
          }"
        >
          {{ toastMessage }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.rich-editor {
  border-radius: 12px;
  overflow: hidden;
  background: var(--neu-bg);
  box-shadow:
    inset 3px 3px 6px 0 var(--neu-shadow-dark),
    inset -3px -3px 6px 0 var(--neu-shadow-light);
  border: 1px solid var(--border);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.4);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  margin: 0 6px;
  background: var(--border);
}

.tb {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 30px;
  height: 30px;
  padding: 0 6px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--foreground);
  opacity: 0.6;
  transition: all 0.15s ease;
  cursor: pointer;
  background: transparent;
  border: none;
}

.tb:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.06);
}

.tb-active {
  opacity: 1;
  background: rgba(224, 122, 95, 0.12);
  color: #e07a5f;
}

.editor-wrap {
  min-height: 200px;
  max-height: 70vh;
  overflow-y: auto;
}

/* Tiptap 编辑器内容样式 */
:deep(.tiptap) {
  padding: 16px 20px;
  min-height: 200px;
  outline: none;
  font-size: 15px;
  line-height: 1.8;
  color: var(--foreground);
}

:deep(.tiptap p) {
  margin: 0.5em 0;
}

:deep(.tiptap h1) {
  font-size: 1.8em;
  font-weight: 700;
  margin: 0.8em 0 0.4em;
  line-height: 1.3;
}

:deep(.tiptap h2) {
  font-size: 1.4em;
  font-weight: 700;
  margin: 0.7em 0 0.35em;
  line-height: 1.3;
}

:deep(.tiptap h3) {
  font-size: 1.15em;
  font-weight: 700;
  margin: 0.6em 0 0.3em;
  line-height: 1.4;
}

:deep(.tiptap ul),
:deep(.tiptap ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

:deep(.tiptap li) {
  margin: 0.2em 0;
}

:deep(.tiptap blockquote) {
  border-left: 3px solid #e07a5f;
  padding-left: 1em;
  margin: 0.8em 0;
  color: #8c7e74;
  font-style: italic;
}

:deep(.tiptap pre) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: "Courier New", monospace;
  font-size: 13px;
  overflow-x: auto;
  margin: 0.8em 0;
}

:deep(.tiptap code) {
  background: rgba(0, 0, 0, 0.06);
  border-radius: 4px;
  padding: 2px 5px;
  font-family: "Courier New", monospace;
  font-size: 0.9em;
}

:deep(.tiptap pre code) {
  background: none;
  padding: 0;
}

:deep(.tiptap hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.2em 0;
}

:deep(.tiptap img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 0.8em 0;
}

:deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #bfb3a3;
  pointer-events: none;
  height: 0;
}

.toast-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  pointer-events: none;
}

.toast-box {
  color: #fff;
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  pointer-events: auto;
}

.toast-enter-active {
  transition: all 0.3s ease-out;
}
.toast-leave-active {
  transition: all 0.25s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
