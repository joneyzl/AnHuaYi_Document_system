<template>
  <el-container class="main-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h3>安华易文档管理系统</h3>
      </div>
      <el-menu
        :default-active="activePath"
        class="side-menu"
        router
      >
        <el-menu-item index="/">
          <el-icon><EpHome /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><EpDocument /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-menu-item index="/upload">
          <el-icon><EpUpload /></el-icon>
          <span>文档上传</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><EpMenu /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="userStore.isAdmin">
          <el-icon><EpUser /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown>
            <el-button link>
              <img :src="'/anhuayi_logo.svg'" alt="LOGO" style="width: 124px; height: 24px; margin-right: 8px; vertical-align: middle;" />
              <el-icon><EpUser /></el-icon>
              <span>{{ userStore.user?.username || '未登录' }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="navigateToProfile">个人信息</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
      
      <el-footer class="footer">
        <!-- <div class="footer-logo">
          <img src="/beian.svg" alt="备案号" style="max-width: 50px; height: auto;" />
        </div> -->
         <span style="font-size: 12px;">© Copyright 2025 ANHUAYI. 天津安华易科技发展有限公司 津ICP备11001704号-1  津公网安备 12019202000105号</span>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activePath = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const navigateToProfile = () => {
  router.push('/profile')
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 确保在获取用户信息失败时清除登录状态
      userStore.logout()
    }
  }
})
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  color: white;
  padding-top: 0;
}

.logo {
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid #1890ff;
  background-color: #001529;
}

.logo h3 {
  margin: 0;
  color: white;
}

.side-menu {
  height: calc(100vh - 80px);
  background-color: #001529;
}

.side-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

.side-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background-color: #1890ff;
}

.header {
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow: auto;
  flex: 1;
}

.footer {
  background-color: white;
  padding: 20px;
  text-align: center;
  border-top: 1px solid #e0e0e0;
}

.footer-logo {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>