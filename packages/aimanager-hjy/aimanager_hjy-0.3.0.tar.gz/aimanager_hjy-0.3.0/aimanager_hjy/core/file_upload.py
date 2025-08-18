"""
文件上传模块
"""

import os
import uuid
from datetime import datetime
from typing import Optional
import oss2
from loguru import logger
from .config import AppConfig


def upload_file(file_path: str, prefix: str = "", config: Optional[AppConfig] = None) -> Optional[str]:
    """
    上传文件到OSS
    
    Args:
        file_path: 本地文件路径
        prefix: OSS路径前缀
        config: 应用配置，如果为None则使用默认配置
        
    Returns:
        str: 文件URL，失败时返回None
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None
            
        if config is None:
            from .config import get_config
            config = get_config()
        
        # 创建OSS客户端
        auth = oss2.Auth(config.oss.access_key_id, config.oss.access_key_secret)
        bucket = oss2.Bucket(auth, config.oss.endpoint, config.oss.bucket)
        
        # 生成OSS对象名
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        oss_key = f"{prefix}{timestamp}_{unique_id}{file_ext}"
        
        # 上传文件
        with open(file_path, 'rb') as f:
            result = bucket.put_object(oss_key, f)
            
        if result.status == 200:
            file_url = f"https://{config.oss.bucket}.{config.oss.endpoint}/{oss_key}"
            logger.info(f"文件上传成功: {file_url}")
            return file_url
        else:
            logger.error(f"文件上传失败: {result.status}")
            return None
            
    except Exception as e:
        logger.error(f"文件上传异常: {e}")
        return None


def upload_bytes(data: bytes, file_name: str, prefix: str = "", config: Optional[AppConfig] = None) -> Optional[str]:
    """
    上传字节数据到OSS
    
    Args:
        data: 字节数据
        file_name: 文件名
        prefix: OSS路径前缀
        config: 应用配置
        
    Returns:
        str: 文件URL，失败时返回None
    """
    try:
        if config is None:
            from .config import get_config
            config = get_config()
        
        # 创建OSS客户端
        auth = oss2.Auth(config.oss.access_key_id, config.oss.access_key_secret)
        bucket = oss2.Bucket(auth, config.oss.endpoint, config.oss.bucket)
        
        # 生成OSS对象名
        file_ext = os.path.splitext(file_name)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        oss_key = f"{prefix}{timestamp}_{unique_id}{file_ext}"
        
        # 上传数据
        result = bucket.put_object(oss_key, data)
        
        if result.status == 200:
            file_url = f"https://{config.oss.bucket}.{config.oss.endpoint}/{oss_key}"
            logger.info(f"数据上传成功: {file_url}")
            return file_url
        else:
            logger.error(f"数据上传失败: {result.status}")
            return None
            
    except Exception as e:
        logger.error(f"数据上传异常: {e}")
        return None


def delete_file(file_url: str, config: Optional[AppConfig] = None) -> bool:
    """
    删除OSS文件
    
    Args:
        file_url: 文件URL
        config: 应用配置
        
    Returns:
        bool: 删除是否成功
    """
    try:
        if config is None:
            from .config import get_config
            config = get_config()
        
        # 从URL中提取OSS对象名
        if config.oss.bucket in file_url and config.oss.endpoint in file_url:
            oss_key = file_url.split(f"{config.oss.bucket}.{config.oss.endpoint}/")[1]
        else:
            logger.error("无法从URL中提取OSS对象名")
            return False
        
        # 创建OSS客户端
        auth = oss2.Auth(config.oss.access_key_id, config.oss.access_key_secret)
        bucket = oss2.Bucket(auth, config.oss.endpoint, config.oss.bucket)
        
        # 删除文件
        result = bucket.delete_object(oss_key)
        
        if result.status == 204:
            logger.info(f"文件删除成功: {oss_key}")
            return True
        else:
            logger.error(f"文件删除失败: {result.status}")
            return False
            
    except Exception as e:
        logger.error(f"文件删除异常: {e}")
        return False


def get_file_info(file_url: str, config: Optional[AppConfig] = None) -> Optional[dict]:
    """
    获取文件信息
    
    Args:
        file_url: 文件URL
        config: 应用配置
        
    Returns:
        dict: 文件信息，失败时返回None
    """
    try:
        if config is None:
            from .config import get_config
            config = get_config()
        
        # 从URL中提取OSS对象名
        if config.oss.bucket in file_url and config.oss.endpoint in file_url:
            oss_key = file_url.split(f"{config.oss.bucket}.{config.oss.endpoint}/")[1]
        else:
            logger.error("无法从URL中提取OSS对象名")
            return None
        
        # 创建OSS客户端
        auth = oss2.Auth(config.oss.access_key_id, config.oss.access_key_secret)
        bucket = oss2.Bucket(auth, config.oss.endpoint, config.oss.bucket)
        
        # 获取文件信息
        info = bucket.head_object(oss_key)
        
        return {
            'size': info.content_length,
            'last_modified': info.last_modified,
            'etag': info.etag,
            'content_type': info.content_type
        }
        
    except Exception as e:
        logger.error(f"获取文件信息异常: {e}")
        return None
