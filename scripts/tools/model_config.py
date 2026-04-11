"""
兼容层：model_config.py

此文件已迁移至 config.py，保留此文件仅为向后兼容。
新代码请直接使用：from tools.config import ...

迁移日期: 2026-04-11
"""

import os
from typing import Dict, List

from tools.config import (
    get_path,
    PROJECT_ROOT,
    MODEL_UNDER_TEST,
    API_ENDPOINT,
    get_api_key,
    get_evaluator_providers,
    EVALUATOR_PROVIDERS,
    EVALUATOR_MODEL,
    EVALUATOR_API_ENDPOINT,
    BUSINESS_SCENARIO,
    BUSINESS_SCOPE,
    API_TIMEOUT,
    API_TEMPERATURE,
    API_TOP_P,
    SINGLE_THREAD_DELAY,
    CONCURRENT_DELAY,
    MAX_CONCURRENT_SUGGESTION,
    QUALITY_GATE_THRESHOLD,
    DIMENSION_CODE_MAP,
    DIMENSION_NAMES,
    EVALUATION_DIMENSIONS,
    get_test_cases_path,
    get_evaluator_template_path,
    get_results_dir,
    get_model_config,
    get_api_config,
    get_execution_config,
)

__all__ = [
    "PROJECT_ROOT",
    "MODEL_UNDER_TEST",
    "API_ENDPOINT",
    "get_api_key",
    "get_evaluator_providers",
    "EVALUATOR_PROVIDERS",
    "EVALUATOR_MODEL",
    "EVALUATOR_API_ENDPOINT",
    "BUSINESS_SCENARIO",
    "BUSINESS_SCOPE",
    "API_TIMEOUT",
    "API_TEMPERATURE",
    "API_TOP_P",
    "SINGLE_THREAD_DELAY",
    "CONCURRENT_DELAY",
    "MAX_CONCURRENT_SUGGESTION",
    "QUALITY_GATE_THRESHOLD",
    "DIMENSION_CODE_MAP",
    "DIMENSION_NAMES",
    "EVALUATION_DIMENSIONS",
    "get_test_cases_path",
    "get_evaluator_template_path",
    "get_results_dir",
    "get_model_config",
    "get_api_config",
    "get_execution_config",
    "get_path",
]
