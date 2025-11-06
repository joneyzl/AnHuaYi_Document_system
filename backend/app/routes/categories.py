from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db
from app.models.document import Document, DocumentCategory
from app.utils.auth import verify_permission

# 创建蓝图
categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """获取分类列表"""
    try:
        # 获取所有分类
        categories = DocumentCategory.query.order_by(DocumentCategory.created_at.desc()).all()
        
        # 构建分类列表
        category_list = []
        
        # 构建响应数据
        for cat in categories:
            category_list.append({
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'document_count': Document.query.filter_by(category_id=cat.id).count(),
                'created_at': cat.created_at.isoformat()
            })
        
        return jsonify({'categories': category_list})
    
    except Exception as e:
        return jsonify({'message': f'获取分类列表失败: {str(e)}'}), 500


@categories_bp.route('/', methods=['POST'])
@jwt_required()
@verify_permission('category_manage')
def create_category():
    """创建分类"""
    try:
        data = request.get_json()
        
        # 验证参数
        if not data.get('name'):
            return jsonify({'message': '分类名称不能为空'}), 400
        
        # 检查名称长度
        if len(data['name']) > 100:
            return jsonify({'message': '分类名称不能超过100个字符'}), 400
        
        # 检查名称是否已存在
        if DocumentCategory.query.filter_by(name=data['name']).first():
            return jsonify({'message': '分类名称已存在'}), 400
        
        # 创建分类
        category = DocumentCategory(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': '分类创建成功',
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'created_at': category.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建分类失败: {str(e)}'}), 500


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@verify_permission('category_manage')
def update_category(category_id):
    """更新分类"""
    try:
        # 查找分类
        category = DocumentCategory.query.get(category_id)
        if not category:
            return jsonify({'message': '分类不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称长度
            if len(data['name']) > 100:
                return jsonify({'message': '分类名称不能超过100个字符'}), 400
            # 检查名称是否已存在（排除当前分类）
            existing = DocumentCategory.query.filter(DocumentCategory.name == data['name'], DocumentCategory.id != category_id).first()
            if existing:
                return jsonify({'message': '分类名称已存在'}), 400
            category.name = data['name']
        
        if 'description' in data:
            category.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': '分类更新成功',
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'created_at': category.created_at.isoformat(),
                'updated_at': category.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新分类失败: ' + str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@verify_permission('category_manage')
def delete_category(category_id):
    """删除分类"""
    try:
        # 查找分类
        category = DocumentCategory.query.get(category_id)
        if not category:
            return jsonify({'message': '分类不存在'}), 404
        
        # 检查是否有关联的文档
        document_count = Document.query.filter_by(category_id=category_id).count()
        if document_count > 0:
            return jsonify({'message': f'该分类下还有{document_count}个文档，不能删除'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': '分类删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除分类失败: ' + str(e)}), 500


@categories_bp.route('/<int:category_id>/documents', methods=['GET'])
@jwt_required()
def get_category_documents(category_id):
    """获取分类下的文档列表"""
    try:
        # 查找分类
        category = DocumentCategory.query.get(category_id)
        if not category:
            return jsonify({'message': '分类不存在'}), 404
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = Document.query.filter_by(category_id=category_id)
        
        # 执行查询
        pagination = query.order_by(Document.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构建响应
        documents = []
        for doc in pagination.items:
            documents.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'file_type': doc.file_type,
                'file_name': doc.original_filename,
                'file_size': doc.file_size,
                'user_id': doc.user_id,
                'username': doc.user.username,
                'created_at': doc.created_at.isoformat()
            })
        
        return jsonify({
            'documents': documents,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'message': f'获取分类文档失败: {str(e)}'}), 500