<template>
  <div class="document-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文档列表</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索文档标题"
            prefix-icon="el-icon-search"
            style="width: 300px;"
            @input="handleSearch"
          />
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="categoryFilter" placeholder="选择分类" @change="handleFilter">
          <el-option label="全部" value="" />
          <el-option
            v-for="category in documentStore.categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
        
        <el-button type="primary" @click="$router.push('/upload')">
            <el-icon><EpUpload /></el-icon>
            上传文档
        </el-button>
      </div>
      
      <el-table
        v-loading="documentStore.isLoading"
        :data="documentStore.documents"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="文档标题">
          <template #default="scope">
            <a href="javascript:void(0)" @click="previewDocument(scope.row)">
              {{ scope.row.title }}
            </a>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" />
        <el-table-column prop="file_size" label="文件大小" width="100">
          <template #default="scope">
            {{ formatFileSize(scope.row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="username" label="创建者" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="downloadDocument(scope.row)">
                <el-icon><EpDownload /></el-icon>
                下载
              </el-button>
              <el-button type="danger" size="small" @click="deleteDocument(scope.row.id)" v-if="userStore.isAdmin">
                <el-icon><EpDelete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="documentStore.pagination.page"
          v-model:page-size="documentStore.pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="documentStore.pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../store/document'
import { useUserStore } from '../store/user'

const documentStore = useDocumentStore()
const userStore = useUserStore()
const router = useRouter()
const searchQuery = ref('')
const categoryFilter = ref('')
const selectedRows = ref([])

const handleSearch = () => {
  loadDocuments()
}

const handleFilter = () => {
  loadDocuments()
}

const loadDocuments = () => {
  const params = {}
  if (searchQuery.value) {
    params.title = searchQuery.value
  }
  if (categoryFilter.value) {
    params.category_id = categoryFilter.value
  }
  documentStore.fetchDocuments(params)
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleSizeChange = (size) => {
  documentStore.pagination.per_page = size
  loadDocuments()
}

const handleCurrentChange = (current) => {
  documentStore.pagination.page = current
  loadDocuments()
}

const previewDocument = async (document) => {
  // 跳转到文档预览页面
  router.push(`/document/${document.id}/preview`)
}

const downloadDocument = (document) => {
  // 实现文档下载功能
  window.open(`http://192.168.100.196:5000/documents/download/${document.id}`)
}

const deleteDocument = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个文档吗？此操作不可撤销。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const success = await documentStore.deleteDocument(id)
    if (success) {
      ElMessage.success('文档删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(async () => {
  await documentStore.fetchCategories()
  await documentStore.fetchDocuments()
})
</script>

<style scoped>
.document-list {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 操作按钮样式 - 调整对齐和间距 */
.operation-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.operation-buttons .el-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0;
}
</style>