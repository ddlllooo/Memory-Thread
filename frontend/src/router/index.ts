import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Blog from '@/pages/Blog.vue'
import Post from '@/pages/Post.vue'
import About from '@/pages/About.vue'
import Login from '@/pages/Login.vue'
import Admin from '@/pages/Admin.vue'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    return { top: 0, behavior: 'instant' }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/blog',
      name: 'blog',
      component: Blog,
    },
    {
      path: '/post/:id',
      name: 'post',
      component: Post,
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      meta: { requiresAuth: true },
    },
  ],
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = sessionStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
