<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const scrollY = ref(0)
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
function onScroll() { scrollY.value = window.scrollY }
</script>

<template>
  <div class="min-h-screen">
    <!-- 顶部 -->
    <section class="relative pt-28 pb-16 px-6 overflow-hidden">
      <div
        class="blob w-[300px] h-[300px] -top-20 -right-20"
        style="background: #E07A5F; opacity: 0.08;"
        :style="{ transform: `translateY(${scrollY * 0.04}px)` }"
      />
      <div
        class="blob w-[200px] h-[200px] bottom-0 left-10"
        style="background: #8A9A86; opacity: 0.06;"
        :style="{ transform: `translateY(${-scrollY * 0.03}px)` }"
      />
      <div class="max-w-3xl mx-auto relative z-10">
        <h1
          class="text-4xl md:text-5xl font-bold text-foreground mb-3 tracking-tight"
          style="font-family: var(--font-serif);"
        >
          关于
        </h1>
        <p style="color: #8C7E74;">关于这个博客和背后的我</p>
        <div class="divider-fade max-w-xs mt-6" />
      </div>
    </section>

    <!-- 内容 -->
    <section class="px-6 pb-24">
      <div class="max-w-3xl mx-auto space-y-8">
        <!-- 博客介绍 -->
        <div class="glass-strong rounded-2xl p-8 md:p-10">
          <h2
            class="text-xl font-semibold text-foreground mb-4"
            style="font-family: var(--font-serif);"
          >
            关于这个博客
          </h2>
          <p class="leading-relaxed mb-4" style="color: #4A3F38;">
            Memory Thread 是一个个人博客，用来记录生活中的点滴和学习过程中的思考。
            在这里，我会分享技术笔记、读书心得、生活感悟等内容。
          </p>
          <p class="leading-relaxed" style="color: #4A3F38;">
            不追求华丽的辞藻，只希望每一篇文章都能真实地表达当时的想法。
            写作是整理思路最好的方式，如果某篇文章恰好对你有帮助，那就更好了。
          </p>
        </div>

        <!-- 关于我 -->
        <div class="card-neu p-8 md:p-10">
          <h2
            class="text-xl font-semibold text-foreground mb-4"
            style="font-family: var(--font-serif);"
          >
            关于我
          </h2>
          <p class="leading-relaxed" style="color: #4A3F38;">
            一个喜欢写代码、看书、偶尔徒步的普通人。相信记录的力量，把想法写下来，
            是整理思路最好的方式。
          </p>
        </div>

      </div>
    </section>
  </div>
</template>
