"""
兼容层：evaluator_prompt_assembler.py

此文件已迁移至 evaluation.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.evaluation import ...

迁移日期: 2026-04-11
"""

from tools.evaluation import (
    EvaluatorPromptAssembler,
)

__all__ = [
    "EvaluatorPromptAssembler",
]
