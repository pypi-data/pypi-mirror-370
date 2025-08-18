"""
验证模块
"""

from typing import Any, Dict, List, Optional
from loguru import logger


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    验证必需字段
    
    Args:
        data: 数据字典
        required_fields: 必需字段列表
        
    Returns:
        bool: 验证是否通过
        
    Raises:
        ValueError: 当必需字段缺失时
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    return True


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 验证是否通过
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL地址
        
    Returns:
        bool: 验证是否通过
    """
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def validate_file_path(file_path: str) -> bool:
    """
    验证文件路径
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 验证是否通过
    """
    import os
    return os.path.exists(file_path) and os.path.isfile(file_path)


def validate_file_size(file_path: str, max_size_mb: int = 20) -> bool:
    """
    验证文件大小
    
    Args:
        file_path: 文件路径
        max_size_mb: 最大文件大小(MB)
        
    Returns:
        bool: 验证是否通过
    """
    import os
    if not validate_file_path(file_path):
        return False
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return file_size_mb <= max_size_mb


def validate_file_type(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """
    验证文件类型
    
    Args:
        file_path: 文件路径
        allowed_extensions: 允许的文件扩展名列表
        
    Returns:
        bool: 验证是否通过
    """
    if allowed_extensions is None:
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.jpg', '.jpeg', '.png', '.gif']
    
    import os
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in allowed_extensions


def validate_json_data(data: str) -> bool:
    """
    验证JSON数据格式
    
    Args:
        data: JSON字符串
        
    Returns:
        bool: 验证是否通过
    """
    import json
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置数据
    
    Args:
        config: 配置字典
        
    Returns:
        bool: 验证是否通过
    """
    required_fields = ['database', 'oss', 'ai_service']
    
    try:
        validate_required_fields(config, required_fields)
        
        # 验证数据库配置
        db_config = config.get('database', {})
        db_required = ['host', 'port', 'name', 'user', 'password']
        validate_required_fields(db_config, db_required)
        
        # 验证OSS配置
        oss_config = config.get('oss', {})
        oss_required = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket']
        validate_required_fields(oss_config, oss_required)
        
        # 验证AI服务配置
        ai_config = config.get('ai_service', {})
        ai_required = ['url', 'timeout']
        validate_required_fields(ai_config, ai_required)
        
        return True
        
    except ValueError as e:
        logger.error(f"配置验证失败: {e}")
        return False
