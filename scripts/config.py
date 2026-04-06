"""
全局配置模块

集中管理所有配置常量，避免硬编码

作者: BighuaBighua
日期: 2026-04-06
版本: 1.0
"""

# ==================== 模型配置 ====================

# 被测模型
MODEL_UNDER_TEST = "ernie-4.5-turbo-128k"

# 评测模型
EVALUATOR_MODEL = "ernie-4.5-turbo-128k"

# API 端点
API_ENDPOINT = "https://qianfan.baidubce.com/v2/chat/completions"

# ==================== API 配置 ====================

# API 超时时间（秒）
API_TIMEOUT = 60

# API 温度参数
API_TEMPERATURE = 0.7

# API Top-P 参数
API_TOP_P = 0.9

# ==================== 执行配置 ====================

# 单线程执行延迟（秒）
SINGLE_THREAD_DELAY = 2.0

# 并发执行延迟（秒）
CONCURRENT_DELAY = 0.5

# 最大并发数建议
MAX_CONCURRENT_SUGGESTION = 2

# ==================== 测试配置 ====================

# 质量门阈值（通过率）
QUALITY_GATE_THRESHOLD = 0.9

# ==================== 文件路径配置 ====================

# 默认用例文件
DEFAULT_TEST_CASES_FILE = "projects/01-ai-customer-service/cases/universal.json"

# 默认评测模板
DEFAULT_EVALUATOR_TEMPLATE = "templates/customer-service-evaluator.md"

# 默认结果目录
DEFAULT_RESULTS_DIR = "projects/01-ai-customer-service/results"


# ==================== 辅助函数 ====================

def get_model_config() -> dict:
    """
    获取模型配置字典
    
    Returns:
        dict: 模型配置
    """
    return {
        "model": MODEL_UNDER_TEST,
        "evaluator_model": EVALUATOR_MODEL,
        "api_endpoint": API_ENDPOINT
    }


def get_api_config() -> dict:
    """
    获取 API 配置字典
    
    Returns:
        dict: API 配置
    """
    return {
        "timeout": API_TIMEOUT,
        "temperature": API_TEMPERATURE,
        "top_p": API_TOP_P
    }


def get_execution_config() -> dict:
    """
    获取执行配置字典
    
    Returns:
        dict: 执行配置
    """
    return {
        "single_thread_delay": SINGLE_THREAD_DELAY,
        "concurrent_delay": CONCURRENT_DELAY,
        "max_concurrent_suggestion": MAX_CONCURRENT_SUGGESTION
    }
