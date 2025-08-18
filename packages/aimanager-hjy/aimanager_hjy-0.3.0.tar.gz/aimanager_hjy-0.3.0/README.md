# aimanager_hjy

AI服务管理包 - 统一的AI模型调用接口

## 简介

`aimanager_hjy` 是一个统一的AI服务管理包，提供标准化的AI模型调用接口。它是 `ai_runner_hjy` 的升级版本，采用更规范的命名和更完善的功能。

## 主要功能

- **统一AI调用接口**: 通过 `run_route()` 方法调用各种AI服务
- **配置管理**: 支持多种配置方式（环境变量、配置文件、数据库）
- **文件上传**: 集成OSS存储，支持文件上传和管理
- **数据库连接**: 内置MySQL连接管理
- **错误处理**: 完善的错误处理和重试机制
- **日志记录**: 集成loguru日志系统

## 安装

```bash
pip install aimanager_hjy
```

## 快速开始

### 基本使用

```python
from aimanager_hjy import AIManager

# 初始化AI管理器
ai_manager = AIManager()

# 调用AI服务
result = ai_manager.run_route("dogvoice.analysis.s2", {
    "audio_url": "https://example.com/audio.mp3",
    "user_id": "user_123"
})

print(result)
```

### 配置管理

```python
from aimanager_hjy import get_config

# 获取配置
config = get_config()
print(config.database.host)
print(config.oss.bucket)
```

### 文件上传

```python
from aimanager_hjy import upload_file

# 上传文件到OSS
file_url = upload_file("audio.mp3", "audio/")
print(f"文件已上传到: {file_url}")
```

## 配置说明

### 环境变量配置

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dogvoice
DB_USER=root
DB_PASSWORD=password

# OSS配置
OSS_ACCESS_KEY_ID=your_access_key
OSS_ACCESS_KEY_SECRET=your_secret_key
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=your_bucket

# AI服务配置
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_TIMEOUT=30
```

### 配置文件

创建 `config.yaml` 文件：

```yaml
database:
  host: localhost
  port: 3306
  name: dogvoice
  user: root
  password: password

oss:
  access_key_id: your_access_key
  access_key_secret: your_secret_key
  endpoint: oss-cn-hangzhou.aliyuncs.com
  bucket: your_bucket

ai_service:
  url: http://localhost:8000
  timeout: 30
  retry_count: 3
```

## API参考

### AIManager类

#### `__init__(config_path: str = None)`
初始化AI管理器

#### `run_route(route_name: str, params: dict = None) -> dict`
调用AI服务路由

- `route_name`: 路由名称，如 "dogvoice.analysis.s2"
- `params`: 参数字典

#### `run_once(route_name: str, params: dict = None) -> dict`
执行一次性AI调用

#### `run(route_name: str, params: dict = None) -> dict`
执行AI调用（别名）

### 工具函数

#### `get_config() -> AppConfig`
获取应用配置

#### `get_db_connection() -> Connection`
获取数据库连接

#### `upload_file(file_path: str, prefix: str = "") -> str`
上传文件到OSS

#### `validate_required_fields(data: dict, required_fields: list) -> bool`
验证必需字段

## 迁移指南

### 从 ai_runner_hjy 迁移

```python
# 旧代码
from ai_runner_hjy import AIRunner, run_route

runner = AIRunner()
result = run_route("dogvoice.analysis.s2", params)

# 新代码
from aimanager_hjy import AIManager, run_route

manager = AIManager()
result = run_route("dogvoice.analysis.s2", params)
```

## 开发

### 安装开发依赖

```bash
pip install -e .[dev]
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black aimanager_hjy/
isort aimanager_hjy/
```

## 许可证

MIT License

## 更新日志

### v0.1.0
- 初始版本
- 基于 ai_runner_hjy 重构
- 统一命名规范
- 完善文档和示例
