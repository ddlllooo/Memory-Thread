import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 滚动位置监听 composable
 */
export function useScroll() {
  const scrollY = ref(0)

  function onScroll() {
    scrollY.value = window.scrollY
  }

  onMounted(() => {
    window.addEventListener('scroll', onScroll, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', onScroll)
  })

  return { scrollY }
}
