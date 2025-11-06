from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Favorite(Base):
    """用户收藏文档模型"""
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    user = relationship('User', backref='user_favorites')
    document = relationship('Document', backref='favorited_by')
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, document_id={self.document_id})>"