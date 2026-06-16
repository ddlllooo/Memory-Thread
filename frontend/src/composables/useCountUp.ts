import { ref, watch, onUnmounted, toValue, type Ref } from 'vue'

/**
 * 数字滚动计数器
 * @param target 目标值（Ref 或 getter）
 * @param duration 动画时长（毫秒）
 */
export function useCountUp(target: Ref<number> | (() => number), duration = 1200) {
  const current = ref(0)
  let rafId = 0

  function animate(from: number, to: number) {
    cancelAnimationFrame(rafId)
    if (from === to) { current.value = to; return }

    const start = performance.now()
    const diff = to - from

    function tick(now: number) {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // easeOutExpo：先快后慢，更有冲击力
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      current.value = Math.round(from + diff * ease)
      if (progress < 1) rafId = requestAnimationFrame(tick)
    }

    rafId = requestAnimationFrame(tick)
  }

  watch(target, (to) => {
    animate(current.value, to)
  }, { immediate: true })

  onUnmounted(() => cancelAnimationFrame(rafId))

  return current
}
