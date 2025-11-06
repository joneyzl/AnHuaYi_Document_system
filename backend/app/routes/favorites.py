from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db
from app.models.user_favorite import UserFavorite
from app.models.document import Document, DocumentCategory
from app.utils.auth import get_current_user, check_document_permission

# 创建蓝图
favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/', methods=['POST'])
@jwt_required()
def add_favorite():
    """添加文档到收藏"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        data = request.get_json()
        document_id = data.get('document_id')
        
        if not document_id:
            return jsonify({'message': '文档ID不能为空'}), 400
        
        # 检查文档是否存在
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'message': '文档不存在'}), 404
        
        # 检查用户是否有权限访问该文档
        if not check_document_permission(user, document):
            return jsonify({'message': '无权限访问此文档'}), 403
        
        # 检查是否已经收藏
        existing_favorite = UserFavorite.query.filter_by(
            user_id=user.id,
            document_id=document_id
        ).first()
        
        if existing_favorite:
            return jsonify({'message': '已经收藏过该文档'}), 400
        
        # 添加收藏
        favorite = UserFavorite(
            user_id=user.id,
            document_id=document_id
        )
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'message': '收藏成功',
            'favorite_id': favorite.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'收藏失败: {str(e)}'}), 500


@favorites_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(document_id):
    """取消文档收藏"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 查找收藏记录
        favorite = UserFavorite.query.filter_by(
            user_id=user.id,
            document_id=document_id
        ).first()
        
        if not favorite:
            return jsonify({'message': '未找到收藏记录'}), 404
        
        # 删除收藏
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': '取消收藏成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'取消收藏失败: {str(e)}'}), 500


@favorites_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_favorites():
    """获取当前用户的收藏列表"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 获取用户的收藏
        favorites = UserFavorite.query.filter_by(
            user_id=user.id
        ).order_by(UserFavorite.created_at.desc()).all()
        
        # 构建响应
        result = []
        for favorite in favorites:
            doc = favorite.document
            # 检查文档是否仍然存在且用户有权限访问
            if doc and check_document_permission(user, doc):
                result.append({
                    'id': favorite.id,
                    'document_id': doc.id,
                    'document_name': doc.name,
                    'document_type': doc.file_type,
                    'document_format': doc.format,
                    'category_name': doc.category.name if doc.category else '未分类',
                      'created_at': favorite.created_at.isoformat()
                })
        
        return jsonify({'favorites': result})
    
    except Exception as e:
        return jsonify({'message': f'获取收藏列表失败: {str(e)}'}), 500


@favorites_bp.route('/check/<int:document_id>', methods=['GET'])
@jwt_required()
def check_favorite(document_id):
    """检查文档是否已被收藏"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 检查是否已经收藏
        favorite = UserFavorite.query.filter_by(
            user_id=user.id,
            document_id=document_id
        ).first()
        
        return jsonify({
            'is_favorite': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        })
    
    except Exception as e:
        return jsonify({'message': f'检查收藏状态失败: {str(e)}'}), 500