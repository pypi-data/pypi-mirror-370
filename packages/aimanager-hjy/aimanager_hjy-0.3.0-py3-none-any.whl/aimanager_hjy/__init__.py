"""
aimanager_hjy - AI服务管理包

统一的AI模型调用接口，提供标准化的AI服务管理功能。
"""

from .core.manager import AIManager
from .core.config import get_config, AppConfig, init
from .core.database import get_db_connection
from .core.file_upload import upload_file
from .core.validation import validate_required_fields
from .core.route import run_route, run_once, run

__version__ = "0.1.5"
__author__ = "hjy"
__email__ = "hjy@example.com"

__all__ = [
    "AIManager",
    "get_config",
    "AppConfig",
    "init",
    "get_db_connection",
    "upload_file",
    "validate_required_fields",
    "run_route",
    "run_once",
    "run",
]
