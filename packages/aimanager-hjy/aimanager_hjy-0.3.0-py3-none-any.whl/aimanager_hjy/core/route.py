"""
路由模块 - AI服务调用
"""

import json
import time
import uuid
from typing import Any, Dict, Optional, Tuple
import httpx
from loguru import logger
from .config import AppConfig, get_config
from .database import get_db_connection


def run_route(route_name: str, params: Optional[Dict[str, Any]] = None, config: Optional[AppConfig] = None) -> Dict[str, Any]:
    """
    调用AI服务路由
    
    Args:
        route_name: 路由名称，如 "dogvoice.analysis.s2"
        params: 参数字典
        config: 应用配置
        
    Returns:
        Dict[str, Any]: 调用结果
    """
    try:
        if config is None:
            config = get_config()
        
        # 解析路由名称
        if '.' not in route_name:
            raise ValueError("路由名称格式错误，应为 'project.route' 格式")
        
        project, route_key = route_name.split('.', 1)
        
        # 构建请求
        url, headers, body = _build_request(project, route_key, params, config)
        
        # 执行请求
        status, response = _execute_request(url, headers, body, config)
        
        # 记录日志
        _log_request(route_name, params, status, response, config)
        
        return {
            'success': status == 200,
            'status': status,
            'data': response,
            'route_name': route_name
        }
        
    except Exception as e:
        logger.error(f"路由调用失败: {e}")
        return {
            'success': False,
            'status': 500,
            'error': str(e),
            'route_name': route_name
        }


def run_once(route_name: str, params: Optional[Dict[str, Any]] = None, config: Optional[AppConfig] = None) -> Dict[str, Any]:
    """
    执行一次性AI调用
    
    Args:
        route_name: 路由名称
        params: 参数字典
        config: 应用配置
        
    Returns:
        Dict[str, Any]: 调用结果
    """
    return run_route(route_name, params, config)


def run(route_name: str, params: Optional[Dict[str, Any]] = None, config: Optional[AppConfig] = None) -> Dict[str, Any]:
    """
    执行AI调用（别名）
    
    Args:
        route_name: 路由名称
        params: 参数字典
        config: 应用配置
        
    Returns:
        Dict[str, Any]: 调用结果
    """
    return run_route(route_name, params, config)


def _build_request(project: str, route_key: str, params: Optional[Dict[str, Any]], config: AppConfig) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    """
    构建请求
    
    Args:
        project: 项目名称
        route_key: 路由键
        params: 参数字典
        config: 应用配置
        
    Returns:
        Tuple[str, Dict[str, str], Dict[str, Any]]: URL, 请求头, 请求体
    """
    # 构建URL
    base_url = config.ai_service.url.rstrip('/')
    url = f"{base_url}/api/v1/{project}/{route_key}"
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'aimanager_hjy/0.1.0',
        'X-Request-ID': str(uuid.uuid4()),
        'X-Trace-ID': str(uuid.uuid4())
    }
    
    # 构建请求体
    body = {
        'timestamp': int(time.time()),
        'params': params or {}
    }
    
    return url, headers, body


def _execute_request(url: str, headers: Dict[str, str], body: Dict[str, Any], config: AppConfig) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    执行HTTP请求
    
    Args:
        url: 请求URL
        headers: 请求头
        body: 请求体
        config: 应用配置
        
    Returns:
        Tuple[int, Optional[Dict[str, Any]]]: 状态码, 响应数据
    """
    try:
        with httpx.Client(timeout=config.ai_service.timeout) as client:
            response = client.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                try:
                    return response.status_code, response.json()
                except json.JSONDecodeError:
                    return response.status_code, {'text': response.text}
            else:
                logger.error(f"请求失败: {response.status_code} - {response.text}")
                return response.status_code, None
                
    except httpx.TimeoutException:
        logger.error(f"请求超时: {url}")
        return 408, None
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        return 500, None
    except Exception as e:
        logger.error(f"请求异常: {e}")
        return 500, None


def _log_request(route_name: str, params: Optional[Dict[str, Any]], status: int, response: Optional[Dict[str, Any]], config: AppConfig) -> None:
    """
    记录请求日志
    
    Args:
        route_name: 路由名称
        params: 参数字典
        status: 状态码
        response: 响应数据
        config: 应用配置
    """
    try:
        connection = get_db_connection(config)
        if connection:
            cursor = connection.cursor()
            
            # 插入日志记录
            log_data = {
                'route_name': route_name,
                'params': json.dumps(params or {}),
                'status': status,
                'response': json.dumps(response or {}),
                'timestamp': int(time.time())
            }
            
            query = """
                INSERT INTO ai_call_logs (route_name, params, status, response, timestamp)
                VALUES (%(route_name)s, %(params)s, %(status)s, %(response)s, %(timestamp)s)
            """
            
            cursor.execute(query, log_data)
            connection.commit()
            cursor.close()
            connection.close()
            
    except Exception as e:
        logger.warning(f"日志记录失败: {e}")


def test_route(route_name: str, config: Optional[AppConfig] = None) -> bool:
    """
    测试路由连接
    
    Args:
        route_name: 路由名称
        config: 应用配置
        
    Returns:
        bool: 连接是否成功
    """
    try:
        if config is None:
            config = get_config()
        
        # 解析路由名称
        if '.' not in route_name:
            return False
        
        project, route_key = route_name.split('.', 1)
        
        # 构建测试URL
        base_url = config.ai_service.url.rstrip('/')
        url = f"{base_url}/api/v1/{project}/{route_key}"
        
        # 发送测试请求
        with httpx.Client(timeout=5) as client:
            response = client.get(url)
            return response.status_code in [200, 404, 405]  # 404和405表示路由存在但方法不对
            
    except Exception as e:
        logger.error(f"路由测试失败: {e}")
        return False
