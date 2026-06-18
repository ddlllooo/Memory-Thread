<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi } from '@/api/posts'
import { useScroll } from '@/composables/useScroll'
import { sanitizeHtml } from '@/utils/sanitize'
import { formatDate } from '@/utils/format'
import type { Post } from '@/types'

const route = useRoute()
const router = useRouter()
const { scrollY } = useScroll()
const loading = ref(true)
const post = ref<Post | null>(null)
const readProgress = ref(0)

const sanitizedContent = computed(() =>
  post.value ? sanitizeHtml(post.value.content) : ''
)

onMounted(async () => {
  const id = route.params.id as string
  try {
    post.value = await postsApi.getPost(id)
  } catch (error) {
    console.error('加载文章失败:', error)
    post.value = null
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  // useScroll handles cleanup
})

function onScroll() {
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  readProgress.value = docHeight > 0 ? Math.min(1, scrollY.value / docHeight) : 0
}

function goBack() {
  router.push('/blog')
}
</script>

<template>
  <div class="min-h-screen">
    <!-- 阅读进度 -->
    <div class="fixed top-0 left-0 right-0 z-60 h-0.5">
      <div
        class="h-full transition-all duration-100"
        style="background: linear-gradient(90deg, #E07A5F, #8A9A86);"
        :style="{ width: `${readProgress * 100}%` }"
      />
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="pt-32 px-6 max-w-3xl mx-auto space-y-4">
      <div class="h-10 bg-muted rounded-xl animate-pulse w-2/3" />
      <div class="h-4 bg-muted rounded-lg w-1/3 animate-pulse" />
      <div class="h-72 bg-muted rounded-2xl animate-pulse" />
    </div>

    <!-- 未找到 -->
    <div v-else-if="!post" class="pt-32 text-center px-6">
      <div class="glass rounded-2xl p-12 inline-block max-w-md">
        <p class="text-lg mb-4" style="color: #8C7E74;">文章不存在</p>
        <button class="btn-primary" @click="goBack"><span>返回博客</span></button>
      </div>
    </div>

    <!-- 文章 -->
    <article v-else>
      <!-- 封面 HERO -->
      <section
        v-if="post.cover_image"
        class="relative h-[50vh] md:h-[60vh] overflow-hidden"
      >
        <div
          class="absolute inset-0 bg-cover bg-center"
          :style="{
            backgroundImage: `url(${post.cover_image})`,
            transform: `translateY(${scrollY * 0.2}px) scale(${1 + scrollY * 0.0002})`,
          }"
        />
        <div class="absolute inset-0 bg-linear-to-t from-background via-background/50 to-transparent" />
      </section>

      <!-- 正文区域 -->
      <section class="px-6 pb-24">
        <div class="max-w-3xl mx-auto">
          <!-- 标题卡 -->
          <div
            :class="[
              'glass-strong rounded-2xl p-8 md:p-10 relative z-10 mb-10',
              post.cover_image ? '-mt-16' : 'mt-20',
            ]"
          >
            <!-- 返回按钮 -->
            <button
              class="inline-flex items-center gap-1.5 text-xs mb-6 transition-colors duration-200 hover:text-primary"
              style="color: #8C7E74;"
              @click="goBack"
            >
              ← 返回博客
            </button>

            <h1
              class="text-3xl md:text-4xl font-bold text-foreground mb-4 tracking-tight leading-tight"
              style="font-family: var(--font-serif);"
            >
              {{ post.title }}
            </h1>
            <div class="flex items-center gap-3 text-sm" style="color: #8C7E74;">
              <time>{{ formatDate(post.created_at) }}</time>
              <span style="color: #D5CBBD;">·</span>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="tag in post.tags" :key="tag" class="tag-pill">{{ tag }}</span>
              </div>
            </div>
          </div>

          <!-- 正文 -->
          <div class="card-neu p-8 md:p-10">
            <div
              class="prose max-w-none text-foreground leading-relaxed"
              style="font-family: var(--font-sans);"
              v-html="sanitizedContent"
            />
          </div>

          <!-- 底部 -->
          <div class="mt-10 flex justify-center">
            <button class="btn-ghost" @click="goBack">
              ← 返回博客
            </button>
          </div>
        </div>
      </section>
    </article>
  </div>
</template>

<style scoped>
.prose :deep(p) {
  margin-bottom: 1em;
  line-height: 1.9;
}

.prose :deep(h1) {
  font-family: var(--font-serif);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 1.5em 0 0.5em;
  color: var(--foreground);
}

.prose :deep(h2) {
  font-family: var(--font-serif);
  font-size: 1.375rem;
  font-weight: 600;
  margin: 1.25em 0 0.5em;
  color: var(--foreground);
}

.prose :deep(h3) {
  font-family: var(--font-serif);
  font-size: 1.125rem;
  font-weight: 600;
  margin: 1em 0 0.5em;
  color: var(--foreground);
}

.prose :deep(ul) {
  list-style-type: disc;
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.prose :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.prose :deep(li) {
  margin-bottom: 0.3em;
  line-height: 1.8;
}

.prose :deep(blockquote) {
  border-left: 3px solid #E07A5F;
  padding-left: 1em;
  margin: 1em 0;
  color: #8C7E74;
  font-style: italic;
}

.prose :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5em 0;
}

.prose :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em 0;
}

.prose :deep(mark) {
  border-radius: 2px;
  padding: 0 2px;
}

.prose :deep(strong) {
  font-weight: 600;
}

.prose :deep(em) {
  font-style: italic;
}

.prose :deep(u) {
  text-decoration: underline;
}

.prose :deep(s) {
  text-decoration: line-through;
}
</style>
