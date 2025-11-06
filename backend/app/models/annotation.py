from datetime import datetime
from app.models import db


class Annotation(db.Model):
    """文档标注模型"""
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, comment='文档ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    annotation_type = db.Column(db.String(20), nullable=False, comment='标注类型：text图形标注/shape(图形标注)/arrow(箭头标注)')
    content = db.Column(db.Text, comment='标注内容')
    position = db.Column(db.JSON, comment='标注位置信息（x, y坐标、大小等）')
    style = db.Column(db.JSON, comment='标注样式（颜色、线条粗细、字体等）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')