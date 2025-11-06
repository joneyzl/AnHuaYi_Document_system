import os
from datetime import timedelta


class Config:
    """基础配置"""
    # 数据库配置 - 使用MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/anhuayidb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-here'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {
        'pdf', 'dwg', 'dxf', 'psd',  # 版式文件
        'doc', 'docx', 'md', 'txt'    # 流式文件
    }
    
    # FTP配置
    FTP_ROOT = 'D:\\test\\FTP'
    FTP_STORAGE_PATH = FTP_ROOT
    
    # 用户上传限制
    MAX_UPLOAD_PER_DAY = 20
    
    # 文档编辑自动保存间隔（秒）
    AUTO_SAVE_INTERVAL = 30
    
    # CORS配置
    CORS_HEADERS = 'Content-Type, Authorization'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    

# 配置映射字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}