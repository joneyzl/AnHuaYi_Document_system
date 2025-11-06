import os
import sys
from flask import Flask
from app.config.config import config
from app.models import db
from app.models.user import User, Role, Permission
from app.models.document import Document, DocumentVersion, DocumentCategory
from app.models.user_favorite import UserFavorite
from app.models.annotation import Annotation
from app.models.access_log import AccessLog


def create_app(config_name='development'):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    return app


def init_database():
    """初始化数据库"""
    # 创建应用
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        print("创建数据库表...")
        db.create_all()
        
        # 检查是否已存在角色数据
        if Role.query.count() == 0:
            print("初始化角色和权限数据...")
            
            # 创建管理员角色
            admin_role = Role(name='admin', description='系统管理员')
            db.session.add(admin_role)
            
            # 创建普通用户角色
            user_role = Role(name='user', description='普通用户')
            db.session.add(user_role)
            db.session.commit()
            
            # 为管理员角色添加所有权限
            admin_permissions = [
                Permission(role_id=admin_role.id, permission_type='view', is_enabled=True),
                Permission(role_id=admin_role.id, permission_type='upload', is_enabled=True),
                Permission(role_id=admin_role.id, permission_type='edit', is_enabled=True),
                Permission(role_id=admin_role.id, permission_type='user_manage', is_enabled=True),
                Permission(role_id=admin_role.id, permission_type='category_manage', is_enabled=True)
            ]
            db.session.add_all(admin_permissions)
            
            # 为普通用户角色添加基础权限
            user_permissions = [
                Permission(role_id=user_role.id, permission_type='view', is_enabled=True),
                Permission(role_id=user_role.id, permission_type='upload', is_enabled=True),
                Permission(role_id=user_role.id, permission_type='edit', is_enabled=True),
                Permission(role_id=user_role.id, permission_type='user_manage', is_enabled=False),
                Permission(role_id=user_role.id, permission_type='category_manage', is_enabled=False)
            ]
            db.session.add_all(user_permissions)
            
            # 创建默认管理员用户
            from werkzeug.security import generate_password_hash
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@example.com',
                role_id=admin_role.id,
                status=True
            )
            db.session.add(admin_user)
            
            # 创建默认文档分类
            default_categories = [
                DocumentCategory(name='技术文档', description='技术相关文档'),
                DocumentCategory(name='管理制度', description='公司管理制度'),
                DocumentCategory(name='项目计划', description='项目相关计划文档'),
                DocumentCategory(name='会议纪要', description='各类会议记录'),
                DocumentCategory(name='其他文档', description='其他类型文档')
            ]
            db.session.add_all(default_categories)
            
            db.session.commit()
            print("角色和权限数据初始化完成！")
        else:
            print("数据库已有初始数据，跳过初始化步骤。")
    
    print("数据库初始化完成！")


if __name__ == '__main__':
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    init_database()