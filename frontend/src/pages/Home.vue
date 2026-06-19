<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postsApi } from '@/api/posts'
import { useScroll } from '@/composables/useScroll'
import { formatDate, stripHtml } from '@/utils/format'
import type { Post } from '@/types'

const router = useRouter()
const { scrollY } = useScroll()
const recentPosts = ref<Post[]>([])
const heroVisible = ref(false)
const loading = ref(true)
const loadError = ref(false)

onMounted(async () => {
  requestAnimationFrame(() => { heroVisible.value = true })

  try {
    const response = await postsApi.getPosts(1, 3, true)
    recentPosts.value = response.data
  } catch (error) {
    console.error('加载文章失败:', error)
    loadError.value = true
  } finally {
    loading.value = false
  }
})

function goToPost(id: string) {
  router.push(`/post/${id}`)
}

function goToBlog() {
  router.push('/blog')
}

function reloadPage() {
  window.location.reload()
}
</script>

<template>
  <div class="min-h-screen">
    <!-- ========== HERO ========== -->
    <section class="relative h-screen flex items-center justify-center overflow-hidden">
      <!-- 暖调光斑 -->
      <div
        class="blob w-[500px] h-[500px] -top-40 -left-40"
        style="background: #E07A5F;"
        :style="{ transform: `translate(${scrollY * 0.02}px, ${scrollY * 0.04}px)`, opacity: 0.12 }"
      />
      <div
        class="blob w-[400px] h-[400px] -bottom-20 -right-20"
        style="background: #8A9A86;"
        :style="{ transform: `translate(${-scrollY * 0.015}px, ${-scrollY * 0.03}px)`, opacity: 0.1 }"
      />

      <!-- 网格点阵 -->
      <div
        class="absolute inset-0"
        style="background-image: radial-gradient(circle, #2B221E 0.5px, transparent 0.5px); background-size: 40px 40px; opacity: 0.025;"
      />

      <!-- Hero 内容 -->
      <div
        class="relative z-10 max-w-2xl mx-auto px-6 text-center"
        :style="{ transform: `translateY(${scrollY * 0.12}px)`, opacity: Math.max(0, 1 - scrollY / 500) }"
      >
        <p
          :class="['text-xs tracking-[0.25em] uppercase mb-6 transition-all duration-1000 ease-out', heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6']"
          style="color: #8A9A86;"
        >
          Personal Blog
        </p>

        <h1
          :class="['text-5xl md:text-7xl font-bold tracking-tight text-foreground mb-6 transition-all duration-1000 delay-150 ease-out leading-tight', heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6']"
          style="font-family: var(--font-serif);"
        >
          记录生活<br>
          <span class="text-gradient">分享思考</span>
        </h1>

        <p
          :class="['text-base md:text-lg mb-10 max-w-md mx-auto transition-all duration-1000 delay-300 ease-out', heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6']"
          style="color: #8C7E74;"
        >
          在这里留下成长的足迹，用文字和图片编织属于自己的故事。
        </p>

        <div
          :class="['flex items-center justify-center gap-4 transition-all duration-1000 delay-500 ease-out', heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6']"
        >
          <button class="btn-primary" @click="goToBlog">
            <span>开始阅读</span>
          </button>
          <button class="btn-ghost" @click="router.push('/about')">
            了解更多
          </button>
        </div>
      </div>

      <!-- 滚动指示 -->
      <div
        class="absolute bottom-10 left-1/2 -translate-x-1/2"
        :style="{ opacity: Math.max(0, 1 - scrollY / 200) }"
      >
        <div class="w-5 h-9 rounded-full flex items-start justify-center p-1.5" style="border: 1.5px solid #D5CBBD;">
          <div class="w-1 h-2 rounded-full animate-bounce" style="background: #BFB3A3;" />
        </div>
      </div>
    </section>

    <!-- ========== 最新文章 ========== -->
    <section class="relative py-24 px-6">
      <div class="max-w-5xl mx-auto">
        <div class="mb-14 text-center">
          <h2
            class="text-3xl md:text-4xl font-bold text-foreground mb-3"
            style="font-family: var(--font-serif);"
          >
            最新文章
          </h2>
          <p style="color: #8C7E74;">最近写下的想法与记录</p>
          <div class="divider-fade max-w-xs mx-auto mt-6" />
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-12 gap-6">
          <div class="md:col-span-7 h-80 bg-muted rounded-2xl animate-pulse" />
          <div class="md:col-span-5 flex flex-col gap-6">
            <div class="h-28 bg-muted rounded-xl animate-pulse" />
            <div class="h-28 bg-muted rounded-xl animate-pulse" />
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="loadError" class="text-center py-12">
          <p class="text-sm mb-4" style="color: #8C7E74;">加载文章失败，请稍后重试</p>
          <button class="btn-ghost text-sm" @click="reloadPage()">重新加载</button>
        </div>

        <!-- 非对称网格 -->
        <div v-else-if="recentPosts.length" class="grid grid-cols-1 md:grid-cols-12 gap-6">
          <!-- 大卡 -->
          <div
            class="md:col-span-7 card-glass p-1 cursor-pointer group"
            @click="goToPost(recentPosts[0].id)"
          >
            <div v-if="recentPosts[0].cover_image" class="rounded-xl overflow-hidden bg-muted aspect-16/10">
              <img
                :src="recentPosts[0].cover_image"
                :alt="recentPosts[0].title"
                class="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-700 ease-out"
                loading="lazy"
              />
            </div>
            <div class="p-5">
              <div class="flex items-center gap-2 text-xs mb-2 text-muted-foreground">
                <time>{{ formatDate(recentPosts[0].created_at) }}</time>
                <span v-for="tag in recentPosts[0].tags.slice(0, 2)" :key="tag" class="tag-pill">{{ tag }}</span>
              </div>
              <h3
                class="text-xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300 mb-1"
                style="font-family: var(--font-serif);"
              >
                {{ recentPosts[0].title }}
              </h3>
              <p class="text-sm line-clamp-2 text-muted-foreground">{{ recentPosts[0].summary || stripHtml(recentPosts[0].content, 120) }}</p>
            </div>
          </div>

          <!-- 小卡 -->
          <div class="md:col-span-5 flex flex-col gap-6">
            <div
              v-for="post in recentPosts.slice(1, 3)"
              :key="post.id"
              class="card-neu p-4 cursor-pointer group flex gap-4"
              @click="goToPost(post.id)"
            >
              <div
                v-if="post.cover_image"
                class="w-24 h-24 shrink-0 rounded-xl overflow-hidden bg-muted"
              >
                <img
                  :src="post.cover_image"
                  :alt="post.title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
              </div>
              <div class="flex-1 min-w-0 flex flex-col justify-center">
                <div class="text-xs mb-1 text-muted-foreground">
                  <time>{{ formatDate(post.created_at) }}</time>
                </div>
                <h3
                  class="font-semibold text-foreground group-hover:text-primary transition-colors duration-300 line-clamp-2 text-sm"
                  style="font-family: var(--font-serif);"
                >
                  {{ post.title }}
                </h3>
                <p class="text-xs line-clamp-1 mt-1 text-muted-foreground">{{ post.summary || stripHtml(post.content, 80) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="text-center mt-12">
          <button class="btn-ghost" @click="goToBlog">
            查看全部文章 →
          </button>
        </div>
      </div>
    </section>

    <!-- ========== 简介条 ========== -->
    <section class="relative py-20 px-6 overflow-hidden">
      <div class="absolute inset-0 bg-linear-to-br from-primary/4 via-transparent to-green/4" />
      <div class="max-w-3xl mx-auto text-center relative z-10">
        <div class="glass-strong rounded-2xl p-10 md:p-14">
          <h2
            class="text-2xl md:text-3xl font-bold text-foreground mb-4"
            style="font-family: var(--font-serif);"
          >
            关于这个博客
          </h2>
          <p class="leading-relaxed mb-8" style="color: #8C7E74;">
            这是一个记录生活与技术的个人空间。不追求华丽，只希望每一篇文章都能真实地表达当时的想法。
            如果某篇文章恰好对你有帮助，那就更好了。
          </p>
          <button class="btn-primary" @click="router.push('/about')">
            <span>了解更多</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
