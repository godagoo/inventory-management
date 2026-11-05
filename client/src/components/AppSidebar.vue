<template>
  <aside id="app-sidebar" class="app-sidebar" :class="{ 'is-open': isOpen }">
    <div class="sidebar-brand">
      <div class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
      <button
        ref="closeButton"
        type="button"
        class="sidebar-close"
        :aria-label="t('nav.closeMenu')"
        @click="$emit('close')"
      >
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />
        </svg>
      </button>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.primary')">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-link"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path :d="item.icon" />
        </svg>
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

defineProps({
  isOpen: { type: Boolean, default: false }
})
defineEmits(['close', 'show-profile-details', 'show-tasks'])

const { t } = useI18n()
const closeButton = ref(null)

// Icon paths are 24px outline glyphs
const navItems = computed(() => [
  { to: '/', label: t('nav.overview'), icon: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z' },
  { to: '/inventory', label: t('nav.inventory'), icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
  { to: '/orders', label: t('nav.orders'), icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 7h6m-6 4h4' },
  { to: '/spending', label: t('nav.finance'), icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { to: '/demand', label: t('nav.demandForecast'), icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' },
  { to: '/restocking', label: t('nav.restocking'), icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' },
  { to: '/backlog', label: t('nav.backlog'), icon: 'M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z' },
  { to: '/reports', label: t('nav.reports'), icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' }
])

defineExpose({
  focusFirst: () => closeButton.value?.focus()
})
</script>

<style scoped>
.app-sidebar {
  position: sticky;
  top: 0;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--color-sidebar-bg);
  color: var(--color-sidebar-text);
  z-index: var(--z-sidebar);
}

.sidebar-brand {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-4) var(--space-4);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.brand-name {
  color: var(--color-sidebar-text-strong);
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  letter-spacing: -0.02em;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.brand-subtitle {
  font-size: var(--text-xs);
  line-height: 1.4;
}

.sidebar-close {
  display: none;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  margin: calc(var(--space-2) * -1) calc(var(--space-2) * -1) 0 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-sidebar-text);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.sidebar-close svg {
  width: 20px;
  height: 20px;
}

.sidebar-close:hover {
  background: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-strong);
}

.sidebar-nav {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-2) var(--space-3);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 40px;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-sidebar-text);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-link svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  min-width: 0;
  overflow-wrap: anywhere;
}

.nav-link:hover {
  background: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-strong);
}

/* Active is marked by tint, weight and a leading bar, so colour is not the only cue */
.nav-link.router-link-exact-active {
  background: var(--color-sidebar-active);
  color: var(--color-sidebar-text-strong);
  font-weight: var(--weight-semibold);
}

.nav-link.router-link-exact-active::before {
  content: '';
  position: absolute;
  left: calc(var(--space-3) * -1);
  top: var(--space-2);
  bottom: var(--space-2);
  width: 3px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  background: var(--color-sidebar-accent);
}

.nav-link:focus-visible,
.sidebar-close:focus-visible {
  outline: 2px solid var(--color-sidebar-accent);
  outline-offset: -2px;
}

/* Footer stays outside the scrolling nav so its upward menus are not clipped */
.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--color-sidebar-border);
}

@media (max-width: 1023.98px) {
  .app-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    height: auto;
    width: min(var(--sidebar-width), 85vw);
    z-index: var(--z-drawer);
    box-shadow: var(--shadow-lg);
    transform: translateX(-100%);
    /* Hidden after the slide so the closed drawer leaves the tab order */
    visibility: hidden;
    transition: transform 0.2s ease, visibility 0s linear 0.2s;
  }

  .app-sidebar.is-open {
    transform: translateX(0);
    visibility: visible;
    transition: transform 0.2s ease, visibility 0s;
  }

  .sidebar-close {
    display: inline-flex;
  }

  .nav-link {
    min-height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .app-sidebar,
  .app-sidebar.is-open {
    transition: none;
  }
}
</style>
