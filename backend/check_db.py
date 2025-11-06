from app import create_app, db
from app.models.document import DocumentCategory

# 创建应用实例
app = create_app()

# 使用应用上下文
with app.app_context():
    print('当前数据库中的分类信息:')
    categories = DocumentCategory.query.all()
    
    for cat in categories:
        print(f'ID: {cat.id}, 名称: {cat.name}, 描述: {cat.description}')
    
    print(f'分类总数: {len(categories)}')
    
    # 检查数据库连接和表结构
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    print('\n数据库中的表:')
    print(inspector.get_table_names())
    
    if 'document_categories' in inspector.get_table_names():
        print('\n分类表结构:')
        print(inspector.get_columns('document_categories'))