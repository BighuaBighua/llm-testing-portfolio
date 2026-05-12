# API 统一调用客户端设计 — 重试/限流/日志/异常捕获

> 日期: 2026-04-27
> 状态: 待审核
> 版本: 1.0

---

## 1. 背景与问题

### 1.1 现状

当前项目中 API 调用存在以下问题：

| 问题 | 位置 | 说明 |
|------|------|------|
| 重试逻辑简陋 | `run_tests.py:253-273` | `_call_model_under_test` 用 for 循环 + 固定 `sleep(2)` 重试，无指数退避 |
| 评测模型同理 | `run_tests.py:275-301` | `_call_openai_compatible` 同样手动循环重试 |
| 无重试日志 | 上述两处 | 重试时只 `print` 一行，无结构化记录 |
| 无 HTTP 状态码分级 | 上述两处 | 400/401/403/429/5xx 无差异化处理 |
| 限流参数硬编码 | `run_tests.py:262,269,300` | `time.sleep(2)` 写死，无法通过配置调整 |
| YAML 配置未生效 | `execution.yaml:34-37` | 已定义 `retry.max_attempts/backoff_factor/max_delay` 但代码未使用 |
| 调用出口分散 | `run_tests.py` | 被测模型和评测模型各自实现重试/异常逻辑，规则不一致 |

### 1.2 目标

1. **统一出口** — 所有 API 调用走同一个客户端，重试/限流/日志/异常处理规则一致
2. **配置驱动** — 重试次数、退避因子、限流间隔等参数从 `execution.yaml` 读取，不再硬编码
3. **指数退避重试** — 使用 `urllib3.Retry` + `HTTPAdapter` 实现标准指数退避
4. **全链路日志** — 双轨制：`print` 管终端进度展示，`logger` 管结构化日志留痕
5. **请求前限流** — 每次 API 调用前 `time.sleep` 防止触发接口限流
6. **异常捕获完善** — HTTP 状态码分级处理 + 细粒度异常捕获

---

## 2. 影响文件清单

| 文件 | 操作 | 改动内容 |
|------|------|----------|
| `scripts/tools/api_client.py` | **新建** | APIClient 类：统一重试、限流、日志、异常捕获 |
| `scripts/run_tests.py` | **修改** | TestRunner 中 `_call_model_under_test` 和 `_call_openai_compatible` 改为调用 APIClient |
| `configs/execution.yaml` | **修改** | 新增 `rate_limit` 配置节，补充 `retry.status_forcelist` 和 `retry.no_retry_status_codes` |
| `scripts/tools/config.py` | **修改** | ConfigRegistry 新增 `retry_config` 和 `rate_limit_config` 属性 |

**总计：1 个新建文件 + 3 个修改文件**

无需修改的文件：
- `scripts/tools/utils.py` — 已有 `APIError` 和 `get_logger`，无需改动
- `requirements.txt` — `urllib3` 是 `requests` 的依赖，已间接安装

---

## 3. 配置扩展设计

### 3.1 execution.yaml 新增字段

在 `parameters` 节下新增 `retry.status_forcelist`、`retry.no_retry_status_codes` 和 `rate_limit` 配置：

```yaml
parameters:
  timing:
    api_timeout: 60
    case_timeout: 300
  retry:
    max_attempts: 3
    backoff_factor: 2
    max_delay: 60
    status_forcelist: [429, 500, 502, 503, 504]      # 触发重试的HTTP状态码
    no_retry_status_codes: [400, 401, 403]             # 不重试的HTTP状态码
  rate_limit:
    delay_between_calls: 1.0                            # API调用间隔（秒）
    delay_on_429: 10                                    # 429限流时额外等待（秒）
```

### 3.2 字段说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `retry.max_attempts` | int | 3 | 最大重试次数（对应 urllib3.Retry 的 total） |
| `retry.backoff_factor` | float | 2 | 退避因子，等待时间 = backoff_factor * (2 ** (retry_count - 1)) |
| `retry.max_delay` | int | 60 | 最大等待时间（秒），防止退避时间过长 |
| `retry.status_forcelist` | list | [429,500,502,503,504] | 触发自动重试的 HTTP 状态码 |
| `retry.no_retry_status_codes` | list | [400,401,403] | 不重试的 HTTP 状态码（客户端错误） |
| `rate_limit.delay_between_calls` | float | 1.0 | 每次 API 调用前的固定等待时间（秒） |
| `rate_limit.delay_on_429` | int | 10 | 遇到 429 限流响应时的额外等待时间（秒） |

### 3.3 ConfigRegistry 新增属性

在 `ConfigRegistry` 类中新增两个属性，让 APIClient 能从配置注册中心读取参数：

```python
@property
def retry_config(self) -> dict:
    """重试配置"""
    return self._execution_config.get("parameters", {}).get("retry", {
        "max_attempts": 3,
        "backoff_factor": 2,
        "max_delay": 60,
        "status_forcelist": [429, 500, 502, 503, 504],
        "no_retry_status_codes": [400, 401, 403],
    })

@property
def rate_limit_config(self) -> dict:
    """限流配置"""
    return self._execution_config.get("parameters", {}).get("rate_limit", {
        "delay_between_calls": 1.0,
        "delay_on_429": 10,
    })
```

---

## 4. APIClient 类设计

### 4.1 类结构

```
APIClient
├── __init__(config_registry)      — 读取配置，初始化 session 和限流状态
├── _create_session() -> Session   — urllib3.Retry + HTTPAdapter + session.mount()
├── _retry_log(retry_info)         — 重试日志回调（print + logger 双轨）
├── _rate_limit()                  — 请求前 time.sleep 限流
├── post(url, headers, json_body)  — 统一 POST 请求（被测模型）
└── call_openai(prompt, provider)  — OpenAI 兼容调用（评测模型）
```

### 4.2 `__init__` 初始化

```python
def __init__(self, config_registry=None):
    self._registry = config_registry
    self.logger = get_logger(__name__)

    # 读取重试配置
    if config_registry:
        retry_cfg = config_registry.retry_config
        rate_limit_cfg = config_registry.rate_limit_config
        timeout_cfg = config_registry.execution_config.get("parameters", {}).get("timing", {})
    else:
        retry_cfg = {}
        rate_limit_cfg = {}
        timeout_cfg = {}

    self._max_attempts = retry_cfg.get("max_attempts", 3)
    self._backoff_factor = retry_cfg.get("backoff_factor", 2)
    self._max_delay = retry_cfg.get("max_delay", 60)
    self._status_forcelist = retry_cfg.get("status_forcelist", [429, 500, 502, 503, 504])
    self._no_retry_status_codes = set(retry_cfg.get("no_retry_status_codes", [400, 401, 403]))

    self._delay_between_calls = rate_limit_cfg.get("delay_between_calls", 1.0)
    self._delay_on_429 = rate_limit_cfg.get("delay_on_429", 10)

    self._api_timeout = timeout_cfg.get("api_timeout", 60)

    # 创建带重试的 session
    self._session = self._create_session()

    # 限流状态
    self._last_call_time = 0.0
```

### 4.3 `_create_session` 创建带重试的 Session

```python
def _create_session(self) -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=self._max_attempts,
        backoff_factor=self._backoff_factor,
        allowed_methods=['POST', 'GET'],
        status_forcelist=self._status_forcelist,
        before_sleep=self._retry_log,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
```

**设计要点**：
- `urllib3.Retry` 自动处理指数退避：等待时间 = `backoff_factor * (2 ** (attempt - 1))`
- `before_sleep` 回调在每次重试前触发，用于记录重试日志
- `status_forcelist` 中的状态码会自动触发重试
- `allowed_methods` 限定 POST 和 GET 方法可重试

### 4.4 `_retry_log` 重试日志回调

```python
def _retry_log(self, retry_info):
    num = retry_info.total - retry_info.remaining
    status_code = 'unknown'
    if hasattr(retry_info, 'response') and retry_info.response is not None:
        status_code = retry_info.response.status_code
    wait_time = getattr(retry_info.next_action, 'sleep', 0) if hasattr(retry_info, 'next_action') else 0

    # 429 限流：在重试回调中额外等待，给服务端恢复窗口
    if status_code == 429:
        print(f"  ⚠️ 触发限流(429) | 额外等待 {self._delay_on_429}s")
        self.logger.warning(f"触发429限流 | 额外等待 {self._delay_on_429}s")
        time.sleep(self._delay_on_429)

    # print → 终端实时可见
    print(f"  ⚠️ 第{num}次重试 | 状态码: {status_code} | 等待: {wait_time:.1f}s")
    # logger → 日志文件留痕
    self.logger.warning(f"第{num}次重试 | 状态码: {status_code} | 等待: {wait_time:.1f}s")
```

**设计要点**：
- 429 在 `status_forcelist` 中，`urllib3.Retry` 会自动触发重试
- `before_sleep` 回调在重试前触发，是处理 429 额外等待的正确位置
- 不在 `post()` 主流程中处理 429，因为 429 响应会被 `urllib3` 底层拦截，不会到达 `post()` 的主流程

### 4.5 `_rate_limit` 请求前限流

```python
def _rate_limit(self):
    now = time.time()
    elapsed = now - self._last_call_time
    delay = self._delay_between_calls - elapsed

    if delay > 0:
        print(f"  ⏳ 限流等待: {delay:.1f}s")
        self.logger.debug(f"限流等待: {delay:.1f}s")
        time.sleep(delay)

    self._last_call_time = time.time()
```

**设计要点**：
- 记录上次调用时间，计算实际需要等待的时长
- 如果距离上次调用已超过 `delay_between_calls`，则无需等待
- `print` 输出等待提示，`logger.debug` 记录到日志

### 4.6 `post` 统一 POST 请求

```python
def post(self, url, headers, json_body, timeout=None) -> Optional[dict]:
    """统一 POST 请求

    流程：
    1. _rate_limit() 限流
    2. session.post() 发请求（urllib3 自动重试 status_forcelist 中的状态码）
    3. 手动检查 no_retry_status_codes（400/401/403 不重试，直接返回）
    4. 429 由 urllib3 自动重试，额外等待在 _retry_log 回调中处理
    5. 异常捕获：ConnectionError/HTTPError/JSONDecodeError/Exception

    Returns:
        成功时返回响应 JSON 字典，失败时返回 None
    """
    self._rate_limit()

    actual_timeout = timeout or self._api_timeout

    try:
        res = self._session.post(url=url, headers=headers, json=json_body, timeout=actual_timeout)
        status_code = res.status_code

        # 不重试的状态码：客户端错误
        if status_code in self._no_retry_status_codes:
            if status_code == 401:
                print("  ❌ 401 鉴权失败：API Key错误/过期/无权限")
                self.logger.error("401 鉴权失败：API Key错误/过期/无权限")
            elif status_code == 400:
                print("  ❌ 400 参数错误：请求格式/字段非法")
                self.logger.error("400 参数错误：请求格式/字段非法")
            elif status_code == 403:
                print("  ❌ 403 禁止访问")
                self.logger.error("403 禁止访问")
            return None

        res.raise_for_status()
        return res.json()

    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ 请求最终失败！网络异常，已触发最大重试次数")
        self.logger.error(f"ConnectionError: {e}", exc_info=True)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ 请求最终失败！HTTP异常，已触发最大重试次数")
        self.logger.error(f"HTTPError: {e}", exc_info=True)
        return None
    except JSONDecodeError as e:
        print(f"  ❌ 响应JSON解析失败")
        self.logger.error(f"JSONDecodeError: {e}", exc_info=True)
        return None
    except Exception as e:
        print(f"  ❌ 请求异常: {type(e).__name__}")
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return None
```

**设计要点**：
- `no_retry_status_codes` 中的状态码（400/401/403）直接返回 None，不触发 urllib3 重试
- 429 由 `urllib3.Retry` 自动重试，额外等待在 `_retry_log` 回调中处理（不在 post 主流程中）
- 异常捕获分四层：ConnectionError → HTTPError → JSONDecodeError → Exception
- 每层异常都有 `print`（终端摘要）+ `logger`（完整堆栈）

### 4.7 `call_openai` OpenAI 兼容调用

```python
def call_openai(self, prompt, provider, max_retries=None) -> Optional[str]:
    """OpenAI 兼容调用（评测模型）

    流程：
    1. _rate_limit() 限流
    2. OpenAI SDK 调用（外层手动重试 + 日志）
    3. 异常捕获 + print + logger

    Args:
        prompt: 评测提示词
        provider: 包含 api_key/base_url/model 的字典
        max_retries: 最大重试次数（默认使用配置值）

    Returns:
        成功时返回响应文本，失败时返回 None
    """
    if OpenAI is None:
        print("  ⚠️ openai 包未安装，无法调用评测API")
        return None

    self._rate_limit()

    actual_retries = max_retries if max_retries is not None else self._max_attempts
    client = OpenAI(api_key=provider["api_key"], base_url=provider["base_url"])

    for attempt in range(actual_retries):
        try:
            response = client.chat.completions.create(
                model=provider["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            num = attempt + 1
            print(f"  ⚠️ [{provider['name']}] 第{num}次调用失败: {type(e).__name__}")
            self.logger.warning(f"[{provider['name']}] 第{num}次调用失败: {e}")
            if attempt < actual_retries - 1:
                wait = min(self._backoff_factor * (2 ** attempt), self._max_delay)
                print(f"  ⏳ 等待 {wait:.1f}s 后重试...")
                time.sleep(wait)

    print(f"  ❌ [{provider['name']}] 调用最终失败，已触发最大重试次数")
    self.logger.error(f"[{provider['name']}] 调用最终失败")
    return None
```

**设计要点**：
- OpenAI SDK 不走 `requests.Session`，因此无法使用 `urllib3.Retry`
- 手动实现指数退避重试：`wait = min(backoff_factor * (2 ** attempt), max_delay)`
- 共享 `_rate_limit()` 和日志逻辑，保证与 `post()` 一致
- 重试日志同样使用 `print` + `logger` 双轨制

---

## 5. TestRunner 改造设计

### 5.1 `__init__` 新增 APIClient

```python
# 在 TestRunner.__init__ 中新增
from tools.api_client import APIClient
self._api_client = APIClient(config_registry=self._registry)
```

### 5.2 `_call_model_under_test` 简化

**现有代码**（253-273行）：手动 for 循环 + `sleep(2)` + 手动异常处理

**改为**：

```python
def _call_model_under_test(self, prompt_or_messages, max_retries=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
    }

    under_test_inference = self._registry.under_test_inference if self._registry else {"temperature": 0.7, "top_p": 0.9}
    api_timeout = self._registry.execution_config.get("parameters", {}).get("timing", {}).get("api_timeout", 60) if self._registry else 60

    if isinstance(prompt_or_messages, list):
        data = {
            "model": self.model,
            "messages": prompt_or_messages,
            "temperature": under_test_inference.get("temperature", 0.7),
            "top_p": under_test_inference.get("top_p", 0.9)
        }
    else:
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt_or_messages}],
            "temperature": under_test_inference.get("temperature", 0.7),
            "top_p": under_test_inference.get("top_p", 0.9)
        }

    result = self._api_client.post(self.api_url, headers, data, timeout=api_timeout)

    if result is None:
        return "❌ 被测模型API调用失败"
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"]
    elif "error" in result:
        return f"❌ 被测模型API错误: {result['error']}"
    else:
        return f"❌ 被测模型API返回异常: {result}"
```

**变化**：
- 移除手动 for 循环重试 → 由 `APIClient.post()` 内部 `urllib3.Retry` 处理
- 移除硬编码 `time.sleep(2)` → 由 `APIClient._rate_limit()` 处理
- 移除手动异常捕获 → 由 `APIClient.post()` 统一处理

### 5.3 `_call_openai_compatible` 简化

**现有代码**（275-301行）：手动 for 循环 + `sleep(2)`

**改为**：

```python
def _call_openai_compatible(self, prompt, provider, max_retries=None):
    return self._api_client.call_openai(prompt, provider, max_retries=max_retries)
```

**变化**：
- 整个方法体缩减为一行委托调用
- 重试/限流/日志/异常全部由 `APIClient.call_openai()` 处理

### 5.4 用例间延迟保留

`run_single_test` 和 `run_multi_turn_test` 中的 `time.sleep(delay_between_cases)` 保留不变：

```python
# 保留（654行、767行）
exec_cfg = self._registry.execution_config if self._registry else {}
concurrency_cfg = exec_cfg.get('concurrency', {})
mode_cfg = concurrency_cfg.get('modes', {}).get('single_thread', {})
time.sleep(mode_cfg.get('delay_between_cases', 2.0))
```

**原因**：`delay_between_cases` 是用例间的业务节奏控制，与 API 调用间的限流是不同概念：
- `delay_between_cases`：一个用例执行完后等待，属于测试节奏控制 → 保留在 TestRunner
- `delay_between_calls`：每次 API 请求前等待，属于限流保护 → 移入 APIClient

---

## 6. 全链路日志设计

### 6.1 双轨制原则

| 类型 | 输出方式 | 示例 | 理由 |
|------|----------|------|------|
| 执行进度/状态 | `print` | `📝 正在执行第 1/10 条用例` | 实时可见、emoji 直观 |
| 成功/失败结果 | `print` | `✅ 评测API调用成功: DashScope` | 用户一眼看到结论 |
| 重试过程 | `print` + `logger` | `⚠️ 第2次重试 \| 状态码: 429 \| 等待: 4s` | 终端看进度，日志留痕 |
| 异常详情 | `logger` | `[APIClient] ConnectionError: ...` | 终端不刷屏，日志可查 |
| 请求耗时/调试 | `logger.debug` | `POST {url} \| 耗时: 1200ms` | 只在 DEBUG 级别可见 |

### 6.2 日志级别映射

| 阶段 | print | logger 级别 | 内容 |
|------|-------|-------------|------|
| 请求前限流 | `⏳ 限流等待: {delay}s` | DEBUG | 限流等待时间 |
| 重试中 | `⚠️ 第{N}次重试 \| 状态码: {code} \| 等待: {wait}s` | WARNING | 重试次数和原因 |
| 429 限流 | `⚠️ 触发限流(429) \| 额外等待 {delay}s` | WARNING | 限流响应处理 |
| 401 鉴权失败 | `❌ 401 鉴权失败：API Key错误/过期/无权限` | ERROR | 鉴权问题 |
| 400 参数错误 | `❌ 400 参数错误：请求格式/字段非法` | ERROR | 请求格式问题 |
| 403 禁止访问 | `❌ 403 禁止访问` | ERROR | 权限问题 |
| 请求最终失败 | `❌ 请求最终失败！网络/HTTP异常，已触发最大重试次数` | ERROR | 重试耗尽 |
| JSON 解析失败 | `❌ 响应JSON解析失败` | ERROR | 响应格式问题 |
| 未知异常 | `❌ 请求异常: {ExceptionType}` | ERROR | 兜底异常 |

### 6.3 与 TestRunRecorder 的关系

- `APIClient` 的日志 → `logging` 系统（控制台 + 可选日志文件）
- `TestRunRecorder` 的日志 → 批次目录的 `test_execution.log`（用例级别）
- 两者互补，不冲突：
  - `APIClient` 记录 API 调用级别的技术细节（重试、限流、异常）
  - `TestRunRecorder` 记录用例级别的业务进度（开始、完成、通过/失败）

---

## 7. 数据流

### 7.1 被测模型调用流程

```
TestRunner._call_model_under_test()
  └→ APIClient.post(url, headers, data)
       ├→ _rate_limit()           # time.sleep 限流
       ├→ session.post()          # urllib3.Retry 自动重试
       │    ├→ 成功 → return json
       │    ├→ 429 → sleep(delay_on_429) → 自动重试
       │    ├→ 400/401/403 → return None（不重试）
       │    └→ 5xx → 自动重试（指数退避）
       └→ 异常捕获 → print + logger → return None
```

### 7.2 评测模型调用流程

```
TestRunner._call_openai_compatible()
  └→ APIClient.call_openai(prompt, provider)
       ├→ _rate_limit()           # time.sleep 限流
       ├→ OpenAI SDK 调用
       │    ├→ 成功 → return text
       │    └→ 异常 → 手动重试（指数退避）
       └→ 重试耗尽 → print + logger → return None
```

---

## 8. 配置参数流转

```
execution.yaml
  └→ ConfigLoader.load_execution_config()
       └→ ConfigRegistry.execution_config
            ├→ ConfigRegistry.retry_config       # 新增属性
            ├→ ConfigRegistry.rate_limit_config   # 新增属性
            └→ APIClient.__init__(config_registry)
                 ├→ self._max_attempts
                 ├→ self._backoff_factor
                 ├→ self._max_delay
                 ├→ self._status_forcelist
                 ├→ self._no_retry_status_codes
                 ├→ self._delay_between_calls
                 └→ self._delay_on_429
```

---

## 9. 非目标（不在本次范围内）

1. 异步 API 调用（async/aiohttp）— 当前项目使用同步模型，暂不需要
2. 令牌桶/漏桶限流 — 当前项目请求量级不需要，固定间隔足够
3. Prometheus/监控指标 — 当前项目无此需求
4. API 调用去重/缓存 — 与测试场景不符
5. 修改 `TestRunRecorder` 的日志格式 — 保持现有用例级日志不变
6. 修改 `generate_test_cases.py` — 用例生成脚本的 API 调用暂不在本次改造范围
