import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/projects' },
  { path: '/login', component: () => import('../pages/LoginPage.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('../pages/RegisterPage.vue'), meta: { guest: true } },
  { path: '/pending', component: () => import('../pages/PendingPage.vue') },
  { path: '/projects', component: () => import('../pages/ProjectsPage.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id', component: () => import('../pages/ProjectPage.vue'), meta: { requiresAuth: true } },
  { path: '/letters/new', component: () => import('../pages/LetterEditorPage.vue'), meta: { requiresAuth: true } },
  { path: '/letters/:id/edit', component: () => import('../pages/LetterEditorPage.vue'), meta: { requiresAuth: true } },
  { path: '/profile', component: () => import('../pages/ProfilePage.vue'), meta: { requiresAuth: true } },
  { path: '/settings', component: () => import('../pages/SettingsPage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/settings/template/:type', component: () => import('../pages/TemplateEditorPage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (auth.token && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.guest && auth.isLoggedIn) {
    return '/projects'
  }

  if (to.meta.requiresAuth) {
    if (!auth.isLoggedIn) return '/login'
    if (!auth.isApproved) return '/pending'
    if (to.meta.requiresAdmin && !auth.isAdmin) return '/projects'
  }
})

export default router
