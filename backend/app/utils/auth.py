from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
# 注：当前文件位于 app/utils/ 目录下


def verify_permission(required_permission):
    """
    权限验证装饰器
    :param required_permission: 需要的权限类型
    :return: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 验证JWT令牌
            verify_jwt_in_request()
            
            # 获取当前用户ID
            user_id = get_jwt_identity()
            
            # 查找用户
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 检查用户状态
            if not user.status:
                return jsonify({'message': '用户账号已被禁用'}), 403
            
            # 检查权限
            has_permission = False
            for permission in user.role.permissions:
                if permission.permission_type == required_permission and permission.is_enabled:
                    has_permission = True
                    break
            
            # 如果是管理员，默认有所有权限
            if user.role.name == 'admin':
                has_permission = True
            
            if not has_permission:
                return jsonify({'message': '无权限访问此资源'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """
    获取当前登录用户
    :return: User对象
    """
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def check_document_permission(user, document):
    """
    检查用户是否有权限访问文档
    :param user: 用户对象
    :param document: 文档对象
    :return: 布尔值，表示是否有权限
    """
    # 管理员可以访问所有文档
    if user.role.name == 'admin':
        return True
    
    # 文档所有者可以访问
    if document.creator_id == user.id:
        return True
    
    # 非私有文档所有人都可以访问
    if not document.is_private:
        return True
    
    return False


def check_permission(user, required_permission):
    """
    检查用户是否有指定权限
    :param user: 用户对象
    :param required_permission: 权限类型
    :return: 布尔值
    """
    # 管理员默认有所有权限
    if user.role.name == 'admin':
        return True
    
    # 检查用户权限
    for permission in user.role.permissions:
        if permission.permission_type == required_permission and permission.is_enabled:
            return True
    
    return False