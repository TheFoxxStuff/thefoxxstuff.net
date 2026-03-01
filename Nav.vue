<template>
  <header role="banner" aria-label="Site navigation">
    <div class="nav-info" aria-live="polite" aria-atomic="true" aria-relevant="text">
      <i class="bx bx-sitemap icon-16"></i>
      <div class="breadcrumbs-container">
        <div class="bread-text" ref="breadText">
          <template v-if="!isNotFoundRoute">
            <router-link 
              v-for="(crumb, index) in breadcrumbs" 
              :key="index"
              :to="crumb.path"
              class="breadcrumb-link"
            >
              {{ crumb.title }}
              <span v-if="index < breadcrumbs.length - 1" class="slash">/</span>
            </router-link>
          </template>
          <span v-else class="not-found-breadcrumb">Not Found</span>
        </div>
        <div class="fade-mask fade-left" :class="{ active: showLeftFade && !isNotFoundRoute }"></div>
        <div class="fade-mask fade-right" :class="{ active: showRightFade && !isNotFoundRoute }"></div>
      </div>
    </div>
    <button
      class="menu-toggle"
      aria-controls="mobile-menu"
      :aria-expanded="isOpen.toString()"
      :aria-label="isOpen ? 'Close menu' : 'Open menu'"
      @click="toggleMenu"
    >
      <i class="bx" :class="menuIconClass"></i>
      {{ isOpen ? 'Close menu' : 'Open menu' }}
    </button>
  </header>

  <nav
    id="mobile-menu"
    class="menu-panel"
    :class="{ active: isOpen }"
    role="menu"
    aria-label="Mobile navigation menu"
    :aria-hidden="(!isOpen).toString()"
  >
    <div class="panel-header" tabindex="-1" ref="panelHeader">Navbar</div>
    <div class="main-links" role="none">
      <router-link 
        v-for="(item, i) in mainLinks" 
        :key="i" 
        :to="item.path"
        role="menuitem" 
        :tabindex="isOpen ? (i === 0 ? 0 : -1) : -1" 
        class="btn-link"
        @click="closeMenu"
      >
        <i :class="['bx', item.icon, 'icon-20']"></i>
        {{ item.text }}
      </router-link>
    </div>
    <div class="subsection-label">other links</div>
    <div class="other-links" role="none">
      <router-link 
        v-for="(item, i) in otherLinks" 
        :key="i" 
        :to="item.path"
        role="menuitem" 
        tabindex="-1" 
        class="btn-link"
        @click="closeMenu"
      >
        <i :class="['bx', item.icon, 'icon-20']"></i>
        {{ item.text }}
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isOpen = ref(false)
const breadText = ref(null)
const panelHeader = ref(null)
const showLeftFade = ref(false)
const showRightFade = ref(true)

// Menu links data
const mainLinks = [
  { text: 'Home', icon: 'bx-home', path: '/' },
  { text: 'Blog', icon: 'bx-notepad', path: '/blog' },
  { text: 'Music', icon: 'bx-music', path: '/music' },
  { text: 'Arts', icon: 'bx-palette', path: '/arts' },
  { text: 'Links', icon: 'bx-link', path: '/links' },
  { text: 'About', icon: 'bx-info-circle', path: '/about' },
]

const otherLinks = [
  { text: 'Characters', icon: 'bx-group', path: '/characters' },
]

// Check if current route is 404
const isNotFoundRoute = computed(() => route.name === 'NotFound')

// Generate breadcrumbs hierarchy
const breadcrumbs = computed(() => {
  if (isNotFoundRoute.value) return []

  const crumbs = []
  const matchedRoutes = route.matched.filter(r => r.meta?.breadcrumb)
  
  // Add Home as first crumb (except for 404)
  crumbs.push({
    path: '/',
    title: 'Home'
  })
  
  // Add remaining path segments
  matchedRoutes.forEach(record => {
    if (record.path === '/') return
    
    const title = typeof record.meta.breadcrumb === 'function' 
      ? record.meta.breadcrumb(route) 
      : record.meta.breadcrumb
    
    let path = record.path
    // Replace dynamic params in path
    for (const param in route.params) {
      path = path.replace(`:${param}`, route.params[param])
    }
    
    // Avoid duplicates
    if (!crumbs.some(c => c.path === path)) {
      crumbs.push({
        path,
        title: title || record.name || 'Untitled'
      })
    }
  })
  
  return crumbs
})

// Toggle mobile menu
function toggleMenu() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    setTimeout(() => panelHeader.value?.focus(), 360)
  } else {
    document.querySelector('.menu-toggle')?.focus()
  }
}

// Close mobile menu
function closeMenu() {
  isOpen.value = false
  document.querySelector('.menu-toggle')?.focus()
}

// Handle breadcrumbs scroll position
function checkScrollPosition() {
  if (!breadText.value || isNotFoundRoute.value) return
  const { scrollLeft, scrollWidth, clientWidth } = breadText.value
  showLeftFade.value = scrollLeft > 0
  showRightFade.value = scrollLeft < scrollWidth - clientWidth
}

// Keyboard navigation
function handleKeyDown(e) {
  if (e.key === 'Escape' && isOpen.value) {
    e.preventDefault()
    closeMenu()
  }

  if (e.key === 'Tab' && isOpen.value) {
    const focusable = document.querySelectorAll('.menu-panel .btn-link')
    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }
}

// Lifecycle hooks
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  if (breadText.value) {
    breadText.value.addEventListener('scroll', checkScrollPosition, { passive: true })
    checkScrollPosition()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
  breadText.value?.removeEventListener('scroll', checkScrollPosition)
})

// Watch for route changes
watch(() => route.path, () => {
  setTimeout(checkScrollPosition, 100)
})

// Compute menu icon class
const menuIconClass = computed(() => isOpen.value ? 'bx-x' : 'bx-menu')
</script>

<style scoped>
* {
  box-sizing: border-box;
}
header {
  position: fixed;
  bottom: -1px;
  left: 0;
  width: 100%;
  max-width: 100%;
  background-image: 
    linear-gradient(var(--w5), var(--w5)),
    linear-gradient(var(--header), var(--header)); 
  border-radius: 14px 14px 0 0;
  padding: 12px 16px calc(16px + env(safe-area-inset-bottom)) 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  z-index: 120;
  backdrop-filter: blur(20px);
  /* box-shadow: 0 0 0 11px rgba(255, 255, 255, 0.5),
                0 0 20px rgba(0, 0, 0, 1);  */
}
.nav-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13.25px;
  color: var(--w60);
  font-weight: 500;
  min-width: 0;
  flex: 1;
  margin-left: 4px;
}

.nav-info svg {
  width: 18px;
  height: 18px;
  stroke: var(--w60);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}

.breadcrumbs-container {
  position: relative;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.bread-text {
  white-space: nowrap;
  overflow-x: scroll;
  text-overflow: initial;
  width: 100%;
  font-size: 12px;
  padding: 0 4px;
  color: var(--w60);
  -ms-overflow-style: none;
  scrollbar-width: none;
  touch-action: pan-x;
  -webkit-overflow-scrolling: touch;
}

.bread-text::-webkit-scrollbar {
  display: none;
}

.fade-mask {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 20px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.fade-mask.active {
  opacity: 1;
}

.fade-left {
  left: 0;
  background: linear-gradient(90deg, hsl(5%, 0%, 5%, 0.9) 0%, transparent 100%);
}

.fade-right {
  right: 0;
  background: linear-gradient(270deg, hsl(5%, 0%, 5%, 0.9) 0%, transparent 100%);
}

button.menu-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--w5);
  border: none;
  padding: 9px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: var(--w60);
  user-select: none;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  flex-shrink: 0;
  margin-left: 8px;
}

button.menu-toggle:hover,
button.menu-toggle:focus-visible {
  background: var(--w8);
  color: var(--w);
}

button.menu-toggle svg {
  width: 20px;
  height: 20px;
  stroke: var(--w60);
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

nav.menu-panel {
  position: fixed;
  bottom: calc(4.6rem + env(safe-area-inset-bottom, 0px));
  /* bottom: 4.6rem; */
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  background-image: 
    linear-gradient(var(--w5), var(--w5)),
    linear-gradient(var(--header), var(--header)); 
  border-radius: 12px;
  padding: 1rem 1.2rem 1.7rem 1.2rem;
  width: 94vw;
  max-width: 480px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  z-index: 30;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
}

nav.menu-panel.active {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0);
}

nav.menu-panel > .panel-header {
  font-weight: 900;
  font-size: 20px;
  color: var(--w);
  letter-spacing: -0.04em;
  margin-bottom: 1rem;
  user-select: text;
}

.main-links {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.btn-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  background: var(--w5);
  border-radius: 10px;
  color: var(--w60);
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
  user-select: none;
  border: none;
  width: 100%;
}

.btn-link:hover,
.btn-link:focus-visible {
  background: var(--w8);
  color: var(--w);
  outline: none;
}

.btn-link svg {
  width: 20px;
  height: 20px;
  stroke: var(--w60);
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
  transition: stroke 0.3s ease;
}

.btn-link:hover svg,
.btn-link:focus-visible svg {
  stroke: var(--w);
}

.subsection-label {
  font-weight: 400;
  font-size: 12px;
  color: var(--w60);
  margin: 8px 0;
  text-transform: lowercase;
  user-select: none;
}

.other-links {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  overflow-x: auto;
}

.other-links .btn-link {
  min-width: fit-content;
}

.slash {
  color: var(--w18);
  margin: 0px 3.5px 0px 0px;
}

/* Focus outline for accessibility */
.btn-link:focus-visible,
button.menu-toggle:focus-visible {
  outline: 3px solid #00ff22;
  outline-offset: 2px;
}

@supports (-webkit-touch-callout: none) {
  header {
    transition: transform 0.2s ease;
  }

  body {
    padding-bottom: calc(60px + var(--safe-bottom));
  }
}


</style>