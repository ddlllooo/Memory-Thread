<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import type { DailyVisit } from '@/api/stats'

const props = defineProps<{
  data: DailyVisit[]
  years: number[]
  currentYear: number
}>()

const emit = defineEmits<{ (e: 'update:year', year: number): void }>()

const loaded = ref(false)
onMounted(() => {
  requestAnimationFrame(() => { loaded.value = true })
})

const LEVELS = [
  '#EDE8E3',
  '#F5D0A9',
  '#E8A87C',
  '#E07A5F',
  '#C84B31',
]

function getLevel(count: number): number {
  if (count === 0) return 0
  if (count <= 2) return 1
  if (count <= 5) return 2
  if (count <= 10) return 3
  return 4
}

const ROWS = 7

const gridData = computed(() => {
  const visits = props.data
  if (!visits.length) return { cells: [] as { date: string; count: number; level: number; row: number; col: number }[], cols: 0 }

  const total = visits.length
  const cols = Math.ceil(total / ROWS)

  const cells = visits.map((v, i) => ({
    date: v.date,
    count: v.count,
    level: getLevel(v.count),
    row: i % ROWS,
    col: Math.floor(i / ROWS),
  }))

  return { cells, cols }
})

const gridMap = computed(() => {
  const m = new Map<string, { date: string; count: number; level: number }>()
  gridData.value.cells.forEach(c => m.set(`${c.row}-${c.col}`, c))
  return m
})

// tooltip
const hovered = ref<{ date: string; count: number } | null>(null)
const tooltipPos = ref({ x: 0, y: 0 })

function onEnter(e: MouseEvent, cell: { date: string; count: number }) {
  hovered.value = cell
  const rect = (e.target as HTMLElement).getBoundingClientRect()
  tooltipPos.value = { x: rect.left + rect.width / 2, y: rect.top - 8 }
}

function onLeave() {
  hovered.value = null
}
</script>

<template>
  <div class="contribution-wrapper">
    <!-- 年份选择 -->
    <div class="header-row">
      <select
        class="year-select"
        :value="currentYear"
        @change="emit('update:year', Number(($event.target as HTMLSelectElement).value))"
      >
        <option v-for="y in years" :key="y" :value="y">{{ y }}年</option>
      </select>
    </div>

    <!-- 格子 -->
    <div
      class="cells-grid"
      :style="{
        gridTemplateColumns: `repeat(${gridData.cols}, 1fr)`,
        gridTemplateRows: `repeat(${ROWS}, 1fr)`,
      }"
    >
      <template v-for="row in ROWS" :key="row">
        <template v-for="col in gridData.cols" :key="`${row}-${col}`">
          <div
            v-if="gridMap.get(`${row - 1}-${col - 1}`)"
            class="cell"
            :class="{ 'cell-lit': loaded }"
            :style="{
              backgroundColor: LEVELS[gridMap.get(`${row - 1}-${col - 1}`)!.level],
              transitionDelay: `${(col - 1) * 15}ms`,
            }"
            @mouseenter="onEnter($event, gridMap.get(`${row - 1}-${col - 1}`)!)"
            @mouseleave="onLeave"
          />
          <div v-else class="cell cell-empty" />
        </template>
      </template>
    </div>

    <!-- 颜色图例 -->
    <div class="legend">
      <div v-for="(color, i) in LEVELS" :key="i" class="cell legend-cell" :style="{ backgroundColor: color }" />
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div
        v-if="hovered"
        class="tooltip"
        :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }"
      >
        <strong>{{ hovered.date }}</strong>
        <span>{{ hovered.count }} 次访问</span>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.contribution-wrapper {
  width: 100%;
}

.header-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 6px;
}

.year-select {
  padding: 2px 8px;
  font-size: 12px;
  color: #4A3F38;
  background: #F5F0EB;
  border: 1px solid #D9D0C7;
  border-radius: 6px;
  cursor: pointer;
  outline: none;
}

.year-select:hover {
  border-color: #C8B8A8;
}

.cells-grid {
  display: grid;
  gap: 3px;
  width: 100%;
}

.cell {
  aspect-ratio: 1;
  border-radius: 3px;
  transition: background-color 0.4s ease, transform 0.15s ease, box-shadow 0.15s ease;
}

.cell:not(.cell-empty):hover {
  transform: scale(1.4);
  box-shadow: 0 0 8px rgba(224, 122, 95, 0.5);
  z-index: 10;
  position: relative;
}

.cell-empty {
  background-color: transparent;
}

.legend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  justify-content: flex-end;
}

.legend-cell {
  width: 12px;
  height: 12px;
}

.tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background: #3D332C;
  color: #F5F0EB;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #3D332C;
}

/* 点亮动画 */
.cell:not(.cell-empty) {
  opacity: 0;
  transform: scale(0.5);
}

.cell.cell-lit:not(.cell-empty) {
  opacity: 1;
  transform: scale(1);
}
</style>
