from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base


class SystemLog(Base):
    """系统日志模型 - 记录权限变更、用户管理等操作"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='操作人ID')
    operator_name = Column(String(100), nullable=False, comment='操作人姓名')
    operation_type = Column(String(50), nullable=False, comment='操作类型：auth_grant/auth_revoke/user_create/user_update/user_delete/category_manage')
    operation_desc = Column(String(255), nullable=False, comment='操作描述')
    target_entity = Column(String(50), comment='操作目标实体：user/role/permission/category')
    target_id = Column(Integer, comment='操作目标ID')
    target_name = Column(String(100), comment='操作目标名称')
    details = Column(Text, comment='详细操作内容（JSON格式）')
    ip_address = Column(String(50), comment='IP地址')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='操作时间')
    
    # 关联关系
    operator = relationship('User', backref='system_operations')
    
    # 索引，提高查询效率
    __table_args__ = (
        Index('idx_operator_time', 'operator_id', 'created_at'),
        Index('idx_type_time', 'operation_type', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SystemLog(operator={self.operator_name}, type={self.operation_type}, time={self.created_at})>"