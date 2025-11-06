import { defineStore } from 'pinia'
import axios from 'axios'

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents: [],
    currentDocument: null,
    categories: [],
    isLoading: false,
    error: null,
    pagination: {
      page: 1,
      per_page: 20,
      total: 0
    }
  }),
  
  actions: {
    async fetchDocuments(params = {}) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get('/documents/', {
          params: { ...this.pagination, ...params }
        })
        
        // 确保documents是数组格式，避免TypeError
        this.documents = Array.isArray(response.data.documents) ? response.data.documents : []
        this.pagination = {
          page: response.data.page,
          per_page: response.data.per_page,
          total: response.data.total
        }
      } catch (error) {
        this.error = error.response?.data?.message || '获取文档列表失败'
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchDocument(id) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get(`/documents/${id}`)
        this.currentDocument = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || '获取文档详情失败'
        return null
      } finally {
        this.isLoading = false
      }
    },
    
    async uploadDocument(formData) {
      this.isLoading = true
      this.error = null
      
      try {
        // 确保有Authorization头
        const token = localStorage.getItem('token')
        const response = await axios.post('/documents/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': token ? `Bearer ${token}` : ''
          }
        })
        
        await this.fetchDocuments()
        return true
      } catch (error) {
        // 更详细的错误处理
        if (error.response) {
          // 服务器返回错误响应
          this.error = error.response.data?.message || `文档上传失败: HTTP ${error.response.status}`
        } else if (error.request) {
          // 请求发出但没有收到响应
          this.error = '网络错误，无法连接到服务器'
        } else {
          // 请求配置出错
          this.error = `请求错误: ${error.message}`
        }
        console.error('上传错误详情:', error)
        return false
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchCategories() {
      try {
        const response = await axios.get('/categories/')
        // 确保categories是数组格式，避免TypeError
        this.categories = Array.isArray(response.data.categories) ? response.data.categories : []
      } catch (error) {
        this.error = error.response?.data?.message || '获取分类列表失败'
        // 出错时确保categories是一个空数组
        this.categories = []
      }
    },
    
    async deleteDocument(id) {
      this.isLoading = true
      
      try {
        console.log('准备删除文档，ID:', id)
        console.log('当前token存在:', !!localStorage.getItem('token'))
        
        // 确保API路径正确
        const response = await axios.delete(`/documents/${id}`)
        console.log('删除成功响应:', response)
        
        await this.fetchDocuments()
        return true
      } catch (error) {
        console.error('删除文档时出错详情:', error)
        
        // 更详细的错误处理
        if (error.response) {
          this.error = error.response.data?.message || `删除文档失败: HTTP ${error.response.status}`
          console.error('HTTP错误状态:', error.response.status)
          console.error('错误响应数据:', error.response.data)
        } else if (error.request) {
          this.error = '网络错误，无法连接到服务器'
          console.error('请求已发送但未收到响应')
        } else {
          this.error = `请求错误: ${error.message}`
          console.error('请求配置错误:', error.message)
        }
        
        return false
      } finally {
        this.isLoading = false
      }
    }
  }
})