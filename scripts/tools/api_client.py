"""
API 统一调用客户端 V1.0

职责：
1. 指数退避重试（手动实现，兼容 urllib3 2.x）
2. 重试日志记录（print + logger 双轨）
3. 请求前限流（time.sleep）
4. HTTP 状态码分级处理
5. 统一异常捕获与日志

日期: 2026-04-27
版本: 1.0
"""

import time
from json import JSONDecodeError
from typing import Optional

import requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from tools.utils import get_logger

logger = get_logger(__name__)


class APIClient:
    """统一 API 调用客户端

    所有 API 调用（被测模型 + 评测模型）统一走此客户端，
    保证重试/限流/日志/异常处理规则一致。
    """

    def __init__(self, config_registry=None):
        self._registry = config_registry

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
        self._status_forcelist = set(retry_cfg.get("status_forcelist", [429, 500, 502, 503, 504]))
        self._no_retry_status_codes = set(retry_cfg.get("no_retry_status_codes", [400, 401, 403]))

        self._delay_between_calls = rate_limit_cfg.get("delay_between_calls", 1.0)
        self._delay_on_429 = rate_limit_cfg.get("delay_on_429", 10)

        self._api_timeout = timeout_cfg.get("api_timeout", 60)

        self._session = requests.Session()

        self._last_call_time = 0.0

    def _calculate_backoff(self, attempt):
        return min(self._backoff_factor * (2 ** attempt), self._max_delay)

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self._last_call_time
        delay = self._delay_between_calls - elapsed

        if delay > 0:
            print(f"  ⏳ 限流等待: {delay:.1f}s")
            logger.debug(f"限流等待: {delay:.1f}s")
            time.sleep(delay)

        self._last_call_time = time.time()

    def post(self, url, headers, json_body, timeout=None) -> Optional[dict]:
        """统一 POST 请求（被测模型调用走这里）

        流程：
        1. _rate_limit() 限流
        2. 手动重试循环（指数退避 + 状态码分级）
        3. no_retry_status_codes（400/401/403）不重试，直接返回
        4. status_forcelist（429/5xx）触发重试，429 额外等待
        5. 异常捕获：ConnectionError/Timeout/JSONDecodeError/Exception

        Returns:
            成功时返回响应 JSON 字典，失败时返回 None
        """
        self._rate_limit()

        actual_timeout = timeout or self._api_timeout

        for attempt in range(self._max_attempts):
            try:
                res = self._session.post(url=url, headers=headers, json=json_body, timeout=actual_timeout)
                status_code = res.status_code

                if status_code in self._no_retry_status_codes:
                    if status_code == 401:
                        print("  ❌ 401 鉴权失败：API Key错误/过期/无权限")
                        logger.error("401 鉴权失败：API Key错误/过期/无权限")
                    elif status_code == 400:
                        print("  ❌ 400 参数错误：请求格式/字段非法")
                        logger.error("400 参数错误：请求格式/字段非法")
                    elif status_code == 403:
                        print("  ❌ 403 禁止访问")
                        logger.error("403 禁止访问")
                    return None

                if status_code in self._status_forcelist:
                    if attempt < self._max_attempts - 1:
                        if status_code == 429:
                            print(f"  ⚠️ 触发限流(429) | 额外等待 {self._delay_on_429}s")
                            logger.warning(f"触发429限流 | 额外等待 {self._delay_on_429}s")
                            time.sleep(self._delay_on_429)

                        wait = self._calculate_backoff(attempt)
                        num = attempt + 1
                        print(f"  ⚠️ 第{num}次重试 | 状态码: {status_code} | 等待: {wait:.1f}s")
                        logger.warning(f"第{num}次重试 | 状态码: {status_code} | 等待: {wait:.1f}s")
                        time.sleep(wait)
                        continue
                    else:
                        print(f"  ❌ 请求最终失败！状态码: {status_code}，已触发最大重试次数")
                        logger.error(f"请求最终失败 | 状态码: {status_code} | 已触发最大重试次数")
                        return None

                res.raise_for_status()
                return res.json()

            except requests.exceptions.ConnectionError as e:
                if attempt < self._max_attempts - 1:
                    wait = self._calculate_backoff(attempt)
                    num = attempt + 1
                    print(f"  ⚠️ 第{num}次重试 | 网络异常 | 等待: {wait:.1f}s")
                    logger.warning(f"第{num}次重试 | ConnectionError | 等待: {wait:.1f}s")
                    time.sleep(wait)
                    continue
                print(f"  ❌ 请求最终失败！网络异常，已触发最大重试次数")
                logger.error(f"ConnectionError: {e}", exc_info=True)
                return None
            except requests.exceptions.Timeout as e:
                if attempt < self._max_attempts - 1:
                    wait = self._calculate_backoff(attempt)
                    num = attempt + 1
                    print(f"  ⚠️ 第{num}次重试 | 请求超时 | 等待: {wait:.1f}s")
                    logger.warning(f"第{num}次重试 | Timeout | 等待: {wait:.1f}s")
                    time.sleep(wait)
                    continue
                print(f"  ❌ 请求最终失败！请求超时，已触发最大重试次数")
                logger.error(f"Timeout: {e}", exc_info=True)
                return None
            except requests.exceptions.HTTPError as e:
                print(f"  ❌ 请求失败！HTTP异常")
                logger.error(f"HTTPError: {e}", exc_info=True)
                return None
            except JSONDecodeError as e:
                print(f"  ❌ 响应JSON解析失败")
                logger.error(f"JSONDecodeError: {e}", exc_info=True)
                return None
            except Exception as e:
                print(f"  ❌ 请求异常: {type(e).__name__}")
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None

        return None

    def call_openai(self, prompt, provider, max_retries=None, evaluator_inference=None) -> Optional[str]:
        """OpenAI 兼容调用（评测模型调用走这里）

        流程：
        1. _rate_limit() 限流
        2. OpenAI SDK 调用（外层手动重试 + 日志）
        3. 异常捕获 + print + logger

        Args:
            prompt: 评测提示词
            provider: 包含 api_key/base_url/model 的字典
            max_retries: 最大重试次数（默认使用配置值）
            evaluator_inference: 评测模型推理参数

        Returns:
            成功时返回响应文本，失败时返回 None
        """
        if OpenAI is None:
            print("  ⚠️ openai 包未安装，无法调用评测API")
            return None

        self._rate_limit()

        actual_retries = max_retries if max_retries is not None else self._max_attempts
        client = OpenAI(api_key=provider["api_key"], base_url=provider["base_url"])

        if evaluator_inference is None:
            evaluator_inference = {"temperature": 0.3, "top_p": 0.9}

        for attempt in range(actual_retries):
            try:
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=evaluator_inference.get("temperature", 0.3),
                    max_tokens=2000,
                    stream=False,
                )
                return response.choices[0].message.content
            except Exception as e:
                num = attempt + 1
                print(f"  ⚠️ [{provider['name']}] 第{num}次调用失败: {type(e).__name__}")
                logger.warning(f"[{provider['name']}] 第{num}次调用失败: {e}")
                if attempt < actual_retries - 1:
                    wait = min(self._backoff_factor * (2 ** attempt), self._max_delay)
                    print(f"  ⏳ 等待 {wait:.1f}s 后重试...")
                    time.sleep(wait)

        print(f"  ❌ [{provider['name']}] 调用最终失败，已触发最大重试次数")
        logger.error(f"[{provider['name']}] 调用最终失败")
        return None

    def call_model_under_test(self, prompt_or_messages, api_key, api_url, model,
                              inference_config=None, timeout=None):
        """被测模型调用 — 从 TestRunner._call_model_under_test 迁移

        Args:
            prompt_or_messages: 纯文本字符串或 OpenAI messages 列表
            api_key: 被测模型 API Key
            api_url: 被测模型 API URL
            model: 被测模型名称
            inference_config: 推理参数 {temperature, top_p}
            timeout: 请求超时时间

        Returns:
            模型回复文本，失败时返回错误提示字符串
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        if inference_config is None:
            inference_config = {"temperature": 0.7, "top_p": 0.9}

        if isinstance(prompt_or_messages, list):
            data = {
                "model": model,
                "messages": prompt_or_messages,
                "temperature": inference_config.get("temperature", 0.7),
                "top_p": inference_config.get("top_p", 0.9)
            }
        else:
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt_or_messages}],
                "temperature": inference_config.get("temperature", 0.7),
                "top_p": inference_config.get("top_p", 0.9)
            }

        result = self.post(api_url, headers, data, timeout=timeout)

        if result is None:
            return "❌ 被测模型API调用失败"
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"❌ 被测模型API错误: {result['error']}"
        else:
            return f"❌ 被测模型API返回异常: {result}"

    def call_evaluator_with_fallback(self, prompt, providers, evaluator_inference=None):
        """评测 Provider 轮询 + 自动切换 — 从 TestRunner.call_evaluator_api 迁移

        注意坑20：返回三元组 (response_text, provider_name, used_model_name)，
        不修改任何外部状态。

        Args:
            prompt: 评测提示词
            providers: Provider 列表，每项包含 api_key/base_url/model/name
            evaluator_inference: 评测模型推理参数

        Returns:
            (响应文本, Provider名称, 模型名称)，全部失败时返回 (None, "unavailable", "")
        """
        for provider in providers:
            if not provider.get("api_key"):
                print(f"  ⏭️ [{provider['name']}] 跳过：无 API Key")
                continue

            print(f"  🔄 尝试评测API: {provider['name']} ({provider['model']})")
            response = self.call_openai(prompt, provider, max_retries=2,
                                        evaluator_inference=evaluator_inference)

            if response and not response.startswith("❌"):
                print(f"  ✅ 评测API调用成功: {provider['name']}")
                return response, provider["name"], provider["model"]
            else:
                print(f"  ⚠️ [{provider['name']}] 调用失败，尝试下一个 Provider...")

        print(f"  🔴 所有评测API均不可用，跳过此用例（评测独立性无法保证，不使用千帆兜底自评）")
        print(f"  💡 提示：请检查 DashScope/ModelScope 的 API Key 配置")
        return None, "unavailable", ""
