<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { statsApi, type VisitorStats } from '@/api/stats'
import { useCountUp } from '@/composables/useCountUp'
import ContributionGrid from '@/components/ui/ContributionGrid.vue'

const scrollY = ref(0)
const stats = ref<VisitorStats | null>(null)
const selectedYear = ref(new Date().getFullYear())

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  fetchStats()
})

onUnmounted(() => window.removeEventListener('scroll', onScroll))
function onScroll() { scrollY.value = window.scrollY }

async function fetchStats(year?: number) {
  const data = await statsApi.getStats(year)
  stats.value = data
}

function onYearChange(year: number) {
  selectedYear.value = year
  fetchStats(year)
}

// 四个滚动数字
const targetVisits = computed(() => stats.value?.total_visits ?? 0)
const targetPosts = computed(() => stats.value?.published_posts ?? 0)
const targetImages = computed(() => stats.value?.total_images ?? 0)
const targetDays = computed(() => stats.value?.running_days ?? 0)

const animVisits = useCountUp(targetVisits)
const animPosts = useCountUp(targetPosts)
const animImages = useCountUp(targetImages)
const animDays = useCountUp(targetDays, 1600)

const summaryItems = [
  { value: animVisits, label: '总访问量', color: '#C84B31', pixels: [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0] },
  { value: animPosts, label: '已发布文章', color: '#E07A5F', pixels: [0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0] },
  { value: animImages, label: '图片数量', color: '#E8A87C', pixels: [1,1,0,0,1,0,1,0,0,1,0,1,0,0,1,1] },
  { value: animDays, label: '运行天数', color: '#F5D0A9', pixels: [0,1,1,0,1,0,0,1,1,0,1,0,0,1,1,0] },
]
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
        <p style="color: #8C7E74;">访客足迹 · 数据记录</p>
        <div class="divider-fade max-w-xs mt-6" />
      </div>
    </section>

    <!-- 贡献格子 -->
    <section class="px-6 pb-8">
      <div class="max-w-[53rem] mx-auto">
        <div class="glass-strong rounded-2xl p-8 md:p-10">
          <h2
            class="text-lg font-semibold text-foreground mb-5"
            style="font-family: var(--font-serif);"
          >
            访问热力图
          </h2>
          <ContributionGrid
            v-if="stats"
            :data="stats.daily_visits"
            :years="stats.years"
            :current-year="selectedYear"
            @update:year="onYearChange"
          />
          <div v-else class="h-24 flex items-center justify-center" style="color: #8C7E74;">
            加载中...
          </div>
        </div>
      </div>
    </section>

    <!-- 统计摘要 -->
    <section class="px-6 pb-24">
      <div class="max-w-3xl mx-auto">
        <div
          v-if="stats"
          class="grid grid-cols-2 md:grid-cols-4 gap-3"
        >
          <div
            v-for="(item, i) in summaryItems"
            :key="i"
            class="pixel-card"
          >
            <!-- 像素图标 -->
            <div class="pixel-icon" :style="{ color: item.color }">
              <svg viewBox="0 0 4 4" width="20" height="20">
                <rect
                  v-for="(on, j) in item.pixels"
                  :key="j"
                  v-show="on"
                  :x="j % 4"
                  :y="Math.floor(j / 4)"
                  width="1"
                  height="1"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div class="pixel-number">{{ item.value }}</div>
            <div class="pixel-label">{{ item.label }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.pixel-card {
  background: #F5F0EB;
  border: 2px solid #D9D0C7;
  padding: 20px 16px;
  text-align: center;
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pixel-card:hover {
  transform: translateY(-2px);
  box-shadow: 4px 4px 0 #D9D0C7;
}

.pixel-icon {
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
}

.pixel-number {
  font-family: 'Courier New', Courier, monospace;
  font-size: 28px;
  font-weight: 700;
  color: #3D332C;
  line-height: 1;
  margin-bottom: 6px;
}

.pixel-label {
  font-size: 12px;
  color: #8C7E74;
  letter-spacing: 0.5px;
}
</style>
