<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { mockPosts } from '@/data/mockPosts'

const router = useRouter()
const selectedTag = ref<string | null>(null)
const scrollY = ref(0)

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
function onScroll() { scrollY.value = window.scrollY }

const allTags = computed(() => {
  const tags = new Set<string>()
  mockPosts.forEach(p => p.tags.forEach(t => tags.add(t)))
  return Array.from(tags)
})

const filteredPosts = computed(() => {
  if (!selectedTag.value) return mockPosts
  return mockPosts.filter(p => p.tags.includes(selectedTag.value!))
})

function goToPost(id: string) {
  router.push(`/post/${id}`)
}
</script>

<template>
  <div class="min-h-screen">
    <!-- 顶部 -->
    <section class="relative pt-28 pb-16 px-6 overflow-hidden">
      <div
        class="blob w-[300px] h-[300px] -top-20 right-10"
        style="background: #E07A5F;"
        :style="{ transform: `translateY(${scrollY * 0.04}px)`, opacity: 0.08 }"
      />
      <div
        class="blob w-[200px] h-[200px] bottom-0 -left-20"
        style="background: #8A9A86;"
        :style="{ transform: `translateY(${-scrollY * 0.03}px)`, opacity: 0.06 }"
      />

      <div class="max-w-4xl mx-auto relative z-10">
        <h1
          class="text-4xl md:text-5xl font-bold text-foreground mb-3 tracking-tight"
          style="font-family: var(--font-serif);"
        >
          博客
        </h1>
        <p style="color: #8C7E74;">记录生活与技术的点点滴滴</p>
        <div class="divider-fade max-w-xs mt-6" />
      </div>
    </section>

    <!-- 标签筛选 -->
    <section class="px-6 pb-8">
      <div class="max-w-4xl mx-auto flex flex-wrap gap-2">
        <button
          :class="[
            'tag-pill transition-all duration-200 cursor-pointer',
            selectedTag === null ? 'text-primary! bg-primary/8!' : '',
          ]"
          @click="selectedTag = null"
        >
          全部
        </button>
        <button
          v-for="tag in allTags"
          :key="tag"
          :class="[
            'tag-pill transition-all duration-200 cursor-pointer',
            selectedTag === tag ? 'text-primary! bg-primary/8!' : '',
          ]"
          @click="selectedTag = tag"
        >
          {{ tag }}
        </button>
      </div>
    </section>

    <!-- 文章列表 -->
    <section class="px-6 pb-24">
      <div class="max-w-4xl mx-auto space-y-5">
        <div
          v-for="(post, i) in filteredPosts"
          :key="post.id"
          :class="[
            'cursor-pointer group',
            i % 3 === 0 ? 'card-glass p-1' : 'card-neu',
          ]"
          @click="goToPost(post.id)"
        >
          <!-- 大卡 -->
          <div v-if="i % 3 === 0 && post.images.length" class="flex flex-col md:flex-row">
            <div class="md:w-2/5 aspect-video md:aspect-auto overflow-hidden rounded-t-xl md:rounded-l-xl md:rounded-tr-none bg-muted">
              <img
                :src="post.images[0].url"
                :alt="post.title"
                class="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-700 ease-out"
                loading="lazy"
              />
            </div>
            <div class="flex-1 p-6 flex flex-col justify-center">
              <div class="flex items-center gap-2 text-xs mb-3" style="color: #8C7E74;">
                <time>{{ post.createdAt }}</time>
                <span v-for="tag in post.tags" :key="tag" class="tag-pill">{{ tag }}</span>
              </div>
              <h2
                class="text-xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300 mb-2"
                style="font-family: var(--font-serif);"
              >
                {{ post.title }}
              </h2>
              <p class="text-sm line-clamp-3 leading-relaxed" style="color: #8C7E74;">
                {{ post.excerpt }}
              </p>
            </div>
          </div>

          <!-- 普通卡片 -->
          <div v-else class="p-6 flex flex-col md:flex-row gap-5">
            <div
              v-if="post.images.length"
              class="md:w-40 h-28 shrink-0 rounded-xl overflow-hidden bg-muted"
            >
              <img
                :src="post.images[0].thumbnail"
                :alt="post.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                loading="lazy"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs mb-2" style="color: #8C7E74;">
                <time>{{ post.createdAt }}</time>
              </div>
              <h2
                class="font-semibold text-foreground group-hover:text-primary transition-colors duration-300 mb-1.5 line-clamp-2"
                style="font-family: var(--font-serif);"
              >
                {{ post.title }}
              </h2>
              <p class="text-sm line-clamp-2 mb-3" style="color: #8C7E74;">{{ post.excerpt }}</p>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="tag in post.tags" :key="tag" class="tag-pill">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredPosts.length === 0" class="text-center py-20">
          <div class="glass rounded-2xl p-12 inline-block">
            <p class="text-lg mb-2" style="color: #8C7E74;">暂无相关文章</p>
            <button class="btn-ghost text-sm" @click="selectedTag = null">查看全部</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
