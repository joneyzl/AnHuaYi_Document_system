# 文档管理系统 - 后端

这是文档管理系统的后端部分，基于Flask开发，提供RESTful API接口供前端调用。

## 系统功能

- 用户认证与授权（JWT）
- 文档管理（上传、下载、删除、查询）
- 分类管理（增删改查）
- 用户管理（增删改查）
- 文件存储管理

## 技术栈

- Python 3.8+
- Flask 2.0+
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- SQLite（生产环境可切换为MySQL/PostgreSQL）

## 启动服务方式

### 1. 安装依赖

```bash
# 进入后端目录
cd document_system/backend

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 初始化数据库
python init_db.py
```

### 3. 启动后端服务

```bash
# 启动开发服务器
python run.py
```

后端服务启动后，API服务将运行在：http://192.168.1.95:5000/api

## API访问路径

### 用户认证

- POST /api/auth/login - 用户登录
- POST /api/auth/register - 用户注册
- POST /api/auth/logout - 用户登出

### 文档管理

- GET /api/documents - 获取文档列表
- POST /api/documents - 上传新文档
- GET /api/documents/<id> - 获取文档详情
- DELETE /api/documents/<id> - 删除文档
- GET /api/documents/<id>/download - 下载文档

### 分类管理

- GET /api/categories - 获取分类列表
- POST /api/categories - 创建新分类
- PUT /api/categories/<id> - 更新分类
- DELETE /api/categories/<id> - 删除分类

### 用户管理

- GET /api/users - 获取用户列表（需要管理员权限）
- POST /api/users - 创建新用户（需要管理员权限）
- PUT /api/users/<id> - 更新用户信息（需要管理员权限）
- DELETE /api/users/<id> - 删除用户（需要管理员权限）

## 配置说明

主要配置文件：`app/config.py`

可配置项包括：
- 数据库连接信息
- JWT密钥
- 文件上传路径
- 服务端口和主机

## 注意事项

1. 确保Python版本 >= 3.8
2. 首次运行需要初始化数据库
3. 管理员账号需要在初始化数据库时创建
4. 文件上传默认保存路径为 `uploads/` 目录

## 许可证

MIT