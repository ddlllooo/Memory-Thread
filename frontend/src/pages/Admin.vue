<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { postsApi } from '@/api/posts'
import { imagesApi } from '@/api/images'
import CanvasEditor from '@/components/ui/CanvasEditor.vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

interface Post {
  id: string
  title: string
  content: string
  summary: string
  cover_image: string | null
  tags: string[]
  published: boolean
  created_at: string
  updated_at: string
}

const router = useRouter()
const authStore = useAuthStore()

const posts = ref<Post[]>([])
const loading = ref(true)
const showEditor = ref(false)
const editingPostId = ref<string | null>(null)
const saving = ref(false)
const deletingId = ref<string | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)

// 删除确认对话框
const showDeleteConfirm = ref(false)
const deleteTargetId = ref<string | null>(null)
const deleteTargetTitle = ref('')

// 提示消息
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')
const showToast = ref(false)

// 编辑器状态
const editingPost = ref({
  title: '',
  content: '',
  tags: '',
  published: false,
  cover_image: '',
})

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await loadPosts()
})

function displayToast(message: string, type: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

async function loadPosts() {
  loading.value = true
  try {
    const response = await postsApi.getPosts(currentPage.value, 20)
    posts.value = response.data
    totalPages.value = response.total_pages
  } catch (error) {
    console.error('加载文章失败:', error)
    displayToast('加载文章列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// 封面图上传
function selectCoverImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    try {
      const result = await imagesApi.uploadImage(file)
      editingPost.value.cover_image = result.url
    } catch (error) {
      displayToast('封面图上传失败', 'error')
    }
  }
  input.click()
}

function removeCoverImage() {
  editingPost.value.cover_image = ''
}

function openEditor(post?: Post) {
  if (post) {
    editingPostId.value = post.id
    editingPost.value = {
      title: post.title,
      content: post.content,
      tags: post.tags.join(', '),
      published: post.published,
      cover_image: post.cover_image || '',
    }
  } else {
    editingPostId.value = null
    editingPost.value = {
      title: '',
      content: '',
      tags: '',
      published: false,
      cover_image: '',
    }
  }
  showEditor.value = true
}

function closeEditor() {
  showEditor.value = false
  editingPostId.value = null
}

async function submitPost(publish: boolean = false) {
  if (!editingPost.value.title) {
    displayToast('请输入文章标题', 'error')
    return
  }

  const tags = editingPost.value.tags
    .split(/[,，、\s]+/)
    .map(t => t.trim())
    .filter(Boolean)

  const postData = {
    title: editingPost.value.title,
    content: editingPost.value.content,
    summary: editingPost.value.content.replace(/<[^>]+>/g, '').slice(0, 200),
    cover_image: editingPost.value.cover_image || undefined,
    tags,
    published: publish,
  }

  saving.value = true
  try {
    if (editingPostId.value) {
      await postsApi.updatePost(editingPostId.value, postData)
      displayToast(publish ? '文章已发布' : '草稿已保存')
    } else {
      await postsApi.createPost(postData)
      displayToast(publish ? '文章已发布' : '草稿已保存')
    }
    showEditor.value = false
    editingPostId.value = null
    await loadPosts()
  } catch (error) {
    displayToast('保存失败，请重试', 'error')
  } finally {
    saving.value = false
  }
}

async function togglePublish(post: Post) {
  try {
    await postsApi.updatePost(post.id, { published: !post.published })
    displayToast(post.published ? '已取消发布' : '文章已发布')
    await loadPosts()
  } catch (error) {
    displayToast('操作失败，请重试', 'error')
  }
}

function confirmDelete(post: Post) {
  deleteTargetId.value = post.id
  deleteTargetTitle.value = post.title
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  deleteTargetId.value = null
  deleteTargetTitle.value = ''
}

async function handleDelete() {
  if (!deleteTargetId.value) return

  deletingId.value = deleteTargetId.value
  showDeleteConfirm.value = false

  try {
    await postsApi.deletePost(deleteTargetId.value)
    displayToast('文章已删除')
    await loadPosts()
  } catch (error) {
    displayToast('删除失败，请重试', 'error')
  } finally {
    deletingId.value = null
    deleteTargetId.value = null
    deleteTargetTitle.value = ''
  }
}

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen py-12 px-6">
    <div class="max-w-4xl mx-auto">
      <!-- Toast 提示 -->
      <Transition name="toast">
        <div
          v-if="showToast"
          class="fixed top-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium"
          :style="{
            background: toastType === 'success' ? '#8A9A86' : '#C4453E',
            color: '#fff'
          }"
        >
          {{ toastMessage }}
        </div>
      </Transition>

      <!-- 删除确认对话框 -->
      <Dialog v-model:open="showDeleteConfirm">
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除文章「{{ deleteTargetTitle }}」吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" @click="cancelDelete">取消</Button>
            <Button variant="destructive" @click="handleDelete">确认删除</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <!-- 头部 -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-foreground" style="font-family: var(--font-serif);">管理后台</h1>
          <p class="text-sm mt-1" style="color: #8C7E74;">管理你的博客文章</p>
        </div>
        <button class="btn-ghost text-sm" @click="logout">退出登录</button>
      </div>

      <!-- 加载 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="h-20 bg-muted rounded-xl animate-pulse" />
      </div>

      <!-- 文章管理 -->
      <div v-else class="space-y-6">
        <!-- 新建按钮 / 编辑器 -->
        <div v-if="!showEditor">
          <button class="btn-primary" @click="openEditor()">
            <span>+ 新建文章</span>
          </button>
        </div>

        <!-- 编辑器面板 -->
        <Transition name="editor">
          <div v-if="showEditor" class="glass-strong rounded-2xl p-6 space-y-5">
            <div class="flex items-center justify-between">
              <h2 class="text-base font-semibold text-foreground">
                {{ editingPostId ? '编辑文章' : '新建文章' }}
              </h2>
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
                v-if="!editingPost.cover_image"
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
                <img :src="editingPost.cover_image" class="w-full h-48 object-cover" />
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
              <CanvasEditor v-model="editingPost.content" />
            </div>

            <!-- 操作栏 -->
            <div class="flex items-center justify-end gap-3 pt-2">
              <button class="btn-ghost text-sm" @click="closeEditor" :disabled="saving">取消</button>
              <button
                class="btn-ghost text-sm"
                @click="submitPost(false)"
                :disabled="saving"
              >
                {{ saving ? '保存中...' : '保存草稿' }}
              </button>
              <button
                class="btn-primary disabled:opacity-50"
                @click="submitPost(true)"
                :disabled="saving"
              >
                <span>{{ saving ? '发布中...' : '发布文章' }}</span>
              </button>
            </div>
          </div>
        </Transition>

        <!-- 文章列表 -->
        <div class="space-y-3">
          <div
            v-for="post in posts"
            :key="post.id"
            class="card-neu p-5 flex items-center justify-between"
            :style="{ opacity: deletingId === post.id ? '0.5' : '1' }"
          >
            <div class="min-w-0 flex-1">
              <div class="min-w-0">
                <h3 class="font-medium text-foreground truncate" style="font-family: var(--font-serif);">{{ post.title }}</h3>
                <p class="text-xs mt-1" style="color: #8C7E74;">
                  {{ new Date(post.created_at).toLocaleDateString('zh-CN') }} ·
                  <span :style="{ color: post.published ? '#8A9A86' : '#E07A5F' }">
                    {{ post.published ? '已发布' : '草稿' }}
                  </span>
                  <span v-if="post.tags.length"> · {{ post.tags.join(', ') }}</span>
                </p>
              </div>
            </div>
            <div class="flex gap-2 ml-4 shrink-0">
              <button
                class="px-3 py-1.5 text-xs rounded-lg transition-colors duration-200"
                :style="{
                  background: post.published ? 'rgba(138, 154, 134, 0.1)' : 'rgba(224, 122, 95, 0.1)',
                  color: post.published ? '#8A9A86' : '#E07A5F'
                }"
                @click="togglePublish(post)"
              >
                {{ post.published ? '取消发布' : '发布' }}
              </button>
              <button
                class="btn-ghost px-3! py-1.5! text-xs"
                @click="openEditor(post)"
              >编辑</button>
              <button
                class="px-3 py-1.5 text-xs rounded-lg transition-colors duration-200"
                style="background: rgba(196, 69, 62, 0.08); color: #C4453E;"
                @click="confirmDelete(post)"
                :disabled="deletingId === post.id"
              >
                {{ deletingId === post.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!posts.length" class="text-center py-12">
            <p class="text-sm" style="color: #8C7E74;">暂无文章，点击上方按钮创建第一篇文章</p>
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

.toast-enter-active {
  transition: all 0.3s ease-out;
}
.toast-leave-active {
  transition: all 0.2s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.fade-enter-active {
  transition: all 0.2s ease-out;
}
.fade-leave-active {
  transition: all 0.15s ease-in;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
