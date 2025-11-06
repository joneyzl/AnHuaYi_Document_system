<template>
  <div class="document-upload">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文档上传</span>
        </div>
      </template>
      
      <el-form :model="uploadForm" :rules="rules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        
        <el-form-item label="文档分类" prop="category_id">
          <el-select v-model="uploadForm.category_id" placeholder="请选择文档分类">
            <el-option
              v-for="category in documentStore.categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="文档描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入文档描述"
          />
        </el-form-item>
        
        <el-form-item label="选择文件">
          <el-upload
            class="upload-demo"
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :file-list="fileList"
            multiple="false"
          >
            <el-icon class="el-icon--upload"><EpUploadFilled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">
                支持上传的文件格式：PDF, Word, Excel, PowerPoint, 文本文件等
              </div>
            </template>
          </el-upload>
          <!-- 文件大小显示 -->
          <div v-if="fileSize !== null" class="file-size-info">
            文件大小：{{ formatFileSize(fileSize) }}
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="documentStore.isLoading">
            确认上传
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../store/document'

const router = useRouter()
const documentStore = useDocumentStore()
const uploadFormRef = ref(null)
const fileList = ref([])
const currentFile = ref(null)
const fileSize = ref(null)

const uploadForm = reactive({
  title: '',
  category_id: '',
  description: ''
})

const rules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择文档分类', trigger: 'change' }
  ]
}

const handleFileChange = (file, fileList) => {
  currentFile.value = file.raw
  // 直接从原生File对象获取文件大小
  if (file.raw && typeof file.raw.size === 'number') {
    fileSize.value = file.raw.size
  } else if (typeof file.size === 'number') {
    // 备用方式
    fileSize.value = file.size
  } else {
    fileSize.value = 0
  }
  // 自动提取文件名（不含扩展名）作为文档标题
  if (file.name) {
    // 移除文件扩展名
    const fileNameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.')) || file.name
    // 设置为文档标题，仅当标题为空时才自动填充
    if (!uploadForm.title) {
      uploadForm.title = fileNameWithoutExt
    }
  }
}

const handleSubmit = async () => {
  const valid = await uploadFormRef.value.validate()
  if (!valid) return
  
  if (!currentFile.value) {
    ElMessage.error('请选择要上传的文件')
    return
  }
  
  const formData = new FormData()
  formData.append('title', uploadForm.title)
  formData.append('category_id', uploadForm.category_id)
  formData.append('description', uploadForm.description)
  formData.append('file', currentFile.value)
  
  const success = await documentStore.uploadDocument(formData)
  if (success) {
    ElMessage.success('文档上传成功')
    router.push('/documents')
  }
}

const resetForm = () => {
  uploadFormRef.value.resetFields()
  fileList.value = []
  currentFile.value = null
  fileSize.value = null
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(async () => {
  await documentStore.fetchCategories()
})
</script>

<style scoped>
.document-upload {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-size-info {
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.upload-demo {
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 20px;
}
</style>