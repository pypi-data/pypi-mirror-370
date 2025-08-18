"""
配置管理模块
"""

import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from loguru import logger


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=3306, description="数据库端口")
    name: str = Field(default="dogvoice", description="数据库名称")
    user: str = Field(default="root", description="数据库用户名")
    password: str = Field(default="", description="数据库密码")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('端口必须在1-65535之间')
        return v


class OSSConfig(BaseModel):
    """OSS配置"""
    access_key_id: str = Field(description="OSS访问密钥ID")
    access_key_secret: str = Field(description="OSS访问密钥")
    endpoint: str = Field(default="oss-cn-hangzhou.aliyuncs.com", description="OSS端点")
    bucket: str = Field(description="OSS存储桶名称")


class AIServiceConfig(BaseModel):
    """AI服务配置"""
    url: str = Field(default="http://localhost:8000", description="AI服务URL")
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    retry_count: int = Field(default=3, description="重试次数")
    retry_delay: int = Field(default=1, description="重试延迟(秒)")


class AppConfig(BaseSettings):
    """应用配置"""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    oss: OSSConfig = Field(description="OSS配置")
    ai_service: AIServiceConfig = Field(default_factory=AIServiceConfig)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


def get_config(config_path: Optional[str] = None) -> AppConfig:
    """
    获取应用配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        AppConfig: 应用配置对象
    """
    try:
        if config_path and os.path.exists(config_path):
            config = AppConfig(_env_file=config_path)
        else:
            config = AppConfig()
        
        logger.info("配置加载成功")
        return config
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        raise


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


def init(config_dict: Dict[str, Any]) -> AppConfig:
    """
    从字典初始化配置
    
    Args:
        config_dict: 配置字典
        
    Returns:
        AppConfig: 应用配置对象
    """
    try:
        config = AppConfig(_env_file=None, **config_dict)
        logger.info("配置初始化成功")
        return config
    except Exception as e:
        logger.error(f"配置初始化失败: {e}")
        raise
