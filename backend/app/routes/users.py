from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import os
from app.models import db
from app.models.user import User, Role
from app.models.document import Document
from app.utils.auth import verify_permission
from app.services.log_service import LogService

# 创建蓝图
users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required()
@verify_permission('user_manage')
def get_users():
    """获取用户列表"""
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 搜索参数
        username = request.args.get('username')
        role_id = request.args.get('role_id', type=int)
        status = request.args.get('status', type=bool)
        
        # 构建查询
        query = User.query
        
        if username:
            query = query.filter(User.username.like(f'%{username}%'))
        if role_id:
            query = query.filter_by(role_id=role_id)
        if status is not None:
            query = query.filter_by(status=status)
        
        # 执行查询
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构建响应
        users = []
        for user in pagination.items:
            users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role_id': user.role_id,
                'role_name': user.role.name,
                'status': user.status,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'message': f'获取用户列表失败: {str(e)}'}), 500


@users_bp.route('/', methods=['POST'])
@jwt_required()
@verify_permission('user_manage')
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        
        # 验证参数
        if not data.get('username') or not data.get('password') or not data.get('role_id'):
            return jsonify({'message': '用户名、密码和角色不能为空'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 检查角色是否存在
        if not Role.query.get(data['role_id']):
            return jsonify({'message': '角色不存在'}), 400
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            email=data.get('email'),
            role_id=data['role_id'],
            status=data.get('status', True)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 记录系统日志
        from app.utils.auth import get_current_user
        admin_user = get_current_user()
        LogService.log_user_management(admin_user, new_user, 'create', request)
        
        return jsonify({'message': '用户创建成功', 'user_id': new_user.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@verify_permission('user_manage')
def update_user(user_id):
    """更新用户信息"""
    try:
        # 查找用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 检查是否有其他用户使用相同的用户名
        if data.get('username') and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'message': '用户名已存在'}), 400
            user.username = data['username']
        
        # 更新其他字段
        if 'email' in data:
            user.email = data['email']
        if 'role_id' in data:
            # 检查角色是否存在
            if not Role.query.get(data['role_id']):
                return jsonify({'message': '角色不存在'}), 400
            user.role_id = data['role_id']
        if 'status' in data:
            user.status = data['status']
        
        # 如果提供了新密码，则更新密码
        if data.get('password'):
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        # 记录系统日志
        from app.utils.auth import get_current_user
        admin_user = get_current_user()
        LogService.log_user_management(admin_user, user, 'update', request)
        
        return jsonify({'message': '用户信息更新成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新用户信息失败: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@verify_permission('user_manage')
def delete_user(user_id):
    """删除用户"""
    try:
        # 查找用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 不允许删除自己
        current_user_id = get_jwt_identity()
        if str(user_id) == current_user_id:
            return jsonify({'message': '不能删除自己的账户'}), 400
        
        # 删除用户关联的私有文档
        private_documents = Document.query.filter_by(
            user_id=user_id,
            is_private=True
        ).all()
        
        # 这里可以添加删除文件的逻辑，暂时先删除数据库记录
        for doc in private_documents:
            db.session.delete(doc)
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        # 记录系统日志
        from app.utils.auth import get_current_user
        admin_user = get_current_user()
        LogService.log_user_management(admin_user, user, 'delete', request)
        
        return jsonify({'message': '用户删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500


@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    try:
        roles = Role.query.all()
        
        result = []
        for role in roles:
            permissions = {p.permission_type: p.is_enabled for p in role.permissions}
            result.append({
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': permissions
            })
        
        return jsonify({'roles': result})
    
    except Exception as e:
        return jsonify({'message': f'获取角色列表失败: {str(e)}'}), 500


@users_bp.route('/roles/<int:role_id>/permissions', methods=['PUT'])
@jwt_required()
@verify_permission('user_manage')
def update_role_permissions(role_id):
    """更新角色权限"""
    try:
        # 查找角色
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'message': '角色不存在'}), 404
        
        data = request.get_json()
        permissions = data.get('permissions', {})
        
        # 更新权限
        for permission_type, is_enabled in permissions.items():
            permission = next(
                (p for p in role.permissions if p.permission_type == permission_type),
                None
            )
            
            if permission:
                permission.is_enabled = is_enabled
            else:
                # 如果权限不存在，则创建新的权限
                from app.models.user import Permission
                new_permission = Permission(
                    role_id=role_id,
                    permission_type=permission_type,
                    is_enabled=is_enabled
                )
                db.session.add(new_permission)
        
        db.session.commit()
        
        return jsonify({'message': '角色权限更新成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新角色权限失败: {str(e)}'}), 500


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息 - 兼容前端请求路径"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 获取用户权限
        permissions = {p.permission_type: p.is_enabled for p in user.role.permissions}
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.name,
                'created_at': user.created_at.isoformat(),
                'permissions': permissions
            }
        })
    
    except Exception as e:
        return jsonify({'message': f'获取用户信息失败: {str(e)}'}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户个人信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新邮箱（如果提供）
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            
            if existing_user:
                return jsonify({'message': '邮箱已被其他用户使用'}), 400
            
            user.email = data['email']
        
        # 提交更改
        db.session.commit()
        
        return jsonify({'message': '个人信息更新成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新个人信息失败: {str(e)}'}), 500