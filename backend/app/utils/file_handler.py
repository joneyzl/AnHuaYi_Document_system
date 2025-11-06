import os
import uuid
from datetime import datetime
import shutil
from flask import current_app
from werkzeug.utils import secure_filename

# 支持的文件格式配置
supported_formats = {
    'layout': ['.doc', '.docx', '.pdf', '.html', '.htm', '.xml', '.txt'],
    'flow': ['.txt', '.md', '.csv', '.json', '.log']
}

def get_file_type(filename):
    """
    根据文件名获取文件类型（layout或flow）
    """
    _, ext = os.path.splitext(filename.lower())
    if ext in supported_formats.get('layout', []):
        return 'layout'
    else:
        return 'flow'

def generate_unique_filename(original_filename):
    """
    生成唯一的文件名
    """
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = secure_filename(original_filename)
    name, ext = os.path.splitext(filename)
    return f"{current_time}_{unique_id}{ext}"

def save_uploaded_file(file, file_type):
    """
    保存上传的文件到指定目录
    """
    try:
        # 记录详细日志
        current_app.logger.debug(f"[DEBUG] 开始保存文件，文件类型: {file_type}")
        current_app.logger.debug(f"[DEBUG] 原始文件名: {file.filename}")
        
        # 获取存储根目录配置
        storage_root = current_app.config.get('FTP_STORAGE_PATH')
        current_app.logger.debug(f"[DEBUG] 存储根目录配置: {storage_root}")
        
        # 验证配置是否存在
        if not storage_root:
            current_app.logger.error("[ERROR] FTP_STORAGE_PATH 配置不存在")
            raise Exception("保存文件失败: FTP_STORAGE_PATH 配置不存在")
        
        # 确保存储根目录存在
        if not os.path.exists(storage_root):
            try:
                os.makedirs(storage_root, exist_ok=True)
                current_app.logger.debug(f"[DEBUG] 创建存储根目录: {storage_root}")
            except Exception as e:
                current_app.logger.error(f"[ERROR] 创建存储根目录失败: {str(e)}")
                raise Exception(f"保存文件失败: 无法创建存储目录")
        
        # 根据文件类型选择存储目录
        if file_type in supported_formats:
            upload_dir = os.path.join(storage_root, f'{file_type}_files')
        else:
            # 对于流式文件，存储在flow_files目录
            upload_dir = os.path.join(storage_root, 'flow_files')
        
        current_app.logger.debug(f"[DEBUG] 上传目录: {upload_dir}")
        
        # 确保上传目录存在
        try:
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)
                current_app.logger.debug(f"[DEBUG] 创建上传目录: {upload_dir}")
            else:
                current_app.logger.debug(f"[DEBUG] 上传目录已存在: {upload_dir}")
            
            # 验证目录权限
            if not os.access(upload_dir, os.W_OK):
                current_app.logger.error(f"[ERROR] 目录权限不足，无法写入: {upload_dir}")
                raise Exception(f"保存文件失败: 目录权限不足")
        except Exception as e:
            current_app.logger.error(f"[ERROR] 目录操作失败: {str(e)}")
            raise Exception(f"保存文件失败: {str(e)}")
        
        # 生成唯一文件名
        unique_filename = generate_unique_filename(file.filename)
        current_app.logger.debug(f"[DEBUG] 生成唯一文件名: {unique_filename}")
        
        # 完整文件路径
        file_path = os.path.join(upload_dir, unique_filename)
        current_app.logger.debug(f"[DEBUG] 文件完整路径: {file_path}")
        
        # 保存文件
        try:
            file.save(file_path)
            current_app.logger.debug(f"[DEBUG] 文件保存成功: {file_path}")
            
            # 验证文件是否保存成功
            if not os.path.exists(file_path):
                current_app.logger.error(f"[ERROR] 文件保存失败，文件不存在: {file_path}")
                raise Exception("保存文件失败: 文件未成功写入磁盘")
            
            # 返回相对路径
            relative_path = os.path.relpath(file_path, storage_root)
            current_app.logger.debug(f"[DEBUG] 返回相对路径: {relative_path}")
            return relative_path, unique_filename
        except Exception as e:
            current_app.logger.error(f"[ERROR] 文件保存过程失败: {str(e)}")
            import traceback
            current_app.logger.error(f"[ERROR] 错误堆栈: {traceback.format_exc()}")
            raise Exception(f"保存文件失败: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"[ERROR] 保存文件异常: {str(e)}")
        import traceback
        current_app.logger.error(f"[ERROR] 异常堆栈: {traceback.format_exc()}")
        raise

def delete_file(file_path):
    """
    删除文件
    :param file_path: 文件路径
    :return: 是否删除成功
    """
    try:
        # 获取存储根目录
        storage_root = current_app.config['FTP_STORAGE_PATH']
        
        # 构建完整路径
        full_path = os.path.join(storage_root, file_path)
        
        # 检查文件是否存在
        if os.path.exists(full_path):
            # 删除文件
            os.remove(full_path)
            return True
        
        return False
    except Exception as e:
        raise Exception(f"删除文件失败: {str(e)}")

def get_file_path(file_path):
    """
    获取文件的完整路径
    :param file_path: 相对路径
    :return: 完整路径
    """
    storage_root = current_app.config['FTP_STORAGE_PATH']
    return os.path.join(storage_root, file_path)

def get_file_size(file_path, is_absolute=False):
    """
    获取文件大小（字节）
    :param file_path: 文件路径
    :param is_absolute: 是否为绝对路径
    :return: 文件大小（字节），失败返回0
    """
    try:
        # 构建完整路径
        if not is_absolute:
            storage_root = current_app.config.get('FTP_STORAGE_PATH')
            if not storage_root:
                current_app.logger.error("[ERROR] FTP_STORAGE_PATH 配置不存在")
                return 0
            full_path = os.path.join(storage_root, file_path)
        else:
            full_path = file_path
        
        current_app.logger.debug(f"[DEBUG] 获取文件大小: {full_path}")
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            current_app.logger.warning(f"[WARNING] 文件不存在: {full_path}")
            return 0
        
        # 检查是否为文件
        if not os.path.isfile(full_path):
            current_app.logger.warning(f"[WARNING] 不是有效的文件: {full_path}")
            return 0
        
        # 获取文件大小
        size = os.path.getsize(full_path)
        current_app.logger.debug(f"[DEBUG] 文件大小获取成功: {size} 字节")
        return size
    except Exception as e:
        current_app.logger.error(f"[ERROR] 获取文件大小失败: {str(e)}")
        import traceback
        current_app.logger.error(f"[ERROR] 错误堆栈: {traceback.format_exc()}")
        return 0

def check_file_size(file):
    """
    检查文件大小是否符合要求
    :param file: 文件对象
    :return: 是否符合大小要求
    """
    try:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 500 * 1024 * 1024)  # 默认500MB
        
        # 保存当前位置，以便后续恢复
        current_pos = file.tell()
        
        # 移动到文件末尾获取大小
        file.seek(0, 2)  # 0表示从文件开头开始计算，2表示偏移到文件末尾
        size = file.tell()  # 获取文件大小（字节）
        
        # 重置文件指针到原始位置
        file.seek(current_pos)
        
        current_app.logger.debug(f"[DEBUG] 检查文件大小 - 当前大小: {size} 字节, 最大允许: {max_size} 字节")
        
        return size <= max_size
    except Exception as e:
        current_app.logger.error(f"[ERROR] 检查文件大小失败: {str(e)}")
        # 如果无法获取大小，保守起见返回False（不允许上传）
        return False

def update_uploaded_file(file, file_type, existing_file_path=None):
    """
    更新已上传的文件，或保存新文件
    :param file: 文件对象
    :param file_type: 文件类型
    :param existing_file_path: 现有的文件路径（如果是更新）
    :return: 相对路径，唯一文件名，文件大小
    """
    try:
        # 详细日志记录文件信息
        current_app.logger.debug(f"[DEBUG] 开始更新文件 - 文件名: {file.filename}, 类型: {file_type}")
        current_app.logger.debug(f"[DEBUG] 文件对象属性检查 - content_length: {file.content_length}")
        if hasattr(file, 'mimetype'):
            current_app.logger.debug(f"[DEBUG] 文件MIME类型: {file.mimetype}")
        
        # 尝试获取文件大小的多种方式
        content_length = file.content_length
        current_app.logger.debug(f"[DEBUG] 从content_length获取文件大小: {content_length} 字节")
        
        # 检查文件大小是否有效
        if content_length is None:
            current_app.logger.warning(f"[WARNING] content_length为None，无法直接获取文件大小")
        elif content_length <= 0:
            current_app.logger.warning(f"[WARNING] content_length为0或负数: {content_length}")
        
        # 如果指定了现有文件路径，先删除它
        if existing_file_path:
            current_app.logger.debug(f"[DEBUG] 删除现有文件: {existing_file_path}")
            delete_file(existing_file_path)
            current_app.logger.debug(f"[DEBUG] 现有文件已删除")
        else:
            current_app.logger.debug(f"[DEBUG] 没有指定现有文件路径，将保存为新文件")
        
        # 保存新文件
        current_app.logger.debug(f"[DEBUG] 开始保存新文件")
        relative_path, unique_filename = save_uploaded_file(file, file_type)
        current_app.logger.debug(f"[DEBUG] 新文件保存成功，路径: {relative_path}, 唯一文件名: {unique_filename}")
        
        # 使用新的get_file_size函数获取文件大小
        file_size = get_file_size(relative_path)
        current_app.logger.debug(f"[DEBUG] 使用get_file_size函数获取文件大小: {file_size} 字节")
        
        # 对比content_length和实际大小
        if content_length is not None and content_length != file_size:
            current_app.logger.warning(f"[WARNING] 文件大小不匹配 - content_length: {content_length}, 实际大小: {file_size}")
        
        current_app.logger.debug(f"[DEBUG] 最终保存到数据库的文件大小: {file_size} 字节")
        
        return relative_path, unique_filename, file_size
    except Exception as e:
        current_app.logger.error(f"[ERROR] 更新文件失败: {str(e)}")
        import traceback
        current_app.logger.error(f"[ERROR] 异常堆栈: {traceback.format_exc()}")
        raise Exception(f"更新文件失败: {str(e)}")

def get_document_statistics():
    """
    获取文档统计信息
    :return: 统计信息字典
    """
    stats = {
        'total_documents': 0,
        'layout_documents': 0,
        'stream_documents': 0,
        'total_size': 0
    }
    
    storage_root = current_app.config['FTP_STORAGE_PATH']
    
    # 统计版式文件
    layout_dir = os.path.join(storage_root, 'layout_files')
    if os.path.exists(layout_dir):
        for file in os.listdir(layout_dir):
            file_path = os.path.join(layout_dir, file)
            if os.path.isfile(file_path):
                stats['layout_documents'] += 1
                stats['total_size'] += os.path.getsize(file_path)
    
    # 统计流式文件
    stream_dir = os.path.join(storage_root, 'stream_files')
    if os.path.exists(stream_dir):
        for file in os.listdir(stream_dir):
            file_path = os.path.join(stream_dir, file)
            if os.path.isfile(file_path):
                stats['stream_documents'] += 1
                stats['total_size'] += os.path.getsize(file_path)
    
    stats['total_documents'] = stats['layout_documents'] + stats['stream_documents']
    
    return stats