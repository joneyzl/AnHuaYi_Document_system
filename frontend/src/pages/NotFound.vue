<template>
  <div class="not-found">
    <div class="not-found-content">
      <el-icon class="error-icon"><EpWarning /></el-icon>
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goBack">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
  background-color: #f0f2f5;
}

.not-found-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 60px;
  color: #f56c6c;
  margin-bottom: 20px;
}

h1 {
  font-size: 48px;
  color: #606266;
  margin-bottom: 10px;
}

p {
  font-size: 16px;
  color: #909399;
  margin-bottom: 30px;
}
</style>