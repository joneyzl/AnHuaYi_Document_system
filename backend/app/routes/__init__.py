# 导入所有蓝图模块
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.documents import documents_bp
from app.routes.categories import categories_bp
from app.routes.annotations import annotations_bp
from app.routes.favorites import favorites_bp
from app.routes.system_logs import system_logs_bp
from app.routes.overview import overview_bp

# 导出所有蓝图
__all__ = ['auth_bp', 'users_bp', 'documents_bp', 'categories_bp', 'annotations_bp', 'favorites_bp', 'system_logs_bp', 'overview_bp']