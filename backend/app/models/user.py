from datetime import datetime
from app import db


class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    description = db.Column(db.String(200), comment='角色描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系
    users = db.relationship('User', backref='role', lazy='dynamic')
    permissions = db.relationship('Permission', backref='role', lazy='dynamic')


class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, comment='角色ID')
    permission_type = db.Column(db.String(50), nullable=False, comment='权限类型：view/upload/edit/user_manage/category_manage')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    
    # 复合唯一约束
    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_type', name='_role_permission_uc'),
    )


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = db.Column(db.String(128), nullable=False, comment='密码哈希')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2, comment='角色ID')
    status = db.Column(db.Boolean, default=True, comment='用户状态：True启用，False禁用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    last_login_at = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    
    # 关系
    documents = db.relationship('Document', backref='creator', lazy='dynamic')
    annotations = db.relationship('Annotation', backref='user', lazy='dynamic')
    favorites = db.relationship('UserFavorite', lazy='dynamic')
    access_logs = db.relationship('AccessLog', backref='user', lazy='dynamic')
    
    @property
    def is_admin(self):
        """判断是否为管理员"""
        return self.role.name == 'admin'