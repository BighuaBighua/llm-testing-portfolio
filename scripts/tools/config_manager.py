"""
兼容层：config_manager.py

此文件已迁移至 config.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.config import ...

迁移日期: 2026-04-11
"""

from tools.config import (
    ConfigLoader,
    ConfigRegistry,
    EvaluationContext,
    ConfigManager,
    get_path,
    get_project_root,
    get_config_dir,
    get_config_manager,
    get_api_config,
    get_business_rules,
    get_test_generation_config,
    get_execution_config,
    get_model_config,
    get_evaluation_dimensions,
    get_model_under_test,
    get_evaluator_providers,
)

__all__ = [
    "ConfigLoader",
    "ConfigRegistry",
    "EvaluationContext",
    "ConfigManager",
    "get_path",
    "get_project_root",
    "get_config_dir",
    "get_config_manager",
    "get_api_config",
    "get_business_rules",
    "get_test_generation_config",
    "get_execution_config",
    "get_model_config",
    "get_evaluation_dimensions",
    "get_model_under_test",
    "get_evaluator_providers",
]
