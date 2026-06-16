<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mockPosts } from '@/data/mockPosts'
import RichEditor from '@/components/ui/RichEditor.vue'
import type { Post, Image } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const posts = ref<Post[]>([])
const images = ref<Image[]>([])
const loading = ref(true)
const activeTab = ref<'posts' | 'images'>('posts')
const showEditor = ref(false)

// 编辑器状态
const editingPost = ref({
  title: '',
  content: '',
  tags: '',
  published: false,
  coverImage: null as Image | null,
})

const uploading = ref(false)
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    posts.value = [...mockPosts]
    images.value = mockPosts.flatMap(p => p.images)
  } finally {
    loading.value = false
  }
}

// 封面图上传
function selectCoverImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = () => {
    const file = input.files?.[0]
    if (!file) return
    const url = URL.createObjectURL(file)
    editingPost.value.coverImage = {
      id: 'cover-' + Date.now(),
      url,
      thumbnail: url,
      title: file.name,
      width: 800,
      height: 450,
      aspectRatio: 16 / 9,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
  }
  input.click()
}

function removeCoverImage() {
  editingPost.value.coverImage = null
}

function openEditor() {
  editingPost.value = {
    title: '',
    content: '',
    tags: '',
    published: false,
    coverImage: null,
  }
  showEditor.value = true
}

function closeEditor() {
  showEditor.value = false
}

function submitPost() {
  if (!editingPost.value.title) return

  const tags = editingPost.value.tags
    .split(/[,，、\s]+/)
    .map(t => t.trim())
    .filter(Boolean)

  const post: Post = {
    id: String(Date.now()),
    title: editingPost.value.title,
    content: editingPost.value.content,
    excerpt: editingPost.value.content.replace(/<[^>]+>/g, '').slice(0, 120),
    images: editingPost.value.coverImage ? [editingPost.value.coverImage] : [],
    tags,
    published: editingPost.value.published,
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0],
  }

  posts.value.unshift(post)
  showEditor.value = false
}

async function deletePost(id: string) {
  if (!confirm('确定要删除这篇文章吗？')) return
  posts.value = posts.value.filter(p => p.id !== id)
}

// 图片管理
async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  selectedFile.value = input.files[0]
}

async function uploadImage() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    const newImage: Image = {
      id: String(Date.now()),
      url: URL.createObjectURL(selectedFile.value!),
      thumbnail: URL.createObjectURL(selectedFile.value!),
      title: selectedFile.value!.name,
      width: 800, height: 600, aspectRatio: 800 / 600,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    images.value.unshift(newImage)
    selectedFile.value = null
  } finally {
    uploading.value = false
  }
}

async function deleteImage(id: string) {
  if (!confirm('确定要删除这张图片吗？')) return
  images.value = images.value.filter(img => img.id !== id)
}

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen py-12 px-6">
    <div class="max-w-4xl mx-auto">
      <!-- 头部 -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-foreground" style="font-family: var(--font-serif);">管理后台</h1>
          <p class="text-sm mt-1" style="color: #8C7E74;">管理你的博客内容</p>
        </div>
        <button class="btn-ghost text-sm" @click="logout">退出登录</button>
      </div>

      <!-- 标签页 -->
      <div class="glass rounded-xl p-1 flex gap-1 mb-8">
        <button
          :class="['flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300', activeTab === 'posts' ? 'neu-pressed text-primary' : '']"
          :style="activeTab !== 'posts' ? 'color: #8C7E74' : ''"
          @click="activeTab = 'posts'"
        >文章管理</button>
        <button
          :class="['flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300', activeTab === 'images' ? 'neu-pressed text-primary' : '']"
          :style="activeTab !== 'images' ? 'color: #8C7E74' : ''"
          @click="activeTab = 'images'"
        >图片管理</button>
      </div>

      <!-- 加载 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="h-20 bg-muted rounded-xl animate-pulse" />
      </div>

      <!-- ========== 文章管理 ========== -->
      <div v-else-if="activeTab === 'posts'" class="space-y-6">
        <!-- 新建按钮 / 编辑器 -->
        <div v-if="!showEditor">
          <button class="btn-primary" @click="openEditor">
            <span>+ 新建文章</span>
          </button>
        </div>

        <!-- 编辑器面板 -->
        <Transition name="editor">
          <div v-if="showEditor" class="glass-strong rounded-2xl p-6 space-y-5">
            <div class="flex items-center justify-between">
              <h2 class="text-base font-semibold text-foreground">新建文章</h2>
              <button class="text-sm" style="color: #8C7E74;" @click="closeEditor">取消</button>
            </div>

            <!-- 标题 -->
            <div>
              <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">文章标题</label>
              <input v-model="editingPost.title" type="text" placeholder="输入文章标题" class="input-neu" />
            </div>

            <!-- 封面图 -->
            <div>
              <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">封面图片</label>
              <div
                v-if="!editingPost.coverImage"
                class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 hover:border-primary/50 hover:bg-primary/3"
                style="border-color: var(--border);"
                @click="selectCoverImage"
              >
                <svg class="mx-auto mb-2" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: #BFB3A3;">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>
                </svg>
                <p class="text-sm" style="color: #8C7E74;">点击上传封面图片</p>
                <p class="text-xs mt-1" style="color: #BFB3A3;">推荐 16:9 比例，支持 JPG/PNG</p>
              </div>
              <div v-else class="relative rounded-xl overflow-hidden bg-muted">
                <img :src="editingPost.coverImage.url" class="w-full h-48 object-cover" />
                <div class="absolute top-2 right-2 flex gap-2">
                  <button
                    class="px-3 py-1.5 text-xs bg-white/90 text-foreground rounded-lg font-medium hover:bg-white transition-colors shadow-sm"
                    @click="selectCoverImage"
                  >更换</button>
                  <button
                    class="px-3 py-1.5 text-xs bg-white/90 rounded-lg font-medium hover:bg-white transition-colors shadow-sm"
                    style="color: #C4453E;"
                    @click="removeCoverImage"
                  >移除</button>
                </div>
              </div>
            </div>

            <!-- 标签 -->
            <div>
              <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">标签</label>
              <input v-model="editingPost.tags" type="text" placeholder="用逗号分隔，如：技术, Vue, 博客" class="input-neu" />
            </div>

            <!-- 富文本编辑器 -->
            <div>
              <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">文章内容</label>
              <RichEditor v-model="editingPost.content" />
            </div>

            <!-- 操作栏 -->
            <div class="flex items-center justify-between pt-2">
              <label class="flex items-center gap-2 text-sm cursor-pointer" style="color: #8C7E74;">
                <input v-model="editingPost.published" type="checkbox" class="w-4 h-4 rounded accent-primary" />
                <span>立即发布</span>
              </label>
              <div class="flex gap-3">
                <button class="btn-ghost text-sm" @click="closeEditor">取消</button>
                <button class="btn-primary" @click="submitPost"><span>发布文章</span></button>
              </div>
            </div>
          </div>
        </Transition>

        <!-- 文章列表 -->
        <div class="space-y-3">
          <div
            v-for="post in posts"
            :key="post.id"
            class="card-neu p-5 flex items-center justify-between"
          >
            <div class="min-w-0 flex-1 flex items-center gap-4">
              <!-- 缩略封面 -->
              <div v-if="post.images.length" class="w-16 h-12 rounded-lg overflow-hidden bg-muted shrink-0">
                <img :src="post.images[0].thumbnail" class="w-full h-full object-cover" />
              </div>
              <div class="min-w-0">
                <h3 class="font-medium text-foreground truncate" style="font-family: var(--font-serif);">{{ post.title }}</h3>
                <p class="text-xs mt-1" style="color: #8C7E74;">
                  {{ post.createdAt }} ·
                  <span :style="{ color: post.published ? '#8A9A86' : '#E07A5F' }">
                    {{ post.published ? '已发布' : '草稿' }}
                  </span>
                  <span v-if="post.tags.length"> · {{ post.tags.join(', ') }}</span>
                </p>
              </div>
            </div>
            <div class="flex gap-2 ml-4 shrink-0">
              <button class="btn-ghost px-3! py-1.5! text-xs" @click="router.push(`/post/${post.id}`)">查看</button>
              <button
                class="px-3 py-1.5 text-xs rounded-lg transition-colors duration-200"
                style="background: rgba(196, 69, 62, 0.08); color: #C4453E;"
                @click="deletePost(post.id)"
              >删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 图片管理 ========== -->
      <div v-else-if="activeTab === 'images'" class="space-y-6">
        <div class="glass-strong rounded-2xl p-6">
          <h2 class="text-base font-semibold mb-4 text-foreground">上传图片</h2>
          <div class="flex items-center gap-3">
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              @change="handleFileUpload"
              class="hidden"
            />
            <button
              class="btn-ghost text-sm flex items-center gap-2"
              @click="() => fileInputRef?.click()"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              选择文件
            </button>
            <span class="text-sm flex-1 truncate" :style="{ color: selectedFile ? '#2B221E' : '#BFB3A3' }">
              {{ selectedFile ? selectedFile.name : '未选择任何文件' }}
            </span>
            <button class="btn-primary disabled:opacity-40 disabled:cursor-not-allowed" :disabled="!selectedFile || uploading" @click="uploadImage">
              <span>{{ uploading ? '上传中...' : '上传' }}</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="image in images" :key="image.id" class="group relative aspect-square rounded-xl overflow-hidden card-neu">
            <img :src="image.thumbnail" :alt="image.title" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <button class="px-3 py-1.5 text-xs bg-white/90 text-foreground rounded-lg font-medium hover:bg-white transition-colors" @click="deleteImage(image.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-enter-active {
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.editor-leave-active {
  transition: all 0.25s ease;
}
.editor-enter-from,
.editor-leave-to {
  opacity: 0;
  transform: translateY(-12px);
  max-height: 0;
}
.editor-enter-to,
.editor-leave-from {
  max-height: 2000px;
}
</style>
