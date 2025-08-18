"""
AI管理器核心类
"""

from typing import Any, Dict, Optional
from loguru import logger
from .config import AppConfig, get_config, init
from .route import run_route, run_once, run
from .file_upload import upload_file, upload_bytes, delete_file, get_file_info
from .database import get_db_connection, test_db_connection
from .validation import validate_required_fields, validate_config


class AIManager:
    """
    AI服务管理器
    
    提供统一的AI服务调用接口，包括配置管理、文件上传、数据库连接等功能。
    """
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化AI管理器
        
        Args:
            config_path: 配置文件路径
            config_dict: 配置字典
        """
        try:
            if config_dict:
                self.config = init(config_dict)
            else:
                self.config = get_config(config_path)
            logger.info("AIManager初始化成功")
        except Exception as e:
            logger.error(f"AIManager初始化失败: {e}")
            raise
    
    def run_route(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用AI服务路由
        
        Args:
            route_name: 路由名称，如 "dogvoice.analysis.s2"
            params: 参数字典
            
        Returns:
            Dict[str, Any]: 调用结果
        """
        return run_route(route_name, params, self.config)
    
    def run_once(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行一次性AI调用
        
        Args:
            route_name: 路由名称
            params: 参数字典
            
        Returns:
            Dict[str, Any]: 调用结果
        """
        return run_once(route_name, params, self.config)
    
    def run(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行AI调用（别名）
        
        Args:
            route_name: 路由名称
            params: 参数字典
            
        Returns:
            Dict[str, Any]: 调用结果
        """
        return run(route_name, params, self.config)
    
    def upload_file(self, file_path: str, prefix: str = "") -> Optional[str]:
        """
        上传文件到OSS
        
        Args:
            file_path: 本地文件路径
            prefix: OSS路径前缀
            
        Returns:
            str: 文件URL，失败时返回None
        """
        return upload_file(file_path, prefix, self.config)
    
    def upload_bytes(self, data: bytes, file_name: str, prefix: str = "") -> Optional[str]:
        """
        上传字节数据到OSS
        
        Args:
            data: 字节数据
            file_name: 文件名
            prefix: OSS路径前缀
            
        Returns:
            str: 文件URL，失败时返回None
        """
        return upload_bytes(data, file_name, prefix, self.config)
    
    def delete_file(self, file_url: str) -> bool:
        """
        删除OSS文件
        
        Args:
            file_url: 文件URL
            
        Returns:
            bool: 删除是否成功
        """
        return delete_file(file_url, self.config)
    
    def get_file_info(self, file_url: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_url: 文件URL
            
        Returns:
            Dict[str, Any]: 文件信息，失败时返回None
        """
        return get_file_info(file_url, self.config)
    
    def get_db_connection(self):
        """
        获取数据库连接
        
        Returns:
            数据库连接对象
        """
        return get_db_connection(self.config)
    
    def test_db_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        return test_db_connection(self.config)
    
    def validate_config(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 配置是否有效
        """
        config_dict = {
            'database': {
                'host': self.config.database.host,
                'port': self.config.database.port,
                'name': self.config.database.name,
                'user': self.config.database.user,
                'password': self.config.database.password
            },
            'oss': {
                'access_key_id': self.config.oss.access_key_id,
                'access_key_secret': self.config.oss.access_key_secret,
                'endpoint': self.config.oss.endpoint,
                'bucket': self.config.oss.bucket
            },
            'ai_service': {
                'url': self.config.ai_service.url,
                'timeout': self.config.ai_service.timeout
            }
        }
        return validate_config(config_dict)
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        result = {
            'config_valid': False,
            'db_connected': False,
            'ai_service_accessible': False,
            'overall_healthy': False
        }
        
        try:
            # 检查配置
            result['config_valid'] = self.validate_config()
            
            # 检查数据库连接
            result['db_connected'] = self.test_db_connection()
            
            # 检查AI服务
            result['ai_service_accessible'] = self._test_ai_service()
            
            # 整体健康状态
            result['overall_healthy'] = all([
                result['config_valid'],
                result['db_connected'],
                result['ai_service_accessible']
            ])
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
        
        return result
    
    def _test_ai_service(self) -> bool:
        """
        测试AI服务连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            import httpx
            with httpx.Client(timeout=5) as client:
                response = client.get(self.config.ai_service.url)
                return response.status_code in [200, 404, 405]
        except Exception:
            return False
    
    def get_config(self) -> AppConfig:
        """
        获取当前配置
        
        Returns:
            AppConfig: 当前配置对象
        """
        return self.config
    
    def update_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        更新配置
        
        Args:
            config_dict: 新配置字典
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证新配置
            if not validate_config(config_dict):
                return False
            
            # 重新初始化配置
            self.config = get_config()
            logger.info("配置更新成功")
            return True
            
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            return False
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        验证必需字段
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            bool: 验证是否通过
        """
        return validate_required_fields(data, required_fields)
