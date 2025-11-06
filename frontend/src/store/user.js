import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isLoading: false,
    error: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },
  
  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.post('/auth/login', {
          username,
          password
        })
        
        this.token = response.data.access_token
        // 从API响应中获取用户信息
        this.user = {
          id: response.data.user?.id,
          username: response.data.user?.username,
          role: response.data.user?.role || 'user',
          email: response.data.user?.email,
          ...response.data.user
        }
        
        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return true
      } catch (error) {
        this.error = error.response?.data?.message || '登录失败，请检查用户名和密码'
        return false
      } finally {
        this.isLoading = false
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    
    async fetchUserInfo() {
      if (!this.token) return Promise.resolve(null)
      
      try {
        const response = await axios.get('/users/profile')
        // 从API响应中获取用户信息
        const userData = response.data.user || response.data
        this.user = {
          id: userData.id,
          username: userData.username,
          role: userData.role || 'user',
          email: userData.email,
          ...userData
        }
        return response.data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        throw error // 抛出错误，让调用方能够捕获
      }
    }
  }
})