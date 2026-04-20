"""
公共工具模块 V1.0

职责：
1. 统一异常类定义
2. 日志配置和管理
3. 通用辅助函数

日期: 2026-04-11
版本: 1.0
"""

import json
import logging
import os
from typing import Any, Dict, Optional


# ============================================================================
# 第一部分：统一异常类
# ============================================================================

class TestingFrameworkError(Exception):
    """测试框架基础异常

    所有框架内自定义异常的基类，支持附加结构化详情信息。
    子类包括：ConfigError、ExecutionError、EvaluationError、APIError、ValidationError、ReportingError
    """

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} | 详情: {self.details}"
        return self.message


class ConfigError(TestingFrameworkError):
    """配置相关错误 - 配置文件缺失、格式错误、字段缺失等场景"""
    pass


class ExecutionError(TestingFrameworkError):
    """执行相关错误 - 测试执行中断、超时、并发异常等场景"""
    pass


class EvaluationError(TestingFrameworkError):
    """评测相关错误 - 评测独立性违规、解析失败、结果异常等场景"""
    pass


class APIError(TestingFrameworkError):
    """API调用相关错误 - 请求失败、响应异常、认证错误等场景"""
    pass


class ValidationError(TestingFrameworkError):
    """数据验证相关错误 - 文件不存在、JSON格式错误、数据结构异常等场景"""
    pass


class ReportingError(TestingFrameworkError):
    """报告生成相关错误 - 报告写入失败、数据导出异常等场景"""
    pass


# ============================================================================
# 第二部分：日志配置
# ============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_loggers: Dict[str, logging.Logger] = {}
_logging_configured = False


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: str = LOG_FORMAT
) -> None:
    """
    统一日志配置（全局单次生效）

    首次调用时配置根日志器，后续调用无效（防止重复配置导致日志重复输出）。
    支持同时输出到控制台和文件。

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选，指定后同时输出到文件）
        format_string: 日志格式字符串
    """
    global _logging_configured

    if _logging_configured:
        return

    handlers = [logging.StreamHandler()]

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(
            logging.FileHandler(log_file, encoding='utf-8')
        )

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt=LOG_DATE_FORMAT,
        handlers=handlers
    )

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（带缓存，避免重复创建）

    Args:
        name: 模块名称（通常使用 __name__）

    Returns:
        日志记录器实例
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


# ============================================================================
# 第三部分：辅助函数
# ============================================================================

def ensure_dir(path: str) -> None:
    """
    确保目录存在，不存在则创建

    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


def load_json(path: str) -> Dict[str, Any]:
    """
    加载JSON文件

    Args:
        path: JSON文件路径

    Returns:
        解析后的字典

    Raises:
        ValidationError: 文件不存在或格式错误
    """
    if not os.path.exists(path):
        raise ValidationError(
            f"JSON文件不存在: {path}",
            details={"file_path": path}
        )

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"JSON文件格式错误: {path}",
            details={"file_path": path, "error": str(e)}
        )


def save_json(data: Dict[str, Any], path: str, indent: int = 2) -> None:
    """
    保存数据到JSON文件

    Args:
        data: 要保存的数据
        path: JSON文件路径
        indent: 缩进空格数
    """
    dir_path = os.path.dirname(path)
    if dir_path:
        ensure_dir(dir_path)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_text(path: str) -> str:
    """
    加载文本文件

    Args:
        path: 文本文件路径

    Returns:
        文件内容

    Raises:
        ValidationError: 文件不存在
    """
    if not os.path.exists(path):
        raise ValidationError(
            f"文本文件不存在: {path}",
            details={"file_path": path}
        )

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_text(content: str, path: str) -> None:
    """
    保存文本到文件

    Args:
        content: 文本内容
        path: 文件路径
    """
    dir_path = os.path.dirname(path)
    if dir_path:
        ensure_dir(dir_path)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_project_root() -> str:
    """
    获取项目根目录

    Returns:
        项目根目录的绝对路径
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(this_dir, "..", ".."))


def get_config_dir() -> str:
    """
    获取配置目录

    Returns:
        配置目录的绝对路径
    """
    return os.path.join(get_project_root(), "configs")


def get_templates_dir() -> str:
    """
    获取模板目录

    Returns:
        模板目录的绝对路径
    """
    return os.path.join(get_project_root(), "templates")


def get_projects_dir() -> str:
    """
    获取项目数据目录

    Returns:
        项目数据目录的绝对路径
    """
    return os.path.join(get_project_root(), "projects")
