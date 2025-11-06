# 文档管理系统 - 前端

这是文档管理系统的前端部分，基于Vue 3 + Vite开发，使用Element Plus作为UI组件库。

## 系统功能

- 用户认证（登录/注销）
- 仪表盘数据统计
- 文档管理（上传、下载、删除、搜索）
- 分类管理（增删改查）
- 用户管理（增删改查）

## 技术栈

- Vue 3
- Vite
- Element Plus
- Vue Router
- Pinia
- Axios

## 启动服务方式

### 1. 安装依赖

```bash
# 进入前端目录
cd document_system/frontend

# 安装依赖
npm install
```

### 2. 开发环境启动

```bash
# 启动开发服务器
npm run dev
```

开发服务器启动后，可以通过以下地址访问：
- 前端应用：http://localhost:4173

### 4. 预览生产版本

```bash
# 构建并预览生产版本
npm run build; npm run preview
```

预览服务器启动后，可以通过以下地址访问：
- 预览地址：http://localhost:4173

### 3. 构建生产版本

```bash
# 构建生产版本
npm run build
```

构建后的文件会生成在 `dist/` 目录下，可以部署到任何静态文件服务器。

## 后端服务配置

前端默认连接的后端API地址为：http://192.168.1.95:5000/api

### IP地址修改说明

项目中需要修改IP地址的位置共有1处：

1. **前端API基础配置**：修改 `src/main.js` 中的 `axios.defaults.baseURL` 配置
   - 路径：`src/main.js`
   - 行号：约第28行
   - 配置项：`axios.defaults.baseURL`

### 修改步骤

1. 找到并修改上述文件中的IP地址配置
2. 重启前端服务以应用新的配置
3. 确保后端服务运行在对应的IP地址和端口上

当前后端服务IP地址：192.168.1.95，端口：5000

## 访问路径

系统主要页面访问路径：

**开发环境（npm run dev）：**
- 登录页面：http://localhost:4173/
- 仪表盘：http://localhost:4173/dashboard
- 文档管理：http://localhost:4173/documents
- 文档上传：http://localhost:4173/upload
- 分类管理：http://localhost:4173/categories
- 用户管理：http://localhost:4173/users (需要管理员权限)

**预览环境（npm run preview）：**
- 登录页面：http://localhost:4173/
- 仪表盘：http://localhost:4173/dashboard
- 文档管理：http://localhost:4173/documents
- 文档上传：http://localhost:4173/upload
- 分类管理：http://localhost:4173/categories
- 用户管理：http://localhost:4173/users (需要管理员权限)

## 注意事项

1. 确保后端服务正在运行，并且API地址配置正确
2. 首次登录可以使用管理员账号（默认管理员账号需要在后端数据库中设置）
3. 开发环境下支持热重载，修改代码后自动刷新页面

## 许可证

MIT
