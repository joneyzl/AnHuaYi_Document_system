from datetime import datetime
from app.models import db


class AccessLog(db.Model):
    """文档访问日志模型"""
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, comment='文档ID')
    action_type = db.Column(db.String(20), nullable=False, comment='操作类型：view/upload/edit/download/annotate')
    ip_address = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='用户代理')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='操作时间')
    
    # 索引，提高查询效率
    __table_args__ = (
        db.Index('idx_user_document_time', 'user_id', 'document_id', 'created_at'),
    )