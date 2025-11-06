<template>
  <div class="user-profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <div class="profile-content">
        <div class="profile-info">
          <el-form :model="userInfo" :rules="infoRules" ref="infoFormRef" label-width="120px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userInfo.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userInfo.email" type="email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item label="角色">
              <el-input v-model="userInfo.roleText" disabled />
            </el-form-item>
            
            <el-form-item label="创建时间">
              <el-input v-model="userInfo.created_at" disabled />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="infoLoading">更新信息</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="password-change">
          <el-divider>修改密码</el-divider>
          
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
            <el-form-item label="原密码" prop="oldPassword">
              <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" show-password />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="passwordLoading">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store/user'
import axios from 'axios'

const userStore = useUserStore()
const infoFormRef = ref(null)
const passwordFormRef = ref(null)
const infoLoading = ref(false)
const passwordLoading = ref(false)

const userInfo = reactive({
  username: '',
  email: '',
  role: '',
  roleText: '',
  created_at: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const infoRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loadUserInfo = async () => {
  try {
    const userData = await userStore.fetchUserInfo()
    
    // 更新用户信息表单
    userInfo.username = userData.user?.username || userStore.user?.username || ''
    userInfo.email = userData.user?.email || userStore.user?.email || ''
    userInfo.role = userData.user?.role || userStore.user?.role || ''
    userInfo.roleText = userInfo.role === 'admin' ? '管理员' : '普通用户'
    userInfo.created_at = userData.user?.created_at || userStore.user?.created_at || ''
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error('获取用户信息失败:', error)
  }
}

const updateProfile = async () => {
  const valid = await infoFormRef.value.validate()
  if (!valid) return
  
  infoLoading.value = true
  
  try {
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    const response = await axios.put('/users/profile', {
      email: userInfo.email
    }, config)
    
    // 更新store中的用户信息
    if (userStore.user) {
      userStore.user.email = userInfo.email
    }
    
    ElMessage.success('用户信息更新成功')
  } catch (error) {
    const errorMsg = error.response?.data?.message || '用户信息更新失败'
    ElMessage.error(errorMsg)
    console.error('更新用户信息失败:', error)
  } finally {
    infoLoading.value = false
  }
}

const changePassword = async () => {
  const valid = await passwordFormRef.value.validate()
  if (!valid) return
  
  passwordLoading.value = true
  
  try {
    const config = {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    }
    
    const response = await axios.put('/api/auth/change-password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    }, config)
    
    ElMessage.success('密码修改成功')
    
    // 重置密码表单
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    passwordFormRef.value.resetFields()
  } catch (error) {
    const errorMsg = error.response?.data?.message || '密码修改失败'
    ElMessage.error(errorMsg)
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    loadUserInfo()
  }
})
</script>

<style scoped>
.user-profile {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  max-width: 800px;
}

.profile-info {
  margin-bottom: 30px;
}

.password-change {
  margin-top: 30px;
}

.el-form-item {
  margin-bottom: 24px;
}
</style>