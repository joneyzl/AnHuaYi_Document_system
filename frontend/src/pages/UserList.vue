<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog = true">
              <el-icon><EpPlus /></el-icon>
              添加用户
          </el-button>
        </div>
      </template>
      
      <el-table
        v-loading="isLoading"
        :data="users"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'primary' : 'success'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              @change="updateUserStatus(scope.row)"
              :disabled="scope.row.id === currentUserId"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="editUser(scope.row)">
                <el-icon><EpEdit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteUser(scope.row.id)"
                :disabled="scope.row.id === currentUserId"
              >
                <el-icon><EpDelete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="editingId" />
        </el-form-item>
        
        <el-form-item label="密码" :required="!editingId">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :disabled="editingId"
          />
          <div class="el-form-item__error" v-if="!editingId && !userForm.password">
            请输入密码
          </div>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="userForm.status" />
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
import { useUserStore } from '../store/user'
import axios from 'axios'

const userStore = useUserStore()
const users = ref([])
const isLoading = ref(false)
const showAddDialog = ref(false)
const userFormRef = ref(null)
const selectedRows = ref([])
const editingId = ref(null)
const dialogLoading = ref(false)
const currentUserId = ref(1) // 假设当前登录用户ID为1

const userForm = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user',
  status: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const dialogTitle = computed(() => {
  return editingId.value ? '编辑用户' : '添加用户'
})

const fetchUsers = async () => {
  isLoading.value = true
  try {
    // 确保axios请求头包含token
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    const response = await axios.get('/users/', config)
    // 确保users是数组格式，避免TypeError: data2 is not iterable错误
    // 从响应中获取users数组，根据后端API结构
    users.value = Array.isArray(response.data.users) ? response.data.users : []
  } catch (error) {
    // 处理认证错误
    if (error.response?.status === 401) {
      ElMessage.error('认证过期，请重新登录')
      userStore.logout()
    } else {
      ElMessage.error('获取用户列表失败')
    }
    console.error('获取用户列表失败:', error)
    console.error('错误响应:', error.response?.data)
    // 出错时确保users是一个空数组
    users.value = []
  } finally {
    isLoading.value = false
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const resetForm = () => {
  userFormRef.value?.resetFields()
  userForm.username = ''
  userForm.password = ''
  userForm.email = ''
  userForm.role = 'user'
  userForm.status = true
  editingId.value = null
  showAddDialog.value = false
}

const editUser = (user) => {
  editingId.value = user.id
  userForm.username = user.username
  userForm.email = user.email
  userForm.role = user.role
  userForm.status = user.status
  userForm.password = '' // 编辑时不显示密码
  showAddDialog.value = true
}

const submitForm = async () => {
  // 检查是否已登录
  if (!userStore.isLoggedIn) {
    ElMessage.error('请先登录')
    return
  }
  
  const valid = await userFormRef.value.validate()
  if (!valid) return
  
  if (!editingId.value && !userForm.password) {
    ElMessage.error('请输入密码')
    return
  }
  
  dialogLoading.value = true
  
  try {
    // 确保axios请求头包含token
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    if (editingId.value) {
      // 编辑用户，不更新密码
      const { password, role, ...updateData } = userForm
      // 将前端的role转换为后端需要的role_id
      updateData.role_id = role === 'admin' ? 1 : 2 // 假设admin角色ID为1，user角色ID为2
      // 确保API路径正确，避免重复的/api前缀
      const response = await axios.put(`/users/${editingId.value}`, updateData, config)
      console.log('用户更新响应:', response)
      ElMessage.success('用户更新成功')
    } else {
      // 添加用户 - 注意：后端需要role_id而不是role
      const userData = {
        ...userForm,
        // 将前端的role转换为后端需要的role_id
        role_id: userForm.role === 'admin' ? 1 : 2 // 假设admin角色ID为1，user角色ID为2
      }
      // 删除原始的role字段
      delete userData.role
      
      // 确保API路径正确，避免重复的/api前缀
      const response = await axios.post('/users/', userData, config)
      console.log('用户添加响应:', response)
      ElMessage.success('用户添加成功')
    }
    
    await fetchUsers()
    resetForm()
  } catch (error) {
    // 更详细的错误信息
    const errorMsg = error.response?.data?.message || error.message || '未知错误'
    
    // 处理认证错误
    if (error.response?.status === 401) {
      ElMessage.error('认证过期，请重新登录')
      userStore.logout()
    } else {
      ElMessage.error(`${editingId.value ? '用户更新失败' : '用户添加失败'}: ${errorMsg}`)
    }
    
    console.error('操作失败详情:', error)
    console.error('错误响应:', error.response?.data)
  } finally {
    dialogLoading.value = false
  }
}

const updateUserStatus = async (user) => {
  try {
    // 确保axios请求头包含token
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    // 确保API路径正确，避免重复的/api前缀
    const response = await axios.put(`/users/${user.id}/status`, {
      status: user.status
    }, config)
    console.log('用户状态更新响应:', response)
    ElMessage.success('用户状态更新成功')
  } catch (error) {
    user.status = !user.status // 恢复原状态
    // 处理认证错误
    if (error.response?.status === 401) {
      ElMessage.error('认证过期，请重新登录')
      userStore.logout()
    } else {
      // 更详细的错误信息
      const errorMsg = error.response?.data?.message || error.message || '未知错误'
      ElMessage.error(`用户状态更新失败: ${errorMsg}`)
    }
    console.error('更新状态失败详情:', error)
    console.error('错误响应:', error.response?.data)
  }
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个用户吗？删除后将无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 确保axios请求头包含token
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    // 确保API路径正确，避免重复的/api前缀
    const response = await axios.delete(`/users/${id}`, config)
    console.log('用户删除响应:', response)
    ElMessage.success('用户删除成功')
    await fetchUsers()
  } catch (error) {
    // 检查是否是用户取消确认对话框
    if (error.name !== 'ElMessageBoxCancel') {
      // 处理认证错误
      if (error.response?.status === 401) {
        ElMessage.error('认证过期，请重新登录')
        userStore.logout()
      } else {
        // 更详细的错误信息
        const errorMsg = error.response?.data?.message || error.message || '未知错误'
        ElMessage.error(`用户删除失败: ${errorMsg}`)
      }
      console.error('删除用户失败详情:', error)
      console.error('错误响应:', error.response?.data)
    }
    // 否则忽略，因为这是用户取消操作
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-list {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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