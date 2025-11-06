from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# 初始化数据库实例
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    from app.config.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 配置CORS
    CORS(app, origins=['*'])  # Allow all origins for development
    
    # 注册蓝图
    from app.routes import auth_bp, users_bp, documents_bp, categories_bp, annotations_bp, favorites_bp, system_logs_bp, overview_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(annotations_bp, url_prefix='/api/annotations')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(system_logs_bp, url_prefix='/api/logs')
    app.register_blueprint(overview_bp, url_prefix='/api/overview')
    
    # 创建上传目录
    if not os.path.exists(app.config.get('FTP_ROOT', 'D:\\test\\FTP')):
        os.makedirs(app.config.get('FTP_ROOT', 'D:\\test\\FTP'), exist_ok=True)
    
    # 添加根路由
    @app.route('/')
    def index():
        return {
            'message': 'Document Management API is running',
            'version': '1.0',
            'status': 'healthy'
        }
    
    return app

# 导入模型以确保它们被注册
from app.models import user, document, favorite, system_log, access_log, annotation