<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const scrolled = ref(false)
const mobileOpen = ref(false)
const hidden = ref(false)
let lastY = 0

const navItems = [
  { name: '首页', path: '/' },
  { name: '博客', path: '/blog' },
  { name: '关于', path: '/about' },
]

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// 路由切换时自动关闭移动端菜单
watch(() => route.path, () => {
  mobileOpen.value = false
})

function onScroll() {
  const y = window.scrollY
  scrolled.value = y > 30
  hidden.value = y > 200 && y > lastY
  lastY = y
}

function go(path: string) {
  router.push(path)
  mobileOpen.value = false
}

function active(path: string) {
  return route.path === path
}
</script>

<template>
  <nav
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-out',
      hidden ? '-translate-y-full' : 'translate-y-0',
      scrolled
        ? 'glass-strong shadow-sm'
        : 'bg-transparent',
    ]"
  >
    <div class="max-w-5xl mx-auto px-6">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <button
          class="text-lg font-semibold tracking-tight text-foreground hover:text-primary transition-colors duration-300"
          style="font-family: var(--font-serif);"
          @click="go('/')"
        >
          MemoryThread
        </button>

        <!-- 桌面导航 -->
        <div class="hidden md:flex items-center gap-1">
          <button
            v-for="item in navItems"
            :key="item.path"
            :class="[
              'px-4 py-2 rounded-lg text-sm transition-all duration-300',
              active(item.path)
                ? 'text-primary bg-primary/8 font-medium'
                : 'text-foreground/60 hover:text-foreground hover:bg-foreground/5',
            ]"
            @click="go(item.path)"
          >
            {{ item.name }}
          </button>
          <button
            v-if="authStore.isAuthenticated"
            :class="[
              'px-4 py-2 rounded-lg text-sm transition-all duration-300',
              active('/admin')
                ? 'text-primary bg-primary/8 font-medium'
                : 'text-foreground/60 hover:text-foreground hover:bg-foreground/5',
            ]"
            @click="go('/admin')"
          >
            管理
          </button>
        </div>

        <!-- 移动端按钮 -->
        <button
          class="md:hidden w-10 h-10 flex items-center justify-center rounded-lg hover:bg-foreground/5 transition-colors"
          :aria-expanded="mobileOpen"
          aria-label="切换导航菜单"
          @click="mobileOpen = !mobileOpen"
        >
          <div class="relative w-5 h-4">
            <span
              :class="[
                'absolute left-0 w-full h-0.5 bg-foreground rounded transition-all duration-300',
                mobileOpen ? 'top-1.5 rotate-45' : 'top-0',
              ]"
            />
            <span
              :class="[
                'absolute left-0 w-full h-0.5 bg-foreground rounded transition-all duration-300 top-1.5',
                mobileOpen ? 'opacity-0 scale-x-0' : 'opacity-100 scale-x-100',
              ]"
            />
            <span
              :class="[
                'absolute left-0 w-full h-0.5 bg-foreground rounded transition-all duration-300',
                mobileOpen ? 'top-1.5 -rotate-45' : 'top-3',
              ]"
            />
          </div>
        </button>
      </div>

      <!-- 移动端菜单 -->
      <Transition name="menu">
        <div
          v-if="mobileOpen"
          class="md:hidden pb-4"
        >
          <div class="glass rounded-xl p-2 mt-2 space-y-1">
            <button
              v-for="item in navItems"
              :key="item.path"
              :class="[
                'w-full text-left px-4 py-3 rounded-lg text-sm transition-all duration-200',
                active(item.path)
                  ? 'text-primary bg-primary/8 font-medium'
                  : 'text-foreground/60 hover:text-foreground hover:bg-foreground/5',
              ]"
              @click="go(item.path)"
            >
              {{ item.name }}
            </button>
            <button
              v-if="authStore.isAuthenticated"
              class="w-full text-left px-4 py-3 rounded-lg text-sm text-foreground/60 hover:text-foreground hover:bg-foreground/5 transition-all duration-200"
              @click="go('/admin')"
            >
              管理
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </nav>
</template>

<style scoped>
.menu-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.menu-leave-active {
  transition: all 0.2s ease;
}
.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
