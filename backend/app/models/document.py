from datetime import datetime
from app.models import db


class DocumentCategory(db.Model):
    """文档分类模型"""
    __tablename__ = 'document_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='分类名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('document_categories.id'), nullable=True, comment='父分类ID')
    description = db.Column(db.String(200), comment='分类描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 自关联关系
    parent = db.relationship('DocumentCategory', remote_side=[id], backref='children')
    # 与文档的关系
    documents = db.relationship('Document', backref='category', lazy='dynamic')


class Document(db.Model):
    """文档模型"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment='文档标题')
    description = db.Column(db.Text, comment='文档描述')
    file_name = db.Column(db.String(255), nullable=False, comment='文件名')
    file_type = db.Column(db.String(50), nullable=False, comment='文件类型')
    file_size = db.Column(db.Integer, comment='文件大小（字节）')
    document_type = db.Column(db.String(20), nullable=False, comment='文档类型：layout(版式)/flow(流式)')
    category_id = db.Column(db.Integer, db.ForeignKey('document_categories.id'), nullable=False, comment='分类ID')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    is_private = db.Column(db.Boolean, default=False, comment='是否私有')
    file_path = db.Column(db.String(500), comment='文件存储路径（FTP）')
    content = db.Column(db.Text, comment='流式文件内容')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    views_count = db.Column(db.Integer, default=0, comment='查看次数')
    
    # 关系
    versions = db.relationship('DocumentVersion', backref='document', lazy='dynamic', order_by='DocumentVersion.version_num.desc()')
    annotations = db.relationship('Annotation', backref='document', lazy='dynamic')
    favorites = db.relationship('UserFavorite', lazy='dynamic')
    access_logs = db.relationship('AccessLog', backref='document', lazy='dynamic')


class DocumentVersion(db.Model):
    """文档版本模型"""
    __tablename__ = 'document_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, comment='文档ID')
    version_num = db.Column(db.Integer, nullable=False, comment='版本号')
    content = db.Column(db.Text, comment='版本内容')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    description = db.Column(db.String(200), comment='版本说明')