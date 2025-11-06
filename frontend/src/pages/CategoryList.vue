<template>
  <div class="category-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><EpPlus /></el-icon>
            添加分类
          </el-button>
        </div>
      </template>
      
      <el-table
        v-loading="isLoading"
        :data="categories"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="description" label="分类描述" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="editCategory(scope.row)">
                <el-icon><EpEdit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteCategory(scope.row.id)" v-if="userStore.isAdmin">
                <el-icon><EpDelete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" v-if="categories.length > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="categoryForm" :rules="rules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="resetForm">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="dialogLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../store/user'

const categories = ref([])
const isLoading = ref(false)
const showAddDialog = ref(false)
const categoryFormRef = ref(null)
const selectedRows = ref([])
const editingId = ref(null)
const dialogLoading = ref(false)
const userStore = useUserStore()

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const categoryForm = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '分类描述不能超过 200 个字符', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => {
  return editingId.value ? '编辑分类' : '添加分类'
})

const fetchCategories = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/categories/')
    // 正确处理API返回的数据格式
    categories.value = response.data.categories || []
    pagination.total = categories.value.length
  } catch (error) {
    ElMessage.error('获取分类列表失败')
    console.error('获取分类列表失败:', error)
    // 出错时确保categories是一个空数组
    categories.value = []
  } finally {
    isLoading.value = false
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  fetchCategories()
}

const handleCurrentChange = (current) => {
  pagination.page = current
  fetchCategories()
}

const resetForm = () => {
  categoryFormRef.value?.resetFields()
  categoryForm.name = ''
  categoryForm.description = ''
  editingId.value = null
  showAddDialog.value = false
}

const editCategory = (category) => {
  editingId.value = category.id
  categoryForm.name = category.name
  categoryForm.description = category.description
  showAddDialog.value = true
}

const submitForm = async () => {
  const valid = await categoryFormRef.value.validate()
  if (!valid) return
  
  dialogLoading.value = true
  
  try {
    if (editingId.value) {
      // 编辑分类
      await axios.put(`/categories/${editingId.value}`, categoryForm)
      ElMessage.success('分类更新成功')
    } else {
      // 添加分类
      await axios.post('/categories/', categoryForm)
      ElMessage.success('分类添加成功')
    }
    
    await fetchCategories()
    resetForm()
  } catch (error) {
    ElMessage.error(editingId.value ? '分类更新失败' : '分类添加失败')
    console.error('操作失败:', error)
  } finally {
    dialogLoading.value = false
  }
}

const deleteCategory = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分类吗？删除后将无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/categories/${id}`)
    ElMessage.success('分类删除成功')
    await fetchCategories()
  } catch {
    // 用户取消删除
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-list {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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