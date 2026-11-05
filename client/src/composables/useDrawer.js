import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

// Must match the shell breakpoint used in the stylesheets (the sidebar is a drawer below it)
const DESKTOP_QUERY = '(min-width: 1024px)'

/**
 * Mobile navigation drawer state: open/close, Escape, route changes, scroll lock,
 * and focus handling. `toggleButton` and `sidebar` are template refs; the sidebar
 * must expose `focusFirst()`.
 */
export function useDrawer(toggleButton, sidebar) {
  const route = useRoute()
  const isOpen = ref(false)
  const desktopQuery = window.matchMedia(DESKTOP_QUERY)

  const open = async () => {
    isOpen.value = true
    await nextTick()
    sidebar.value?.focusFirst()
  }

  // Focus goes back to the toggle only after `inert` is removed, since inert elements cannot take focus
  const close = async ({ restoreFocus = true } = {}) => {
    if (!isOpen.value) return
    isOpen.value = false
    if (!restoreFocus) return
    await nextTick()
    toggleButton.value?.focus()
  }

  const onKeydown = (event) => {
    if (event.key === 'Escape') close()
  }

  // Crossing to desktop while open would leave the content inert, so reset
  const onViewportChange = (event) => {
    if (event.matches) close({ restoreFocus: false })
  }

  watch(isOpen, (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
  })
  watch(() => route.fullPath, () => close())

  onMounted(() => {
    document.addEventListener('keydown', onKeydown)
    desktopQuery.addEventListener('change', onViewportChange)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', onKeydown)
    desktopQuery.removeEventListener('change', onViewportChange)
    document.body.style.overflow = ''
  })

  return { isOpen, open, close }
}
