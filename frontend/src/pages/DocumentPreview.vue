<template>
  <div class="document-preview">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ documentTitle }}</span>
          <el-button type="danger" @click="handleClose">关闭预览</el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-loading :fullscreen="false" text="正在加载文档内容..." />
      </div>
      
      <div v-else-if="error" class="error-container">
        <el-alert
          :title="error"
          type="error"
          show-icon
          description="请尝试下载文档查看或联系管理员"
        />
        <el-button type="primary" @click="downloadDocument" style="margin-top: 20px;">
          <el-icon><EpDownload /></el-icon>
          下载文档
        </el-button>
      </div>
      
      <div v-else>
        <!-- 文本文件预览 -->
        <div v-if="fileType === 'text'" class="text-preview">
          <el-scrollbar height="600px">
            <pre>{{ documentContent }}</pre>
          </el-scrollbar>
        </div>
        
        <!-- Markdown文件预览 -->
        <div v-else-if="fileType === 'markdown'" class="markdown-preview">
          <el-scrollbar height="600px">
            <div v-html="renderedMarkdown"></div>
          </el-scrollbar>
        </div>
        
        <!-- HTML文件预览 -->
        <div v-else-if="fileType === 'html'" class="html-preview">
          <el-scrollbar height="600px">
            <div v-html="documentContent"></div>
          </el-scrollbar>
        </div>
        
        <!-- 图片预览 -->
        <div v-else-if="fileType === 'image'" class="image-preview">
          <el-dialog
            v-model="dialogVisible"
            title="图片预览"
            width="80%"
            append-to-body
          >
            <img :src="previewImageUrl" class="dialog-image" />
          </el-dialog>
          
          <div class="image-container">
            <img :src="previewImageUrl" @click="dialogVisible = true" class="preview-img" />
            <el-button type="primary" @click="dialogVisible = true" style="margin-top: 10px;">
              查看大图
            </el-button>
          </div>
        </div>
        
        <!-- 需要下载的文件类型 -->
        <div v-else-if="needsDownload" class="download-required">
          <el-empty description="该文件类型不支持在线预览，请下载后查看">
            <el-button type="primary" @click="downloadDocument">
              <el-icon><EpDownload /></el-icon>
              下载文档
            </el-button>
          </el-empty>
        </div>
        
        <!-- PDF预览 (使用Blob和iframe) -->
        <div v-else-if="fileType === 'pdf'" class="pdf-preview">
          <iframe :src="pdfBlobUrl" width="100%" height="600px" frameborder="0"></iframe>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(true)
const error = ref('')
const documentContent = ref('')
const documentTitle = ref('正在加载...')
const fileExtension = ref('')
const needsDownload = ref(false)
const previewUrl = ref('')
const documentId = computed(() => route.params.id)
const dialogVisible = ref(false)
const pdfBlobUrl = ref('')

// 计算文件类型
const fileType = computed(() => {
  const ext = fileExtension.value.toLowerCase()
  if (['.txt', '.log', '.docx'].includes(ext)) return 'text'
  if (['.md'].includes(ext)) return 'markdown'
  if (['.html', '.htm', '.xml'].includes(ext)) return 'html'
  if (['.pdf'].includes(ext)) return 'pdf'
  if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(ext)) return 'image'
  return 'other'
})

// 渲染markdown
const renderedMarkdown = computed(() => {
  if (fileType.value === 'markdown' && documentContent.value) {
    return marked(documentContent.value)
  }
  return ''
})

// PDF预览URL
const pdfViewerUrl = computed(() => {
  if (fileType.value === 'pdf') {
    // 处理PDF预览URL，确保包含API基础路径和认证信息
    const baseUrl = axios.defaults.baseURL || ''
    let path = previewUrl.value || `/documents/${documentId.value}/download`
    const token = localStorage.getItem('token') || ''
    
    // 如果路径已经是完整URL，则直接返回
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path
    }
    
    // 处理路径，避免重复的/api前缀
  // 移除路径开头的/api如果baseUrl已经包含/api
  if (baseUrl.includes('/api') && path.startsWith('/api')) {
    path = path.substring(4) // 移除开头的/api
  }

  // 构建完整URL，确保路径格式正确
  const fullUrl = baseUrl.endsWith('/') && path.startsWith('/') 
    ? `${baseUrl.slice(0, -1)}${path}`
    : `${baseUrl}${path}`

  // 对于PDF预览，我们将在组件中处理认证头，而不是作为查询参数
  return fullUrl
  }
  return ''
})

// 图片预览URL
const previewImageUrl = computed(() => {
  if (fileType.value === 'image') {
    // 构建完整的图片URL，确保包含API基础路径和认证
    const baseUrl = axios.defaults.baseURL || ''
    let path = previewUrl.value || `/documents/${documentId.value}/download`
    const token = localStorage.getItem('token') || ''
    
    // 如果路径已经是完整URL，则直接返回
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path
    }
    
    // 处理路径，避免重复的/api前缀
    // 移除路径开头的/api如果baseUrl已经包含/api
    if (baseUrl.includes('/api') && path.startsWith('/api')) {
      path = path.substring(4) // 移除开头的/api
    }
    
    // 构建完整URL，确保路径格式正确
    const fullUrl = baseUrl.endsWith('/') && path.startsWith('/') 
      ? `${baseUrl.slice(0, -1)}${path}`
      : `${baseUrl}${path}`
    
    // 添加token作为查询参数，确保认证
    return fullUrl + (fullUrl.includes('?') ? '&' : '?') + `token=${encodeURIComponent(token)}`
  }
  return ''
})

// 加载文档内容
const loadDocumentPreview = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    // 使用正确的路径，避免重复的/api前缀
    const response = await axios.get(`/documents/${documentId.value}/preview`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    
    const data = response.data
    
    // 处理PDF文件
    if (data.is_pdf) {
      documentContent.value = ''
      fileExtension.value = data.file_extension || '.pdf'
      documentTitle.value = data.file_name || `PDF文档预览 - ${documentId.value}`
      previewUrl.value = data.preview_url || ''
      needsDownload.value = false
      
      // 加载PDF内容并设置blob URL
      try {
        const token = localStorage.getItem('token')
        
        // 构建完整的PDF URL
        const baseUrl = axios.defaults.baseURL || ''
        let path = previewUrl.value || `/documents/${documentId.value}/download`
        
        // 如果路径已经是完整URL，则直接使用
        let fullUrl = path
        if (!path.startsWith('http://') && !path.startsWith('https://')) {
          // 处理路径，避免重复的/api前缀
          if (baseUrl.includes('/api') && path.startsWith('/api')) {
            path = path.substring(4) // 移除开头的/api
          }
          
          // 构建完整URL，确保路径格式正确
          fullUrl = baseUrl.endsWith('/') && path.startsWith('/') 
            ? `${baseUrl.slice(0, -1)}${path}`
            : `${baseUrl}${path}`
        }
        
        const response = await fetch(fullUrl, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : ''
          }
        })
        
        if (!response.ok) {
          throw new Error(`加载PDF失败: ${response.status}`)
        }
        
        const blob = await response.blob()
        // 先释放旧的blob URL，避免内存泄漏
        if (pdfBlobUrl.value) {
          window.URL.revokeObjectURL(pdfBlobUrl.value)
        }
        // 创建新的blob URL
        pdfBlobUrl.value = window.URL.createObjectURL(blob)
      } catch (err) {
        console.error('加载PDF失败:', err)
        error.value = '加载PDF文档失败，请尝试下载查看'
      }
    } else if (data.is_image) {
      // 处理图片类型
      documentContent.value = '' // 清空内容，使用previewUrl
      fileExtension.value = data.file_extension || ''
      documentTitle.value = data.file_name || `文档预览 - ${documentId.value}`
      previewUrl.value = data.preview_url || ''
      needsDownload.value = false
    } else if (data.content) {
      documentContent.value = data.content
      fileExtension.value = data.file_extension || ''
      documentTitle.value = data.file_name || `文档预览 - ${documentId.value}`
    } else if (data.needs_download) {
      needsDownload.value = true
      fileExtension.value = data.file_extension || ''
      documentTitle.value = data.file_name || `文档预览 - ${documentId.value}`
      previewUrl.value = data.preview_url || ''
    }
  } catch (err) {
    error.value = err.response?.data?.message || '加载文档失败'
    console.error('预览文档失败:', err)
  } finally {
    loading.value = false
  }
}

// 下载文档
const downloadDocument = () => {
  const token = localStorage.getItem('token')
  
  // 对于需要认证的下载，使用fetch和blob方式
  fetch(`/documents/${documentId.value}/download`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
  .then(response => {
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    // 从响应头获取文件名，如果没有则使用documentTitle
    let filename = documentTitle.value
    const contentDisposition = response.headers.get('content-disposition')
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/)
      if (match && match[1]) {
        filename = match[1]
      }
    }
    
    return { blob: response.blob(), filename }
  })
  .then(({ blob, filename }) => {
    blob.then(blobData => {
      const url = window.URL.createObjectURL(blobData)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      
      // 使用setTimeout确保链接被正确点击
      setTimeout(() => {
        link.click()
        // 延迟撤销URL以确保下载完成
        setTimeout(() => {
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }, 100)
      }, 0)
    })
  })
  .catch(err => {
    ElMessage.error('下载文档失败')
    console.error('下载失败:', err)
  })
}

// 关闭预览
const handleClose = () => {
  router.back()
}

// 组件挂载时加载文档
onMounted(() => {
  loadDocumentPreview()
})
</script>

<style scoped>
.document-preview {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container,
.error-container,
.download-required {
  padding: 40px;
  text-align: center;
}

.text-preview pre {
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin: 0;
}

.markdown-preview {
  padding: 20px;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3) {
  margin-top: 20px;
  margin-bottom: 10px;
}

.markdown-preview :deep(p) {
  margin-bottom: 10px;
}

.markdown-preview :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
}

.markdown-preview :deep(pre) {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.html-preview :deep(*) {
  max-width: 100%;
}

.pdf-preview {
  padding: 20px 0;
}
  /* 图片预览样式 */
  .image-preview {
    padding: 20px;
    text-align: center;
  }
  
  .image-container {
    display: inline-block;
  }
  
  .preview-img {
    max-width: 100%;
    max-height: 500px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: transform 0.2s;
  }
  
  .preview-img:hover {
    transform: scale(1.02);
  }
  
  .dialog-image {
    width: 100%;
    max-height: 80vh;
    object-fit: contain;
  }
</style>