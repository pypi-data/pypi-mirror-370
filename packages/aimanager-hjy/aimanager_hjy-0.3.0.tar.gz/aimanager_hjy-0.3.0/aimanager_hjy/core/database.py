"""
数据库连接模块
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional
from loguru import logger
from .config import AppConfig


def get_db_connection(config: AppConfig):
    """
    获取数据库连接
    
    Args:
        config: 应用配置
        
    Returns:
        Connection: 数据库连接对象，失败时返回None
    """
    try:
        connection = mysql.connector.connect(
            host=config.database.host,
            port=config.database.port,
            database=config.database.name,
            user=config.database.user,
            password=config.database.password,
            autocommit=False,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            logger.info("数据库连接成功")
            return connection
        else:
            logger.error("数据库连接失败")
            return None
            
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None


def test_db_connection(config: AppConfig) -> bool:
    """
    测试数据库连接
    
    Args:
        config: 应用配置
        
    Returns:
        bool: 连接是否成功
    """
    connection = get_db_connection(config)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            connection.close()
            logger.info("数据库连接测试成功")
            return True
        except Error as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    return False


def execute_query(connection, query: str, params: Optional[tuple] = None) -> Optional[list]:
    """
    执行查询
    
    Args:
        connection: 数据库连接
        query: SQL查询语句
        params: 查询参数
        
    Returns:
        list: 查询结果，失败时返回None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as e:
        logger.error(f"查询执行失败: {e}")
        return None


def execute_update(connection, query: str, params: Optional[tuple] = None) -> bool:
    """
    执行更新操作
    
    Args:
        connection: 数据库连接
        query: SQL更新语句
        params: 更新参数
        
    Returns:
        bool: 执行是否成功
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        logger.error(f"更新执行失败: {e}")
        connection.rollback()
        return False
