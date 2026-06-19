<script setup lang="ts">
const currentYear = new Date().getFullYear()

const links = [
  { name: '首页', path: '/' },
  { name: '博客', path: '/blog' },
  { name: '关于', path: '/about' },
]
</script>

<template>
  <footer class="relative px-6 pt-14 pb-8 overflow-hidden">
    <div class="absolute inset-0 bg-linear-to-b from-transparent to-primary/3" />

    <div class="max-w-5xl mx-auto relative z-10">
      <div class="glass rounded-2xl p-8 md:p-10 mb-8">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div class="text-center md:text-left">
            <h3
              class="text-lg font-bold text-foreground mb-2"
              style="font-family: var(--font-serif);"
            >
              MemoryThread
            </h3>
            <p class="text-sm leading-relaxed" style="color: #8C7E74;">
              记录生活，分享思考。<br>留下成长的足迹。
            </p>
          </div>

          <div class="text-center md:text-right">
            <h4 class="text-sm font-semibold mb-3 text-foreground">快速链接</h4>
            <ul class="flex flex-wrap justify-center md:justify-end gap-4">
              <li v-for="link in links" :key="link.path">
                <router-link
                  :to="link.path"
                  class="text-sm hover:text-primary transition-colors duration-200"
                  style="color: #8C7E74;"
                >
                  {{ link.name }}
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="text-center">
        <div class="divider-fade max-w-xs mx-auto mb-4" />
        <p class="text-xs" style="color: #BFB3A3;">
          &copy; {{ currentYear }} Memory Thread. All rights reserved.
        </p>
        <p class="text-xs mt-2" style="color: #BFB3A3;">
          <a
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-primary transition-colors duration-200"
          >
            宁ICP备2026001665号-1
          </a>
        </p>
      </div>
    </div>
  </footer>
</template>
