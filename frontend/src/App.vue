<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Lenis from 'lenis'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

const route = useRoute()
let lenis: Lenis | undefined

onMounted(() => {
  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    wheelMultiplier: 1,
    touchMultiplier: 2,
  })

  function raf(time: number) {
    lenis?.raf(time)
    requestAnimationFrame(raf)
  }

  requestAnimationFrame(raf)
})

onUnmounted(() => {
  lenis?.destroy()
})

// 路由切换时回到顶部
watch(() => route.path, () => {
  lenis?.scrollTo(0, { immediate: true })
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <Navbar />
    <main class="flex-1 pt-16">
      <router-view v-slot="{ Component, route }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </main>
    <Footer />
  </div>
</template>

<style>
.page-enter-active {
  transition: opacity 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
