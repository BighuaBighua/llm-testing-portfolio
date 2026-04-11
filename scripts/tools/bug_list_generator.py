"""
兼容层：bug_list_generator.py

此文件已迁移至 reporting.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.reporting import ...

迁移日期: 2026-04-11
"""

from tools.reporting import (
    BugListGenerator,
    DIMENSION_NAMES,
)

__all__ = [
    "BugListGenerator",
    "DIMENSION_NAMES",
]
