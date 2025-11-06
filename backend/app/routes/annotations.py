from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db
from app.models.annotation import Annotation
from app.models.document import Document
from app.utils.auth import verify_permission, check_document_permission, get_current_user

# 创建蓝图
annotations_bp = Blueprint('annotations', __name__)


@annotations_bp.route('/document/<int:document_id>', methods=['GET'])
@jwt_required()
@verify_permission('view')
def get_document_annotations(document_id):
    """获取文档的所有标注"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 查找文档
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'message': '文档不存在'}), 404
        
        # 检查权限
        if not check_document_permission(user, document):
            return jsonify({'message': '无权限访问此文档'}), 403
        
        # 获取标注
        annotations = Annotation.query.filter_by(document_id=document_id).order_by(Annotation.created_at).all()
        
        # 构建响应
        result = []
        for annotation in annotations:
            result.append({
                'id': annotation.id,
                'document_id': annotation.document_id,
                'user_id': annotation.user_id,
                'username': annotation.user.username,
                'type': annotation.type,
                'content': annotation.content,
                'position': annotation.position,
                'style': annotation.style,
                'page_number': annotation.page_number,
                'created_at': annotation.created_at.isoformat(),
                'updated_at': annotation.updated_at.isoformat()
            })
        
        return jsonify({'annotations': result})
    
    except Exception as e:
        return jsonify({'message': f'获取标注失败: {str(e)}'}), 500


@annotations_bp.route('/', methods=['POST'])
@jwt_required()
def create_annotation():
    """创建标注"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        data = request.get_json()
        
        # 验证参数
        if not data.get('document_id') or not data.get('type'):
            return jsonify({'message': '文档ID和标注类型不能为空'}), 400
        
        # 支持的标注类型
        supported_types = ['text', 'rectangle', 'circle', 'arrow']
        if data['type'] not in supported_types:
            return jsonify({'message': '不支持的标注类型'}), 400
        
        # 查找文档
        document = Document.query.get(data['document_id'])
        if not document:
            return jsonify({'message': '文档不存在'}), 404
        
        # 检查权限
        if not check_document_permission(user, document):
            return jsonify({'message': '无权限访问此文档'}), 403
        
        # 检查文档类型（仅版式文件支持标注）
        if document.file_type != 'layout':
            return jsonify({'message': '仅版式文件支持标注功能'}), 400
        
        # 创建标注
        annotation = Annotation(
            document_id=data['document_id'],
            user_id=user.id,
            type=data['type'],
            content=data.get('content', ''),
            position=data.get('position', '{}'),
            style=data.get('style', '{}'),
            page_number=data.get('page_number', 1)
        )
        
        db.session.add(annotation)
        db.session.commit()
        
        return jsonify({
            'message': '标注创建成功',
            'annotation': {
                'id': annotation.id,
                'document_id': annotation.document_id,
                'user_id': annotation.user_id,
                'username': user.username,
                'type': annotation.type,
                'content': annotation.content,
                'position': annotation.position,
                'style': annotation.style,
                'page_number': annotation.page_number,
                'created_at': annotation.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建标注失败: {str(e)}'}), 500


@annotations_bp.route('/<int:annotation_id>', methods=['PUT'])
@jwt_required()
def update_annotation(annotation_id):
    """更新标注"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 查找标注
        annotation = Annotation.query.get(annotation_id)
        if not annotation:
            return jsonify({'message': '标注不存在'}), 404
        
        # 检查权限（只允许创建者或管理员修改）
        if annotation.user_id != user.id and user.role.name != 'admin':
            return jsonify({'message': '无权限修改此标注'}), 403
        
        data = request.get_json()
        
        # 更新字段
        if 'content' in data:
            annotation.content = data['content']
        if 'position' in data:
            annotation.position = data['position']
        if 'style' in data:
            annotation.style = data['style']
        if 'page_number' in data:
            annotation.page_number = data['page_number']
        
        db.session.commit()
        
        return jsonify({
            'message': '标注更新成功',
            'annotation': {
                'id': annotation.id,
                'content': annotation.content,
                'position': annotation.position,
                'style': annotation.style,
                'page_number': annotation.page_number,
                'updated_at': annotation.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新标注失败: {str(e)}'}), 500


@annotations_bp.route('/<int:annotation_id>', methods=['DELETE'])
@jwt_required()
def delete_annotation(annotation_id):
    """删除标注"""
    try:
        # 获取当前用户
        user = get_current_user()
        
        # 查找标注
        annotation = Annotation.query.get(annotation_id)
        if not annotation:
            return jsonify({'message': '标注不存在'}), 404
        
        # 检查权限（只允许创建者或管理员删除）
        if annotation.user_id != user.id and user.role.name != 'admin':
            return jsonify({'message': '无权限删除此标注'}), 403
        
        # 删除标注
        db.session.delete(annotation)
        db.session.commit()
        
        return jsonify({'message': '标注删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除标注失败: {str(e)}'}), 500


@annotations_bp.route('/user/<int:user_id>/documents/<int:document_id>', methods=['GET'])
@jwt_required()
@verify_permission('view')
def get_user_document_annotations(user_id, document_id):
    """获取指定用户在指定文档上的标注"""
    try:
        # 获取当前用户
        current_user = get_current_user()
        
        # 查找文档
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'message': '文档不存在'}), 404
        
        # 检查权限
        if not check_document_permission(current_user, document):
            return jsonify({'message': '无权限访问此文档'}), 403
        
        # 获取标注
        annotations = Annotation.query.filter_by(
            user_id=user_id,
            document_id=document_id
        ).order_by(Annotation.created_at).all()
        
        # 构建响应
        result = []
        for annotation in annotations:
            result.append({
                'id': annotation.id,
                'type': annotation.type,
                'content': annotation.content,
                'position': annotation.position,
                'style': annotation.style,
                'page_number': annotation.page_number,
                'created_at': annotation.created_at.isoformat()
            })
        
        return jsonify({'annotations': result})
    
    except Exception as e:
        return jsonify({'message': f'获取用户标注失败: {str(e)}'}), 500