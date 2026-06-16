<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }

  const success = await authStore.login({
    username: username.value,
    password: password.value,
  })

  if (success) {
    router.push('/admin')
  } else {
    error.value = authStore.error || '登录失败'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-6 py-20">
    <div class="blob w-[350px] h-[350px] top-10 -left-40" style="background: #E07A5F; opacity: 0.08;" />
    <div class="blob w-[250px] h-[250px] bottom-10 -right-30" style="background: #8A9A86; opacity: 0.06;" />

    <div class="w-full max-w-sm relative z-10">
      <div class="glass-strong rounded-2xl p-8">
        <!-- 标题 -->
        <div class="text-center mb-8">
          <div
            class="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center"
            style="background: linear-gradient(135deg, #E07A5F, #D06A4F);"
          >
            <span class="text-white text-xl font-bold" style="font-family: var(--font-serif);">M</span>
          </div>
          <h1
            class="text-xl font-bold text-foreground mb-1"
            style="font-family: var(--font-serif);"
          >
            管理员登录
          </h1>
          <p class="text-sm" style="color: #8C7E74;">登录后即可管理博客内容</p>
        </div>

        <!-- 错误 -->
        <Transition name="shake">
          <div
            v-if="error"
            class="mb-5 p-3 rounded-xl text-sm text-center"
            style="background: rgba(196, 69, 62, 0.08); border: 1px solid rgba(196, 69, 62, 0.15); color: #C4453E;"
          >
            {{ error }}
          </div>
        </Transition>

        <!-- 表单 -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              class="input-neu"
              :disabled="authStore.loading"
            />
          </div>

          <div>
            <label class="text-xs font-medium mb-1.5 block" style="color: #8C7E74;">密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="input-neu"
              :disabled="authStore.loading"
            />
          </div>

          <button
            type="submit"
            class="btn-primary w-full mt-2"
            :disabled="authStore.loading"
          >
            <span>{{ authStore.loading ? '登录中...' : '登录' }}</span>
          </button>
        </form>

        <p class="text-xs text-center mt-6" style="color: #BFB3A3;">
          账号: admin / admin123
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shake-enter-active {
  animation: shake 0.4s ease;
}
.shake-leave-active {
  transition: all 0.2s ease;
}
.shake-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}
</style>
