"""
兼容层：record_test_run.py

此文件已迁移至 execution.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.execution import ...

迁移日期: 2026-04-11
"""

from tools.execution import (
    TestRunRecorder,
    TestCaseExecutor,
)

__all__ = [
    "TestRunRecorder",
    "TestCaseExecutor",
]
