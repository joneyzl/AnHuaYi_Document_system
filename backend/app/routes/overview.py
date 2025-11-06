from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.document import Document, DocumentCategory
from app.models.user import User
from app.utils.auth import get_current_user, verify_permission
from app import db

# 创建蓝图
overview_bp = Blueprint('overview', __name__)

@overview_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取系统统计信息"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 构建文档查询
        document_query = Document.query
        if user.role.name != 'admin':
            # 非管理员只能看到自己的文档和公开文档
            document_query = document_query.filter(
                (Document.creator_id == user.id) | (Document.is_private == False)
            )
        
        # 获取统计数据
        total_documents = document_query.count()
        total_categories = DocumentCategory.query.count()
        
        # 获取用户数（只有管理员可以看到总数）
        total_users = User.query.count() if user.role.name == 'admin' else None
        
        return jsonify({
            'total_documents': total_documents,
            'total_categories': total_categories,
            'total_users': total_users
        })
    
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500

@overview_bp.route('/recent-documents', methods=['GET'])
@jwt_required()
def get_recent_documents():
    """获取最近的文档"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 获取数量参数
        limit = request.args.get('limit', 5, type=int)
        
        # 构建文档查询
        document_query = Document.query
        if user.role.name != 'admin':
            # 非管理员只能看到自己的文档和公开文档
            document_query = document_query.filter(
                (Document.creator_id == user.id) | (Document.is_private == False)
            )
        
        # 获取最近的文档
        recent_docs = document_query.order_by(Document.created_at.desc()).limit(limit).all()
        
        # 构建响应
        documents = []
        for doc in recent_docs:
            documents.append({
                'id': doc.id,
                'title': doc.title,
                'category': doc.category.name if doc.category else '未分类',
                'created_at': doc.created_at.isoformat(),
                'username': doc.creator.username if doc.creator else '',
                'file_type': doc.file_type
            })
        
        return jsonify({
            'documents': documents
        })
    
    except Exception as e:
        return jsonify({'message': f'获取最近文档失败: {str(e)}'}), 500