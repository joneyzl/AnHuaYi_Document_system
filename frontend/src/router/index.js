import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../pages/Dashboard.vue')
      },
      {
        path: 'documents',
        name: 'DocumentList',
        component: () => import('../pages/DocumentList.vue')
      },
      {
        path: 'upload',
        name: 'DocumentUpload',
        component: () => import('../pages/DocumentUpload.vue')
      },
      {
        path: 'categories',
        name: 'CategoryList',
        component: () => import('../pages/CategoryList.vue')
      },
      {        path: 'users',        name: 'UserList',        component: () => import('../pages/UserList.vue'),        meta: { requiresAdmin: true }      },      {        path: 'profile',        name: 'UserProfile',        component: () => import('../pages/UserProfile.vue')      },      {        path: 'document/:id/preview',        name: 'DocumentPreview',        component: () => import('../pages/DocumentPreview.vue')      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../pages/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return next('/login')
  }
  
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    return next('/')
  }
  
  next()
})

export default router