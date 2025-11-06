<template>
  <div class="dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统概览</span>
        </div>
      </template>
      
      <div class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ totalDocuments }}</div>
            <div class="stat-label">总文档数</div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ totalCategories }}</div>
            <div class="stat-label">分类数</div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ totalUsers }}</div>
            <div class="stat-label">用户数</div>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <el-card class="recent-documents" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近文档</span>
        </div>
      </template>
      
      <el-table :data="recentDocuments" style="width: 100%">
        <el-table-column prop="title" label="文档标题" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button link size="small">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const totalDocuments = ref(0)
const totalCategories = ref(0)
const totalUsers = ref(0)
const recentDocuments = ref([])

// 获取系统统计信息
const fetchStatistics = async () => {
  try {
    const response = await axios.get('/overview/statistics')
    totalDocuments.value = response.data.total_documents
    totalCategories.value = response.data.total_categories
    // 非管理员可能没有用户数权限
    totalUsers.value = response.data.total_users !== null ? response.data.total_users : '无权限查看'
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取系统概览数据失败')
  }
}

// 获取最近文档
const fetchRecentDocuments = async () => {
  try {
    const response = await axios.get('/overview/recent-documents?limit=5')
    // 确保recentDocuments是数组格式，避免TypeError
        recentDocuments.value = Array.isArray(response.data.documents) ? response.data.documents : []
  } catch (error) {
    console.error('获取最近文档失败:', error)
    ElMessage.error('获取最近文档失败')
  }
}

onMounted(() => {
  // 从API获取真实数据
  fetchStatistics()
  fetchRecentDocuments()
})
</script>

<style scoped>
.dashboard {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>