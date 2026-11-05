<template>
  <div class="app-shell">
    <a class="skip-link" href="#main-content" :inert="drawer.isOpen.value ? '' : null">{{ t('nav.skipToContent') }}</a>

    <AppSidebar
      ref="sidebar"
      :is-open="drawer.isOpen.value"
      @close="drawer.close()"
      @show-profile-details="openProfileDetails"
      @show-tasks="openTasks"
    />
    <div
      v-if="drawer.isOpen.value"
      class="drawer-backdrop"
      aria-hidden="true"
      @click="drawer.close()"
    ></div>

    <!-- inert keeps Tab and clicks inside the drawer while it is open -->
    <div class="app-body" :inert="drawer.isOpen.value ? '' : null">
      <header class="mobile-topbar">
        <button
          ref="menuToggle"
          type="button"
          class="menu-toggle"
          aria-controls="app-sidebar"
          :aria-expanded="drawer.isOpen.value ? 'true' : 'false'"
          :aria-label="t('nav.openMenu')"
          @click="drawer.open()"
        >
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />
          </svg>
        </button>
        <span class="mobile-brand">{{ t('nav.companyName') }}</span>
      </header>
      <FilterBar />
      <main id="main-content" class="main-content" tabindex="-1">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import AppSidebar from './components/AppSidebar.vue'
import { useDrawer } from './composables/useDrawer'

export default {
  name: 'App',
  components: {
    FilterBar,
    AppSidebar,
    ProfileDetailsModal,
    TasksModal
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])
    const sidebar = ref(null)
    const menuToggle = ref(null)
    const drawer = useDrawer(menuToggle, sidebar)

    // The modals sit above the drawer, so close it without pulling focus back to the toggle
    const openProfileDetails = () => {
      drawer.close({ restoreFocus: false })
      showProfileDetails.value = true
    }
    const openTasks = () => {
      drawer.close({ restoreFocus: false })
      showTasks.value = true
    }

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      sidebar,
      menuToggle,
      drawer,
      openProfileDetails,
      openTasks,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/*
 * Design tokens. Slate palette and status colours come from the original UI.
 * The shell switches between sidebar and drawer at 1024px; the media queries here,
 * in AppSidebar.vue, FilterBar.vue and useDrawer.js must all use that same value.
 */
:root {
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-7: 2rem;
  --space-8: 3rem;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;

  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 10px 25px rgba(15, 23, 42, 0.15);

  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #334155;
  --color-text-strong: #0f172a;
  --color-text-muted: #64748b;
  --color-primary: #2563eb;
  --color-primary-bg: #eff6ff;
  --color-primary-fg: #1e40af;
  --color-success: #059669;
  --color-success-bg: #d1fae5;
  --color-success-fg: #065f46;
  --color-warning: #ea580c;
  --color-warning-bg: #fed7aa;
  --color-warning-fg: #92400e;
  --color-danger: #dc2626;
  --color-danger-bg: #fecaca;
  --color-danger-fg: #991b1b;
  --color-danger-tint: #fef2f2;
  --color-info: #2563eb;
  --color-info-bg: #dbeafe;
  --color-info-fg: #1e40af;
  --color-focus: #2563eb;

  --color-sidebar-bg: #0f172a;
  --color-sidebar-text: #94a3b8;
  --color-sidebar-text-strong: #f8fafc;
  --color-sidebar-hover: rgba(248, 250, 252, 0.06);
  --color-sidebar-active: rgba(248, 250, 252, 0.12);
  --color-sidebar-border: rgba(248, 250, 252, 0.1);
  --color-sidebar-accent: #60a5fa;

  --sidebar-width: 240px;
  --topbar-height: 56px;
  --content-max-width: 1600px;

  --z-raised: 1;
  --z-sticky: 10;
  --z-sidebar: 20;
  --z-dropdown: 30;
  --z-backdrop: 40;
  --z-drawer: 50;
  --z-modal: 100;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.skip-link {
  position: fixed;
  top: var(--space-2);
  left: var(--space-2);
  z-index: var(--z-modal);
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  color: var(--color-text-strong);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transform: translateY(-200%);
}

.skip-link:focus {
  transform: none;
}

/* App shell: sidebar column plus content column. minmax(0, 1fr) stops wide tables stretching the page. */
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100dvh;
}

.app-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mobile-topbar {
  display: none;
}

.drawer-backdrop {
  position: fixed;
  inset: 0;
  z-index: var(--z-backdrop);
  background: rgba(15, 23, 42, 0.5);
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-5);
}

.main-content:focus {
  outline: none;
}

@media (max-width: 1023.98px) {
  .app-shell {
    grid-template-columns: minmax(0, 1fr);
  }

  .mobile-topbar {
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    height: var(--topbar-height);
    padding: 0 var(--space-2);
    background: var(--color-sidebar-bg);
    color: var(--color-sidebar-text-strong);
  }

  .menu-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    color: inherit;
    cursor: pointer;
    transition: background-color 0.15s ease;
  }

  .menu-toggle:hover {
    background: var(--color-sidebar-hover);
  }

  .menu-toggle:focus-visible {
    outline-color: var(--color-sidebar-accent);
  }

  .menu-toggle svg {
    width: 20px;
    height: 20px;
  }

  .mobile-brand {
    font-size: var(--text-base);
    font-weight: var(--weight-semibold);
    letter-spacing: -0.02em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .main-content {
    padding: var(--space-4);
  }
}

/* Page header: one h1 per route */
.page-header {
  margin-bottom: var(--space-4);
}

.page-header h1 {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text-strong);
  margin-bottom: var(--space-1);
  letter-spacing: -0.02em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  transition: border-color 0.15s ease;
}

.stat-card:hover {
  border-color: var(--color-border-strong);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text-strong);
  letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-danger);
}

.stat-card.info .stat-value {
  color: var(--color-info);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  margin-bottom: var(--space-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  margin-bottom: var(--space-3);
}

.card-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-text-strong);
  letter-spacing: -0.01em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--color-surface-muted);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}

/* Identifier columns (SKU, order number, quarter) should not break at their hyphens */
td:first-child {
  white-space: nowrap;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--color-bg);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  white-space: nowrap;
}

.badge.success,
.badge.increasing {
  background: var(--color-success-bg);
  color: var(--color-success-fg);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-bg);
  color: var(--color-warning-fg);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-bg);
  color: var(--color-danger-fg);
}

.badge.info,
.badge.low {
  background: var(--color-info-bg);
  color: var(--color-info-fg);
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.loading {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.error {
  background: var(--color-danger-tint);
  border: 1px solid var(--color-danger-bg);
  color: var(--color-danger-fg);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-sm);
}
</style>
