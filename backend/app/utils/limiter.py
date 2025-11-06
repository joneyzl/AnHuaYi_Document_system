from datetime import datetime, timedelta
from app.models.document import Document


# 每日上传限制配置
DAILY_UPLOAD_LIMIT = 20  # 普通用户每日上传文件限制


def check_upload_limit(user_id):
    """
    检查用户今日上传文件数量是否超过限制
    :param user_id: 用户ID
    :return: 是否允许上传（True/False）
    """
    try:
        # 计算今日开始时间
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询用户今日上传的文件数量
        upload_count = Document.query.filter(
            Document.creator_id == user_id,
            Document.created_at >= today
        ).count()
        
        # 检查是否超过限制
        if upload_count >= DAILY_UPLOAD_LIMIT:
            return False
        
        return True
    
    except Exception as e:
        # 发生异常时默认允许上传，避免影响正常使用
        print(f"检查上传限制时发生错误: {str(e)}")
        return True


def get_upload_remaining(user_id):
    """
    获取用户今日剩余上传次数
    :param user_id: 用户ID
    :return: 剩余上传次数
    """
    try:
        # 计算今日开始时间
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询用户今日上传的文件数量
        upload_count = Document.query.filter(
            Document.creator_id == user_id,
            Document.created_at >= today
        ).count()
        
        # 计算剩余次数
        remaining = DAILY_UPLOAD_LIMIT - upload_count
        return max(0, remaining)
    
    except Exception as e:
        # 发生异常时返回默认值
        print(f"获取剩余上传次数时发生错误: {str(e)}")
        return DAILY_UPLOAD_LIMIT


def get_user_upload_stats(user_id):
    """
    获取用户上传统计信息
    :param user_id: 用户ID
    :return: 包含各种统计信息的字典
    """
    try:
        # 计算今日开始时间
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 计算本周开始时间（周一）
        days_since_monday = datetime.now().weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # 计算本月开始时间
        month_start = today.replace(day=1)
        
        # 查询各种统计数据
        today_count = Document.query.filter(
            Document.creator_id == user_id,
            Document.created_at >= today
        ).count()
        
        week_count = Document.query.filter(
            Document.creator_id == user_id,
            Document.created_at >= week_start
        ).count()
        
        month_count = Document.query.filter(
            Document.creator_id == user_id,
            Document.created_at >= month_start
        ).count()
        
        total_count = Document.query.filter_by(user_id=user_id).count()
        
        return {
            'today_count': today_count,
            'week_count': week_count,
            'month_count': month_count,
            'total_count': total_count,
            'today_remaining': max(0, DAILY_UPLOAD_LIMIT - today_count)
        }
    
    except Exception as e:
        # 发生异常时返回空字典
        print(f"获取上传统计信息时发生错误: {str(e)}")
        return {
            'today_count': 0,
            'week_count': 0,
            'month_count': 0,
            'total_count': 0,
            'today_remaining': DAILY_UPLOAD_LIMIT
        }