from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from app.models.system_log import SystemLog
from app.models.access_log import AccessLog
from app.models.user import User
from app.utils.auth import verify_permission, get_current_user

# 创建蓝图
system_logs_bp = Blueprint('system_logs', __name__)


@system_logs_bp.route('/system', methods=['GET'])
@jwt_required()
@verify_permission('admin')
def get_system_logs():
    """获取系统操作日志 - 管理员专用"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 获取过滤参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        operator_id = request.args.get('operator_id', type=int)
        operation_type = request.args.get('operation_type')
        target_entity = request.args.get('target_entity')
        target_id = request.args.get('target_id', type=int)
        
        # 构建查询
        query = SystemLog.query
        
        # 应用过滤条件
        if start_time:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(SystemLog.created_at >= start)
        if end_time:
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(SystemLog.created_at <= end)
        if operator_id:
            query = query.filter(SystemLog.operator_id == operator_id)
        if operation_type:
            query = query.filter(SystemLog.operation_type == operation_type)
        if target_entity:
            query = query.filter(SystemLog.target_entity == target_entity)
        if target_id:
            query = query.filter(SystemLog.target_id == target_id)
        
        # 按时间倒序排列
        query = query.order_by(SystemLog.created_at.desc())
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 构建响应数据
        logs = []
        for log in pagination.items:
            logs.append({
                'id': log.id,
                'operator_id': log.operator_id,
                'operator_name': log.operator_name,
                'operation_type': log.operation_type,
                'operation_desc': log.operation_desc,
                'target_entity': log.target_entity,
                'target_id': log.target_id,
                'target_name': log.target_name,
                'details': log.details,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat()
            })
        
        return jsonify({
            'logs': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    
    except Exception as e:
        return jsonify({'message': f'获取系统日志失败: {str(e)}'}), 500


@system_logs_bp.route('/access', methods=['GET'])
@jwt_required()
@verify_permission('admin')
def get_access_logs():
    """获取文档访问日志 - 管理员专用"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 获取过滤参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        user_id = request.args.get('user_id', type=int)
        document_id = request.args.get('document_id', type=int)
        action_type = request.args.get('action_type')
        
        # 构建查询
        query = AccessLog.query
        
        # 应用过滤条件
        if start_time:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(AccessLog.created_at >= start)
        if end_time:
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(AccessLog.created_at <= end)
        if user_id:
            query = query.filter(AccessLog.user_id == user_id)
        if document_id:
            query = query.filter(AccessLog.document_id == document_id)
        if action_type:
            query = query.filter(AccessLog.action_type == action_type)
        
        # 按时间倒序排列
        query = query.order_by(AccessLog.created_at.desc())
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 构建响应数据
        logs = []
        for log in pagination.items:
            logs.append({
                'id': log.id,
                'user_id': log.user_id,
                'document_id': log.document_id,
                'action_type': log.action_type,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'created_at': log.created_at.isoformat()
            })
        
        return jsonify({
            'logs': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    
    except Exception as e:
        return jsonify({'message': f'获取访问日志失败: {str(e)}'}), 500


@system_logs_bp.route('/user/<int:user_id>/access', methods=['GET'])
@jwt_required()
def get_user_access_logs(user_id):
    """获取指定用户的访问日志 - 管理员或用户本人可见"""
    try:
        current_user = get_current_user()
        
        # 权限检查：只能查看自己的日志或管理员可以查看所有
        if current_user.id != user_id and current_user.role.name != 'admin':
            return jsonify({'message': '无权限查看此用户的访问日志'}), 403
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 获取过滤参数
        days = request.args.get('days', 7, type=int)  # 默认显示最近7天
        
        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # 构建查询
        query = AccessLog.query.filter(
            AccessLog.user_id == user_id,
            AccessLog.created_at >= start_time
        )
        
        # 按时间倒序排列
        query = query.order_by(AccessLog.created_at.desc())
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 构建响应数据
        logs = []
        for log in pagination.items:
            logs.append({
                'id': log.id,
                'document_id': log.document_id,
                'action_type': log.action_type,
                'created_at': log.created_at.isoformat()
            })
        
        return jsonify({
            'logs': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    
    except Exception as e:
        return jsonify({'message': f'获取用户访问日志失败: {str(e)}'}), 500


@system_logs_bp.route('/statistics', methods=['GET'])
@jwt_required()
@verify_permission('admin')
def get_log_statistics():
    """获取日志统计信息 - 管理员专用"""
    try:
        # 计算时间范围（最近30天）
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        
        # 统计各操作类型的数量
        operation_counts = {}
        access_logs = AccessLog.query.filter(
            AccessLog.created_at >= start_time
        ).all()
        
        for log in access_logs:
            if log.action_type not in operation_counts:
                operation_counts[log.action_type] = 0
            operation_counts[log.action_type] += 1
        
        # 统计活跃用户数
        active_users = AccessLog.query.filter(
            AccessLog.created_at >= start_time
        ).distinct(AccessLog.user_id).count()
        
        # 统计最近7天的日访问量
        daily_stats = []
        for i in range(7):
            date = end_time - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = AccessLog.query.filter(
                AccessLog.created_at >= date_start,
                AccessLog.created_at <= date_end
            ).count()
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_stats.reverse()  # 按日期升序排列
        
        return jsonify({
            'operation_counts': operation_counts,
            'active_users': active_users,
            'daily_access_stats': daily_stats,
            'total_access_logs': len(access_logs),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500