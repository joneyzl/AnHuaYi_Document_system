from datetime import datetime
from app.models import db
from app.models.system_log import SystemLog
from app.models.access_log import AccessLog
import json


class LogService:
    """日志服务类"""
    
    @staticmethod
    def log_system_operation(operator, operation_type, operation_desc, 
                           target_entity=None, target_id=None, target_name=None, 
                           details=None, ip_address=None):
        """记录系统操作日志
        
        Args:
            operator: 用户对象
            operation_type: 操作类型
            operation_desc: 操作描述
            target_entity: 目标实体类型
            target_id: 目标实体ID
            target_name: 目标实体名称
            details: 详细信息（字典）
            ip_address: IP地址
        """
        try:
            # 序列化details
            details_str = json.dumps(details) if details else None
            
            # 创建日志记录
            log = SystemLog(
                operator_id=operator.id,
                operator_name=operator.username,
                operation_type=operation_type,
                operation_desc=operation_desc,
                target_entity=target_entity,
                target_id=target_id,
                target_name=target_name,
                details=details_str,
                ip_address=ip_address
            )
            
            db.session.add(log)
            db.session.commit()
            return True
        except Exception as e:
            # 记录日志失败不应影响主流程，回滚事务
            db.session.rollback()
            print(f"记录系统日志失败: {str(e)}")
            return False
    
    @staticmethod
    def log_document_access(user, document, action_type, request=None):
        """记录文档访问日志
        
        Args:
            user: 用户对象
            document: 文档对象
            action_type: 操作类型
            request: Flask请求对象（用于获取IP和User-Agent）
        """
        try:
            # 获取IP地址和User-Agent
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')[:500]  # 限制长度
            
            # 创建访问日志
            log = AccessLog(
                user_id=user.id,
                document_id=document.id,
                action_type=action_type,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(log)
            db.session.commit()
            return True
        except Exception as e:
            # 记录日志失败不应影响主流程，回滚事务
            db.session.rollback()
            print(f"记录访问日志失败: {str(e)}")
            return False
    
    @staticmethod
    def log_auth_grant(admin_user, user, role, permission=None, request=None):
        """记录权限授予日志
        
        Args:
            admin_user: 管理员用户
            user: 被授权用户
            role: 角色对象
            permission: 权限名称（可选）
            request: Flask请求对象
        """
        operation_type = 'auth_grant'
        
        if permission:
            operation_desc = f"授予用户{user.username}操作权限: {permission}"
            details = {
                'user_id': user.id,
                'username': user.username,
                'permission': permission
            }
        else:
            operation_desc = f"授予用户{user.username}角色: {role.name}"
            details = {
                'user_id': user.id,
                'username': user.username,
                'role_id': role.id,
                'role_name': role.name
            }
        
        return LogService.log_system_operation(
            operator=admin_user,
            operation_type=operation_type,
            operation_desc=operation_desc,
            target_entity='user',
            target_id=user.id,
            target_name=user.username,
            details=details,
            ip_address=request.remote_addr if request else None
        )
    
    @staticmethod
    def log_auth_revoke(admin_user, user, role, permission=None, request=None):
        """记录权限撤销日志
        
        Args:
            admin_user: 管理员用户
            user: 被撤销权限的用户
            role: 角色对象
            permission: 权限名称（可选）
            request: Flask请求对象
        """
        operation_type = 'auth_revoke'
        
        if permission:
            operation_desc = f"撤销用户{user.username}操作权限: {permission}"
            details = {
                'user_id': user.id,
                'username': user.username,
                'permission': permission
            }
        else:
            operation_desc = f"撤销用户{user.username}角色: {role.name}"
            details = {
                'user_id': user.id,
                'username': user.username,
                'role_id': role.id,
                'role_name': role.name
            }
        
        return LogService.log_system_operation(
            operator=admin_user,
            operation_type=operation_type,
            operation_desc=operation_desc,
            target_entity='user',
            target_id=user.id,
            target_name=user.username,
            details=details,
            ip_address=request.remote_addr if request else None
        )
    
    @staticmethod
    def log_user_management(admin_user, user, operation, request=None):
        """记录用户管理操作日志
        
        Args:
            admin_user: 管理员用户
            user: 被管理的用户
            operation: 操作类型（create/update/delete）
            request: Flask请求对象
        """
        operation_type_map = {
            'create': 'user_create',
            'update': 'user_update',
            'delete': 'user_delete'
        }
        
        operation_desc_map = {
            'create': f"创建用户: {user.username}",
            'update': f"更新用户: {user.username}",
            'delete': f"删除用户: {user.username}"
        }
        
        return LogService.log_system_operation(
            operator=admin_user,
            operation_type=operation_type_map.get(operation, 'user_update'),
            operation_desc=operation_desc_map.get(operation, f"管理用户: {user.username}"),
            target_entity='user',
            target_id=user.id,
            target_name=user.username,
            details={
                'user_id': user.id,
                'username': user.username,
                'operation': operation,
                'role': user.role.name if user.role else None
            },
            ip_address=request.remote_addr if request else None
        )
    
    @staticmethod
    def log_category_management(admin_user, category, operation, request=None):
        """记录分类管理操作日志
        
        Args:
            admin_user: 管理员用户
            category: 分类对象
            operation: 操作类型（create/update/delete）
            request: Flask请求对象
        """
        operation_desc_map = {
            'create': f"创建分类: {category.name}",
            'update': f"更新分类: {category.name}",
            'delete': f"删除分类: {category.name if hasattr(category, 'name') else '未知'}"
        }
        
        return LogService.log_system_operation(
            operator=admin_user,
            operation_type='category_manage',
            operation_desc=operation_desc_map.get(operation, f"管理分类: {category.name if hasattr(category, 'name') else '未知'}"),
            target_entity='category',
            target_id=category.id if hasattr(category, 'id') else None,
            target_name=category.name if hasattr(category, 'name') else '未知',
            details={
                'category_id': category.id if hasattr(category, 'id') else None,
                'category_name': category.name if hasattr(category, 'name') else '未知',
                'operation': operation,
                'parent_id': category.parent_id if hasattr(category, 'parent_id') else None
            },
            ip_address=request.remote_addr if request else None
        )