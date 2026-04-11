"""
兼容层：bad_case_manager.py

此文件已迁移至 reporting.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.reporting import ...

迁移日期: 2026-04-11
"""

from tools.reporting import (
    BadCaseManager,
    DIMENSION_NAMES,
)

__all__ = [
    "BadCaseManager",
    "DIMENSION_NAMES",
]
