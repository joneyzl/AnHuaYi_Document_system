from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from app.models import db
from app.models.user import User, Role
from app.utils.auth import verify_permission

# 创建蓝图
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证参数
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 获取普通用户角色
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            return jsonify({'message': '系统未初始化，请联系管理员'}), 500
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            email=data.get('email'),
            role_id=user_role.id,
            status=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': '注册成功'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 验证参数
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        # 验证用户和密码
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'message': '用户名或密码错误'}), 401
        
        # 检查用户状态
        if not user.status:
            return jsonify({'message': '账号已被禁用'}), 403
        
        # 创建访问令牌
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=1),
            additional_claims={
                'role': user.role.name,
                'username': user.username
            }
        )
        
        # 获取用户权限
        permissions = {p.permission_type: p.is_enabled for p in user.role.permissions}
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.name,
                'permissions': permissions
            }
        })
    
    except Exception as e:
        return jsonify({'message': f'登录失败: {str(e)}'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
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


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        # 验证参数
        if not old_password or not new_password:
            return jsonify({'message': '原密码和新密码不能为空'}), 400
        
        # 验证原密码
        if not check_password_hash(user.password_hash, old_password):
            return jsonify({'message': '原密码错误'}), 400
        
        # 更新密码
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'修改密码失败: {str(e)}'}), 500