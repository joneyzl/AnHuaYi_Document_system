from datetime import datetime
from app.models import db


class UserFavorite(db.Model):
    """用户收藏模型"""
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, comment='文档ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='收藏时间')
    
    # 复合唯一约束，确保一个用户只能收藏一次同一文档
    __table_args__ = (
        db.UniqueConstraint('user_id', 'document_id', name='_user_document_favorite_uc'),
    )