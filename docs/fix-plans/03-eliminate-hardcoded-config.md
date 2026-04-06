# 任务3：消除硬编码配置

> **优先级**: 中
> **预计工作量**: 1小时
> **涉及文件**: `scripts/run_tests.py`

---

## 问题描述

**当前问题**：
- 模型名 `ernie-4.5-turbo-128k` 在多处硬编码
- API URL、延迟时间等配置分散在代码中
- 修改配置需要改动多处代码

**影响**：
- 难以切换模型
- 难以调整配置
- 代码维护性差

---

## 硬编码位置统计

### 位置1：模型名（7处）

**文件**: `scripts/run_tests.py`

```python
# 第157行
self.model = "ernie-4.5-turbo-128k"  # ❌ 硬编码

# 第602行
"model": self.model  # ✅ 使用变量

# 第645行
"evaluator_model": self.model  # ✅ 使用变量

# 第954行
model="ernie-4.5-turbo-128k",  # ❌ 硬编码

# 第955行
evaluator_model="ernie-4.5-turbo-128k",  # ❌ 硬编码
```

### 位置2：API URL（1处）

```python
# 第156行
self.api_url = "https://qianfan.baidubce.com/v2/chat/completions"  # ❌ 硬编码
```

### 位置3：延迟时间（2处）

```python
# 第497行
time.sleep(2)  # ❌ 硬编码

# 第579行
time.sleep(0.5)  # ❌ 硬编码
```

---

## 修改方案

### 步骤1：创建配置常量模块

**新建文件**: `scripts/config.py`

```python
"""
全局配置模块

集中管理所有配置常量
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
```

### 步骤2：修改 run_tests.py 使用配置

**文件**: `scripts/run_tests.py`

**在文件开头导入配置**：

```python
from config import (
    MODEL_UNDER_TEST,
    EVALUATOR_MODEL,
    API_ENDPOINT,
    API_TIMEOUT,
    API_TEMPERATURE,
    API_TOP_P,
    SINGLE_THREAD_DELAY,
    CONCURRENT_DELAY,
    MAX_CONCURRENT_SUGGESTION,
    DEFAULT_TEST_CASES_FILE,
    DEFAULT_EVALUATOR_TEMPLATE,
    DEFAULT_RESULTS_DIR
)
```

**修改第157行**：

```python
# 修改前
self.model = "ernie-4.5-turbo-128k"

# 修改后
self.model = MODEL_UNDER_TEST
```

**修改第156行**：

```python
# 修改前
self.api_url = "https://qianfan.baidubce.com/v2/chat/completions"

# 修改后
self.api_url = API_ENDPOINT
```

**修改第347-349行**：

```python
# 修改前
"temperature": 0.7,
"top_p": 0.9

# 修改后
"temperature": API_TEMPERATURE,
"top_p": API_TOP_P
```

**修改第356行**：

```python
# 修改前
timeout=60

# 修改后
timeout=API_TIMEOUT
```

**修改第497行**：

```python
# 修改前
time.sleep(2)

# 修改后
time.sleep(SINGLE_THREAD_DELAY)
```

**修改第579行**：

```python
# 修改前
time.sleep(0.5)

# 修改后
time.sleep(CONCURRENT_DELAY)
```

**修改第954-955行**：

```python
# 修改前
model="ernie-4.5-turbo-128k",
evaluator_model="ernie-4.5-turbo-128k",

# 修改后
model=MODEL_UNDER_TEST,
evaluator_model=EVALUATOR_MODEL,
```

---

## 修改对比

| 修改前 | 修改后 |
|--------|--------|
| ❌ 7处硬编码模型名 | ✅ 1处配置常量 |
| ❌ 修改需要改7处 | ✅ 修改只需改1处 |
| ❌ 配置分散难维护 | ✅ 配置集中易管理 |
| ❌ 无法快速切换模型 | ✅ 修改配置即可切换 |

---

## 使用示例

### 示例1：切换模型

**只需修改 `config.py`**：

```python
# 切换到新模型
MODEL_UNDER_TEST = "ernie-4.8-turbo-256k"
EVALUATOR_MODEL = "ernie-4.8-turbo-256k"
```

**无需修改其他代码**！

### 示例2：调整延迟

```python
# 调整 API 调用延迟
SINGLE_THREAD_DELAY = 3.0  # 从 2 秒改为 3 秒
CONCURRENT_DELAY = 1.0      # 从 0.5 秒改为 1 秒
```

---

## 预计工作量

- 创建配置模块: 20 分钟
- 修改 run_tests.py: 30 分钟
- 测试验证: 10 分钟
- **总计**: 1 小时

---

## 修复效果

✅ 配置集中管理
✅ 修改配置只需1处
✅ 易于切换模型
✅ 提高代码可维护性
✅ 符合 DRY 原则（Don't Repeat Yourself）

---

*创建时间: 2026-04-06*
