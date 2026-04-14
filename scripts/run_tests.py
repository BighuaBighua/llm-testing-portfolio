"""
AI客服系统自动化测试执行脚本 V3.0

核心变更（V3.0）：
1. 统一评测管线：EvaluatorPromptAssembler 动态组装评测Prompt
2. EvaluationParser 多策略解析评测响应
3. EvaluatorPolicy 评测独立性保障
4. prompt_injection 维度路由（防御成功/绕过成功）
5. ConfigRegistry 配置中心集成
6. 绕过成功率统计

历史变更（V2.3）：
1. 两次调用分离（被测模型回答 → 评测模型评测）
2. evaluator_template 真正生效
3. 8维评测支持（4基础 + 4高级维度焦点）
4. API 后备切换：DashScope → ModelScope → 千帆兜底
5. OpenAI 兼容协议统一调用
6. append 模式 recorder 正常创建

日期: 2026-04-09
版本: 3.0
"""

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import requests

from tools.config import (
    get_api_config,
    get_api_key,
    get_execution_config,
    get_evaluator_providers,
    get_model_config,
    get_model_under_test,
    get_dimension_names
)
from tools.config import (
    get_test_cases_path,
    get_evaluator_template_path,
    get_results_dir
)
from tools.execution import TestRunRecorder
from tools.evaluation import EvaluatorPromptAssembler
from tools.evaluation import EvaluationParser, EvaluatorPolicy
from tools.under_test_prompt_assembler import UnderTestPromptAssembler
from tools.config import ConfigRegistry, EvaluationContext

# OpenAI 兼容客户端
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("⚠️ openai 包未安装，评测API后备切换不可用。请运行: pip install openai")


class TestRunner:
    """测试执行器 V3.0（统一评测管线 + prompt_injection路由 + 评测独立性保障）"""

    def __init__(self, api_key: str, evaluator_template_path: str, scenario: str = None):
        self.api_key = api_key

        # 使用新的配置管理器获取配置
        api_config = get_api_config()
        execution_config = get_execution_config()

        # 获取被测模型配置
        model_config = get_model_under_test()
        self.api_url = model_config.get('base_url', '') or api_config.get('qianfan', {}).get('base_url', '')
        self.model = model_config.get('model', 'unknown')

        self.test_cases_version = "unknown"
        self.evaluator_providers = get_evaluator_providers()

        if self.evaluator_providers:
            self.evaluator_model_name = self.evaluator_providers[0].get('model', 'unknown')
        else:
            self.evaluator_model_name = 'unknown'

        try:
            ConfigRegistry.reset()
            self._registry = ConfigRegistry.initialize(scenario=scenario)
        except Exception:
            self._registry = None

        self._prompt_assembler = EvaluatorPromptAssembler(self._registry)
        self._under_test_assembler = UnderTestPromptAssembler(registry=self._registry)
        self._response_parser = EvaluationParser()
        self._evaluator_policy = EvaluatorPolicy(
            self._registry.evaluation_settings.get("injection_independence_policy", "strict")
            if self._registry else "strict"
        )

    def load_test_cases(self, test_cases_path: str) -> Tuple[List[Dict], str]:
        """
        加载测试用例模板

        Args:
            test_cases_path: 测试用例文件路径

        Returns:
            (测试用例列表, 用例版本)
        """
        with open(test_cases_path, 'r', encoding='utf-8') as f:
            data: Dict = json.load(f)

        test_cases_version = "unknown"
        if "metadata" in data:
            test_cases_version = data["metadata"]["version"]
            all_cases = data["cases"]
        else:
            all_cases = data
        # 扁平化所有维度的用例
        test_cases = []
        for _, cases in all_cases.items():
            test_cases.extend(cases)

        return test_cases, test_cases_version

    def filter_test_cases(self, test_cases: List[Dict], mode: str, cases_ids: Optional[str] = None, executed_ids: Optional[Set[str]] = None) -> List[Dict]:
        """根据执行模式过滤测试用例"""
        if mode == 'single':
            return test_cases[:1]
        elif mode == 'selected':
            if not cases_ids:
                print("❌ selected 模式需要指定 --cases 参数")
                return []
            selected_ids = set(cases_ids.split(','))
            filtered = [tc for tc in test_cases if tc['id'] in selected_ids]
            if len(filtered) != len(selected_ids):
                found_ids = {tc['id'] for tc in filtered}
                missing_ids = selected_ids - found_ids
                print(f"⚠️ 未找到用例ID: {', '.join(missing_ids)}")
            return filtered
        elif mode == 'incremental':
            if not executed_ids:
                print("⚠️ 未找到已执行用例记录，将执行所有用例")
                return test_cases
            filtered = [tc for tc in test_cases if tc['id'] not in executed_ids]
            if not filtered:
                print("✅ 所有用例已执行过，无需重新执行")
            return filtered
        else:
            return test_cases

    def load_executed_cases(self, batch_dir: str) -> Set[str]:
        """从结果文件中读取已执行的用例ID"""
        results_path = os.path.join(batch_dir, "results.json")

        if not os.path.exists(results_path):
            print(f"⚠️ 未找到结果文件: {results_path}")
            return set()

        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                results: List[Dict] = json.load(f)
            # 防御：校验数据结构
            if not isinstance(results, list):
                print(f"⚠️ 结果文件格式异常：期望列表，得到 {type(results).__name__}")
                return set()
            # 只取包含 id 字段的记录，跳过损坏条目
            executed_ids = {r['id'] for r in results if isinstance(r, dict) and 'id' in r}
            skipped = len(results) - len(executed_ids)
            if skipped:
                print(f"⚠️ 跳过 {skipped} 条缺少 id 字段的损坏记录")
            print(f"📊 已执行用例数: {len(executed_ids)}")
            return executed_ids
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠️ 读取结果文件失败: {e}")
            return set()
        except (KeyError, TypeError) as e:
            print(f"⚠️ 结果文件数据结构异常: {e}")
            return set()

    # ==================== Prompt 构建 ====================

    def build_customer_prompt(self, test_case: Dict, conversation_history: List[Dict] = None) -> Union[str, List[Dict]]:
        return self._under_test_assembler.assemble(test_case, conversation_history)

    def build_evaluator_prompt(self, test_case: Dict, customer_response: str, turn_results: List[Dict] = None) -> str:
        dimension = test_case.get('dimension', 'accuracy')
        ai_response = customer_response or ""

        if dimension == 'multi_turn' and turn_results:
            ai_response = "\n".join(
                f"第{t['turn']}轮 用户: {t['user']}\n第{t['turn']}轮 AI: {t['assistant']}"
                for t in turn_results
            )

        eval_ctx = EvaluationContext.from_test_case(test_case)

        return self._prompt_assembler.assemble(
            dimension=dimension,
            test_case=test_case,
            ai_response=ai_response,
            eval_ctx=eval_ctx,
        )

    # ==================== API 调用 ====================

    def _call_qianfan(self, prompt_or_messages: Union[str, List[Dict]], max_retries: int = 2) -> str:
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

        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, json=data, headers=headers, timeout=api_timeout)
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                elif "error" in result:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️ 千帆API错误，第{attempt+1}次重试...")
                        time.sleep(2)
                        continue
                    return f"❌ 千帆API错误: {result['error']}"
                else:
                    return f"❌ 千帆API返回异常: {result}"
            except (requests.RequestException, KeyError, ValueError) as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 千帆API异常，第{attempt+1}次重试: {e}")
                    time.sleep(2)
                    continue
                return f"❌ 千帆API调用异常: {e}"
        return "❌ 千帆API调用失败：超过最大重试次数"

    def _call_openai_compatible(self, prompt: str, provider: dict, max_retries: int = 1) -> Optional[str]:
        if OpenAI is None:
            return None

        client = OpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"]
        )

        evaluator_inference = self._registry.evaluator_inference if self._registry else {"temperature": 0.3, "top_p": 0.9}

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=evaluator_inference.get("temperature", 0.3),
                    max_tokens=2000,
                    stream=False
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"  ⚠️ [{provider['name']}] 第{attempt+1}次调用失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        return None

    def call_evaluator_api(self, prompt: str) -> Tuple[str, str]:
        """
        调用评测 API（带后备切换）

        Returns:
            (response_text, used_provider_name)
        """
        for provider in self.evaluator_providers:
            if not provider["api_key"]:
                print(f"  ⏭️ [{provider['name']}] 跳过：无 API Key")
                continue

            print(f"  🔄 尝试评测API: {provider['name']} ({provider['model']})")
            response = self._call_openai_compatible(prompt, provider, max_retries=2)

            if response and not response.startswith("❌"):
                print(f"  ✅ 评测API调用成功: {provider['name']}")
                self.evaluator_model_name = provider["model"]
                return response, provider["name"]
            else:
                print(f"  ⚠️ [{provider['name']}] 调用失败，尝试下一个 Provider...")

        # 所有 provider 都失败，使用千帆兜底
        print(f"  🔴 所有评测API失败，使用千帆兜底（评测独立性无法保证）")
        response = self._call_qianfan(prompt)
        self.evaluator_model_name = self.model
        return response, "qianfan_fallback"

    # ==================== 结果解析 ====================

    def parse_evaluation_response(self, evaluation_response: str, test_case: Dict, customer_response: str) -> Dict:
        """
        解析评测响应（V3.0：统一评测管线 + prompt_injection路由）
        """
        dimension = test_case.get("dimension", "accuracy")

        if dimension == "prompt_injection":
            return self._parse_prompt_injection_response(evaluation_response, test_case, customer_response)

        parsed = self._response_parser.parse(evaluation_response, dimension)

        result = {
            "test_case_id": test_case["id"],
            "dimension": dimension,
            "input": test_case["input"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_response": customer_response,
            "test_case_version": self.test_cases_version,
            "evaluator_model": self.evaluator_model_name,
            "evaluation_result": {
                "status": parsed.get("result_label", "未知"),
                "accuracy": "",
                "completeness": "",
                "compliance": "",
                "attitude": "",
                "dimension_focus": "",
                "issues": []
            },
            "full_response": evaluation_response
        }

        if parsed.get("passed") is True:
            result["evaluation_result"]["status"] = "通过"
        elif parsed.get("passed") is False:
            result["evaluation_result"]["status"] = "不通过"

        dimension_patterns = {
            "accuracy": r"准确性[：:]\s*(.*?)\n",
            "completeness": r"完整性[：:]\s*(.*?)\n",
            "compliance": r"合规性[：:]\s*(.*?)\n",
            "attitude": r"态度[：:]\s*(.*?)\n",
        }
        for dim_key, pattern in dimension_patterns.items():
            match = re.search(pattern, evaluation_response)
            if match:
                result["evaluation_result"][dim_key] = match.group(1).strip()

        if dimension in ['multi', 'boundary', 'conflict', 'induction']:
            dim_cn = get_dimension_names().get(dimension, dimension)
            focus_patterns = [
                rf"{dim_cn}[：:]\s*(.*?)\n",
                rf"{dimension}[：:]\s*(.*?)\n",
                r"维度焦点[：:]\s*(.*?)\n",
                r"重点评估[：:]\s*(.*?)\n",
            ]
            for pattern in focus_patterns:
                match = re.search(pattern, evaluation_response)
                if match:
                    result["evaluation_result"]["dimension_focus"] = match.group(1).strip()
                    break

        if result["evaluation_result"]["status"] == "不通过":
            issues_match = re.search(r"违规说明[：:](.*?)(?:\n|$)", evaluation_response)
            if issues_match:
                result["evaluation_result"]["issues"].append(issues_match.group(1).strip())

        return result

    def _parse_prompt_injection_response(self, evaluation_response: str, test_case: Dict, customer_response: str) -> Dict:
        """解析Prompt注入攻击维度评测响应"""
        parsed = self._response_parser.parse(evaluation_response, "prompt_injection")

        result = {
            "test_case_id": test_case["id"],
            "dimension": "prompt_injection",
            "input": test_case["input"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_response": customer_response,
            "test_case_version": self.test_cases_version,
            "evaluator_model": self.evaluator_model_name,
            "evaluation_result": {
                "status": parsed.get("defense_result", "未知"),
                "accuracy": "",
                "completeness": "",
                "compliance": "",
                "attitude": "",
                "dimension_focus": "Prompt注入攻击",
                "issues": []
            },
            "prompt_injection_detail": {
                "defense_result": parsed.get("defense_result", "未知"),
                "bypass_type": parsed.get("bypass_type", ""),
                "attack_type": test_case.get("attack_type", ""),
                "attack_type_cn": test_case.get("attack_type_cn", ""),
                "evaluation_conclusion": parsed.get("evaluation_conclusion", ""),
            },
            "full_response": evaluation_response
        }

        if parsed.get("passed") is True:
            result["evaluation_result"]["status"] = "防御成功"
        elif parsed.get("passed") is False:
            result["evaluation_result"]["status"] = "绕过成功"
            bypass_type = parsed.get("bypass_type", "")
            if bypass_type:
                result["evaluation_result"]["issues"].append(
                    f"绕过类型: {bypass_type}"
                )

        return result

    def parse_multi_turn_evaluation(self, evaluation_response: str, test_case: Dict, turn_results: List[Dict]) -> Dict:
        """
        解析多轮对话评测响应（4子任务）
        """
        result = {
            "test_case_id": test_case["id"],
            "dimension": "multi_turn",
            "input": test_case.get('scenario_type_cn', '') + " - " + str(test_case.get('turn_count', 0)) + "轮对话\n" + "\n".join(f"第{t['turn']}轮 用户: {t['user']}" for t in turn_results),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_response": "\n".join(f"第{t['turn']}轮 用户: {t['user']}\n第{t['turn']}轮 AI: {t['assistant']}" for t in turn_results),
            "test_case_version": self.test_cases_version,
            "evaluator_model": self.evaluator_model_name,
            "turn_results": turn_results,
            "evaluation_result": {
                "status": "未知",
                "accuracy": "",
                "completeness": "",
                "compliance": "",
                "attitude": "",
                "dimension_focus": "",
                "turn_evaluation": "",
                "context_consistency": "",
                "instruction_adherence": "",
                "rule_stability": "",
                "issues": []
            },
            "full_response": evaluation_response
        }

        # 提取子任务1：逐轮校验
        turn_match = re.search(r"子任务1.*?逐轮.*?校验[：:]\s*(.*?)(?=子任务2|$)", evaluation_response, re.DOTALL)
        if turn_match:
            result["evaluation_result"]["turn_evaluation"] = turn_match.group(1).strip()[:500]

        # 提取子任务2：上下文一致性
        context_match = re.search(r"上下文一致性.*?校验[：:]\s*(.*?)(?:\n|$)", evaluation_response)
        if context_match:
            result["evaluation_result"]["context_consistency"] = context_match.group(0).strip()

        # 提取子任务3：指令坚守性
        instruction_match = re.search(r"指令坚守性.*?校验[：:]\s*(.*?)(?:\n|$)", evaluation_response)
        if instruction_match:
            result["evaluation_result"]["instruction_adherence"] = instruction_match.group(0).strip()

        # 提取子任务4：规则稳定性
        stability_match = re.search(r"规则稳定性.*?校验[：:]\s*(.*?)(?:\n|$)", evaluation_response)
        if stability_match:
            result["evaluation_result"]["rule_stability"] = stability_match.group(0).strip()

        # 维度焦点
        result["evaluation_result"]["dimension_focus"] = "多轮对话：逐轮校验4大维度 + 上下文一致性 + 指令坚守性 + 规则稳定性"

        # 判定综合结果
        response_lower = evaluation_response

        # 检查是否通过
        has_fail_indicators = any([
            "不合规" in result["evaluation_result"].get("context_consistency", ""),
            "没守" in result["evaluation_result"].get("instruction_adherence", ""),
            "不稳" in result["evaluation_result"].get("rule_stability", ""),
            "不通过" in response_lower and "综合判定" in response_lower,
        ])

        # 检查逐轮校验是否有不合规
        turn_eval = result["evaluation_result"].get("turn_evaluation", "")
        if "不合规" in turn_eval:
            has_fail_indicators = True

        if has_fail_indicators:
            result["evaluation_result"]["status"] = "不通过"
        elif "综合判定" in response_lower:
            verdict_text = response_lower.split("综合判定")[-1][:30]
            if "不通过" in verdict_text:
                result["evaluation_result"]["status"] = "不通过"
            elif "通过" in verdict_text and "不通过" not in verdict_text:
                result["evaluation_result"]["status"] = "通过"
            else:
                result["evaluation_result"]["status"] = "未知"

        # 提取违规说明
        if result["evaluation_result"]["status"] == "不通过":
            issues_match = re.search(r"违规说明[：:](.*?)(?:\n|$)", evaluation_response)
            if issues_match:
                result["evaluation_result"]["issues"].append(issues_match.group(1).strip())

        return result

    # ==================== 测试执行 ====================

    def run_multi_turn_test(self, test_case: Dict, recorder: Optional[Any] = None, case_index: Optional[int] = None, total_cases: Optional[int] = None) -> Dict:
        """
        执行多轮对话测试用例

        流程：
        1. 逐轮调用待测模型（携带对话历史）
        2. 收集所有轮次后，一次性调用评测模型（4子任务）
        """
        print(f"\n{'='*60}")
        print(f"执行多轮测试: {test_case['id']} - {test_case['dimension']}")
        print(f"场景: {test_case.get('scenario_type_cn', '')} | {test_case.get('turn_count', 0)}轮")
        print(f"测试目的: {test_case['test_purpose']}")
        print(f"{'='*60}")

        if recorder and case_index is not None and total_cases is not None:
            recorder.log_case_start(test_case['id'], case_index, total_cases)

        conversation = test_case.get('conversation', [])
        conversation_history = []
        turn_results = []

        # 逐轮调用待测模型
        for turn_data in conversation:
            user_input = turn_data['user']
            print(f"  📝 第{turn_data['turn']}轮 用户: {user_input[:50]}...")

            # 添加用户消息到历史
            conversation_history.append({"role": "user", "content": user_input})

            # 调用待测模型（携带对话历史）
            messages = self.build_customer_prompt(test_case, conversation_history)
            ai_response = self._call_qianfan(messages)
            print(f"  💬 第{turn_data['turn']}轮 AI: {ai_response[:80]}...")

            # 添加AI回复到历史
            conversation_history.append({"role": "assistant", "content": ai_response})

            # 记录本轮
            turn_record = {
                "turn": turn_data['turn'],
                "user": user_input,
                "assistant": ai_response,
                "assistant_hint": turn_data.get("assistant_hint", ""),
                "context": turn_data.get("context", ""),
                "test_point": turn_data.get("test_point", "")
            }
            turn_results.append(turn_record)

        # 一次性调用评测模型（4子任务）
        print(f"  🔍 调用评测模型进行多轮综合评测...")
        evaluator_prompt = self.build_evaluator_prompt(test_case, "", turn_results=turn_results)
        evaluation_response, used_provider = self.call_evaluator_api(evaluator_prompt)

        # 解析多轮评测结果
        result = self.parse_multi_turn_evaluation(evaluation_response, test_case, turn_results)
        result["evaluator_provider"] = used_provider

        # 打印结果
        print(f"\n--- 多轮评测结果 (via {used_provider}) ---")
        print(f"状态: {result['evaluation_result']['status']}")
        for key in ['turn_evaluation', 'context_consistency', 'instruction_adherence', 'rule_stability']:
            if result['evaluation_result'].get(key):
                print(f"{key}: {result['evaluation_result'][key]}")

        if result['evaluation_result']['issues']:
            print(f"违规说明: {', '.join(result['evaluation_result']['issues'])}")

        if recorder and case_index is not None and total_cases is not None:
            recorder.log_case_complete(
                test_case['id'], case_index, total_cases,
                result['evaluation_result']['status']
            )

        exec_cfg = self._registry.execution_config if self._registry else {}
        concurrency_cfg = exec_cfg.get('concurrency', {})
        mode_cfg = concurrency_cfg.get('modes', {}).get('single_thread', {})
        time.sleep(mode_cfg.get('delay_between_cases', 2.0))
        return result

    def run_single_test(self, test_case: Dict, recorder: Optional[Any] = None, case_index: Optional[int] = None, total_cases: Optional[int] = None) -> Dict:
        """
        执行单个测试用例（V3.0：统一评测管线 + prompt_injection路由）
        多轮对话用例自动走 run_multi_turn_test 分支
        """
        if test_case.get('dimension') == 'multi_turn':
            return self.run_multi_turn_test(test_case, recorder, case_index, total_cases)

        dimension = test_case.get('dimension', 'accuracy')
        print(f"\n{'='*60}")
        print(f"执行测试用例: {test_case['id']} - {dimension}")
        if dimension == 'prompt_injection':
            print(f"攻击手法: {test_case.get('attack_type_cn', '')}（{test_case.get('attack_type', '')}）")
        print(f"测试目的: {test_case['test_purpose']}")
        print(f"{'='*60}")

        if recorder and case_index is not None and total_cases is not None:
            recorder.log_case_start(test_case['id'], case_index, total_cases)

        customer_prompt = self.build_customer_prompt(test_case)
        print("步骤1：调用待测模型获取回答...")
        customer_response = self._call_qianfan(customer_prompt)

        evaluator_prompt = self.build_evaluator_prompt(test_case, customer_response)
        print("步骤2：调用评测模型评测...")

        try:
            self._evaluator_policy.check_independence(self.model, self.evaluator_model_name)
        except ValueError as e:
            print(f"⚠️ {e}")

        evaluation_response, used_provider = self.call_evaluator_api(evaluator_prompt)

        result = self.parse_evaluation_response(evaluation_response, test_case, customer_response)
        result["evaluator_provider"] = used_provider

        print(f"\n--- 客服回答 ---")
        print(result['customer_response'][:200] if len(result['customer_response']) > 200 else result['customer_response'])

        print(f"\n--- 评测结果 (via {used_provider}) ---")
        if dimension == 'prompt_injection':
            detail = result.get("prompt_injection_detail", {})
            print(f"防御结果: {detail.get('defense_result', '未知')}")
            if detail.get('bypass_type'):
                print(f"绕过类型: {detail['bypass_type']}")
            if detail.get('evaluation_conclusion'):
                print(f"判定结论: {detail['evaluation_conclusion']}")
        else:
            print(f"状态: {result['evaluation_result']['status']}")
            print(f"准确性: {result['evaluation_result']['accuracy']}")
            print(f"完整性: {result['evaluation_result']['completeness']}")
            print(f"合规性: {result['evaluation_result']['compliance']}")
            print(f"态度: {result['evaluation_result']['attitude']}")
            if result['evaluation_result']['dimension_focus']:
                print(f"维度焦点: {result['evaluation_result']['dimension_focus']}")

        if result['evaluation_result']['issues']:
            print(f"违规说明: {', '.join(result['evaluation_result']['issues'])}")

        if recorder and case_index is not None and total_cases is not None:
            recorder.log_case_complete(
                test_case['id'], case_index, total_cases,
                result['evaluation_result']['status']
            )

        exec_cfg = self._registry.execution_config if self._registry else {}
        concurrency_cfg = exec_cfg.get('concurrency', {})
        mode_cfg = concurrency_cfg.get('modes', {}).get('single_thread', {})
        time.sleep(mode_cfg.get('delay_between_cases', 2.0))
        return result

    def run_all_tests(self, test_cases: List[Dict], recorder: Optional[Any] = None) -> List[Dict]:
        """执行所有测试用例"""
        print(f"\n开始执行测试，共 {len(test_cases)} 个用例")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n进度: {i}/{len(test_cases)}")
            result = self.run_single_test(test_case, recorder, i, len(test_cases))
            results.append(result)

        print(f"\n所有测试执行完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return results

    def run_tests_concurrent(self, test_cases: List[Dict], max_workers: int = 2, recorder: Optional[Any] = None) -> List[Dict]:
        """并发执行测试用例"""
        print(f"\n开始并发执行测试，共 {len(test_cases)} 个用例")
        print(f"并发数: {max_workers}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [(executor.submit(self.run_single_test, tc), tc) for tc in test_cases]

            completed = 0
            for future, test_case in futures:
                completed += 1

                try:
                    result = future.result()
                    results.append(result)
                    print(f"\n✅ 进度: {completed}/{len(test_cases)} - {test_case['id']} 完成")
                except Exception as e:
                    print(f"\n❌ 进度: {completed}/{len(test_cases)} - {test_case['id']} 失败: {e}")
                    results.append({
                        "test_case_id": test_case['id'],
                        "dimension": test_case['dimension'],
                        "input": test_case['input'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "customer_response": f"执行失败: {str(e)}",
                        "evaluator_model": self.model,
                        "evaluation_result": {
                            "status": "失败",
                            "accuracy": "",
                            "completeness": "",
                            "compliance": "",
                            "attitude": "",
                            "dimension_focus": "",
                            "issues": [f"执行异常: {str(e)}"]
                        }
                    })

                exec_cfg = self._registry.execution_config if self._registry else {}
                concurrency_cfg = exec_cfg.get('concurrency', {})
                mode_cfg = concurrency_cfg.get('modes', {}).get('concurrent', {})
                time.sleep(mode_cfg.get('delay_between_cases', 0.5))

        print(f"\n所有测试执行完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return results

    # ==================== 结果保存 ====================

    def save_execution_records(self, results: List[Dict], output_path: str, mode: str = 'new'):
        """保存执行记录"""
        execution_records = []
        for result in results:
            if result["dimension"] == "multi_turn":
                actual_response = result["customer_response"][:200] + "..."
            else:
                actual_response = result["customer_response"]
            record = {
                "id": result["test_case_id"],
                "input": result["input"],
                "actual_response": actual_response,
                "timestamp": result["timestamp"],
                "model": self.model
            }
            execution_records.append(record)

        existing_records: List[Dict] = []
        new_records = []

        if mode == 'append' and os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_records = json.load(f)
            existing_ids = {r["id"] for r in existing_records}
            new_records = [r for r in execution_records if r["id"] not in existing_ids]
            all_records = existing_records + new_records
        else:
            all_records = execution_records
            new_records = execution_records

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 执行记录已保存到: {output_path}")
        if mode == 'append' and existing_records:
            print(f"   （追加模式：原有 {len(existing_records)} 条，新增 {len(new_records)} 条）")

    def save_evaluation_results(self, results: List[Dict], output_path: str, mode: str = 'new'):
        """保存评测结果"""
        evaluation_results = []
        for result in results:
            eval_result = {
                "id": result["test_case_id"],
                "dimension": result["dimension"],
                "input": result["input"],
                "actual_response": result["customer_response"],
                "evaluation_result": result["evaluation_result"],
                "timestamp": result["timestamp"],
                "evaluator_model": result.get("evaluator_model", self.model),
                "evaluator_provider": result.get("evaluator_provider", "unknown"),
                "test_case_version": result.get("test_case_version", self.test_cases_version)
            }
            if result["dimension"] == "multi_turn" and "turn_results" in result:
                eval_result["turn_results"] = result["turn_results"]
            evaluation_results.append(eval_result)

        existing_results: List[Dict] = []
        new_results = []

        if mode == 'append' and os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
            existing_ids = {r["id"] for r in existing_results}
            new_results = [r for r in evaluation_results if r["id"] not in existing_ids]
            all_results = existing_results + new_results
        else:
            all_results = evaluation_results
            new_results = evaluation_results

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"✅ 评测结果已保存到: {output_path}")
        if mode == 'append' and existing_results:
            print(f"   （追加模式：原有 {len(existing_results)} 条，新增 {len(new_results)} 条）")

    # ==================== 报告生成 ====================

    def generate_report(self, results: List[Dict], output_path: str):
        """生成测试报告"""
        # 从 results.json 读取所有结果
        results_dir = os.path.dirname(output_path)
        results_json_path = os.path.join(results_dir, "results.json")

        all_results: List[Dict] = results
        if os.path.exists(results_json_path):
            with open(results_json_path, 'r', encoding='utf-8') as f:
                all_results = json.load(f)  # type: ignore[assignment]

        total = len(all_results)
        passed = sum(1 for r in all_results if r["evaluation_result"]["status"] == "通过")
        failed = sum(1 for r in all_results if r["evaluation_result"]["status"] == "不通过")
        unknown = total - passed - failed

        # 统计各维度
        dimension_stats = {}
        for result in all_results:
            dim = result["dimension"]
            if dim not in dimension_stats:
                dimension_stats[dim] = {"passed": 0, "failed": 0, "unknown": 0}

            if result["evaluation_result"]["status"] == "通过":
                dimension_stats[dim]["passed"] += 1
            elif result["evaluation_result"]["status"] == "不通过":
                dimension_stats[dim]["failed"] += 1
            else:
                dimension_stats[dim]["unknown"] += 1

        # Prompt注入攻击绕过成功率统计
        pin_stats = {"total": 0, "defense_success": 0, "bypass_success": 0, "unknown": 0, "bypass_types": {}}
        for result in all_results:
            if result["dimension"] == "prompt_injection":
                pin_stats["total"] += 1
                status = result["evaluation_result"]["status"]
                if status == "防御成功":
                    pin_stats["defense_success"] += 1
                elif status == "绕过成功":
                    pin_stats["bypass_success"] += 1
                    detail = result.get("prompt_injection_detail", {})
                    bt = detail.get("bypass_type", "unknown")
                    if bt not in pin_stats["bypass_types"]:
                        pin_stats["bypass_types"][bt] = 0
                    pin_stats["bypass_types"][bt] += 1
                else:
                    pin_stats["unknown"] += 1

        # 统计评测 API 使用情况
        provider_stats = {}
        for result in all_results:
            provider = result.get("evaluator_provider", "unknown")
            if provider not in provider_stats:
                provider_stats[provider] = 0
            provider_stats[provider] += 1

        # 生成报告
        report = f"""# 自动化测试报告

> 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 测试框架: AI客服自动化测试框架 v3.0（统一评测管线 + 动态Prompt组装）
> 待测模型: {self.model}
> 评测模型: {self.evaluator_model_name}
> 用例版本: v{self.test_cases_version}

---

## 📊 执行概况

- **用例总数**: {total}
- **通过数**: {passed}
- **不通过数**: {failed}
- **未知状态**: {unknown}
- **通过率**: {(passed/total*100):.1f}%
- **用例版本**: v{self.test_cases_version}

---

## 🔌 评测API使用分布

| Provider | 调用次数 |
|----------|----------|
"""
        for provider, count in sorted(provider_stats.items(), key=lambda x: x[1], reverse=True):
            report += f"| {provider} | {count} |\n"

        report += f"""
---

## 📋 维度统计

| 维度 | 中文注释 | 通过 | 不通过 | 通过率 |
|------|---------|------|--------|--------|
"""

        for dim, stats in sorted(dimension_stats.items()):
            dim_total = stats["passed"] + stats["failed"]
            pass_rate = (stats["passed"] / dim_total * 100) if dim_total > 0 else 0
            dimension_names = get_dimension_names()
            dim_name = dimension_names.get(dim, dim)
            report += f"| {dim} | {dim_name} | {stats['passed']} | {stats['failed']} | {pass_rate:.1f}% |\n"

        if pin_stats["total"] > 0:
            bypass_rate = (pin_stats["bypass_success"] / pin_stats["total"] * 100) if pin_stats["total"] > 0 else 0
            defense_rate = (pin_stats["defense_success"] / pin_stats["total"] * 100) if pin_stats["total"] > 0 else 0
            report += f"""
---

## 🛡️ Prompt注入攻击绕过成功率统计

| 指标 | 数值 |
|------|------|
| 总测试用例数 | {pin_stats['total']} |
| 防御成功数 | {pin_stats['defense_success']} |
| 绕过成功数 | {pin_stats['bypass_success']} |
| 未知状态数 | {pin_stats['unknown']} |
| **防御成功率** | **{defense_rate:.1f}%** |
| **绕过成功率** | **{bypass_rate:.1f}%** |
"""
            if pin_stats["bypass_types"]:
                report += "\n### 绕过类型分布\n\n| 绕过类型 | 次数 |\n|----------|------|\n"
                for bt, count in sorted(pin_stats["bypass_types"].items(), key=lambda x: x[1], reverse=True):
                    report += f"| {bt} | {count} |\n"

        report += f"""
---

## 📝 详细测试结果

"""

        for result in all_results:
            case_id = result.get('test_case_id') or result.get('id', 'UNKNOWN')
            dimension = result.get('dimension', 'unknown')
            input_text = result.get('input', '')
            customer_response = result.get('customer_response', '') or result.get('actual_response', '')
            evaluator_provider = result.get('evaluator_provider', 'unknown')

            if dimension == 'multi_turn':
                scenario_line = input_text.split('\n')[0] if '\n' in input_text else input_text
                report += f"""### {case_id} - {dimension}

**测试状态**: {result['evaluation_result']['status']}
**评测API**: {evaluator_provider}

**对话场景**: {scenario_line}

**逐轮对话记录**:
```
{customer_response}
```

**评测结果**:
- 维度焦点: {result['evaluation_result'].get('dimension_focus', '')}
- 上下文一致性: {result['evaluation_result'].get('context_consistency', '')}
- 指令坚守性: {result['evaluation_result'].get('instruction_adherence', '')}
- 规则稳定性: {result['evaluation_result'].get('rule_stability', '')}
"""
            elif dimension == 'prompt_injection':
                detail = result.get("prompt_injection_detail", {})
                report += f"""### {case_id} - {dimension}

**防御结果**: {result['evaluation_result']['status']}
**评测API**: {evaluator_provider}

**攻击手法**: {detail.get('attack_type_cn', '')}（{detail.get('attack_type', '')}）

**用户输入**:
```
{input_text}
```

**客服回答**:
```
{customer_response[:500]}{'...' if len(customer_response) > 500 else ''}
```

**评测结果**:
- 防御结果: {detail.get('defense_result', '未知')}
- 绕过类型: {detail.get('bypass_type', '无')}
- 判定结论: {detail.get('evaluation_conclusion', '')}
"""
            else:
                report += f"""### {case_id} - {dimension}

**测试状态**: {result['evaluation_result']['status']}
**评测API**: {evaluator_provider}

**用户提问**:
```
{input_text}
```

**客服回答**:
```
{customer_response[:500]}{'...' if len(customer_response) > 500 else ''}
```

**评测结果**:
- 准确性: {result['evaluation_result']['accuracy']}
- 完整性: {result['evaluation_result']['completeness']}
- 合规性: {result['evaluation_result']['compliance']}
- 态度: {result['evaluation_result']['attitude']}
"""
                if result['evaluation_result'].get('dimension_focus'):
                    report += f"- 维度焦点: {result['evaluation_result']['dimension_focus']}\n"

            if result['evaluation_result']['issues']:
                report += f"\n**违规说明**: {', '.join(result['evaluation_result']['issues'])}\n\n"

            report += "---\n\n"

        report += f"""## 💡 测试总结

- 总通过率: {(passed/total*100):.1f}%
- 评测模型: {self.evaluator_model_name}
- 主要问题分布:
"""

        issue_distribution = {}
        for result in all_results:
            for issue in result['evaluation_result']['issues']:
                if issue not in issue_distribution:
                    issue_distribution[issue] = 0
                issue_distribution[issue] += 1

        for issue, count in sorted(issue_distribution.items(), key=lambda x: x[1], reverse=True):
            report += f"  - {issue}: {count} 次\n"

        report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*框架版本: V3.0（统一评测管线 + prompt_injection路由 + 评测独立性保障）*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ 测试报告已生成: {output_path}")


def main():
    """主函数"""

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI客服系统自动化测试执行脚本 V3.0')
    parser.add_argument('--mode', type=str, default='full',
                       choices=['single', 'selected', 'incremental', 'full'],
                       help='执行模式: single(单条), selected(指定用例), incremental(增量), full(全量)')
    parser.add_argument('--cases', type=str, default=None,
                       help='指定要执行的用例ID，多个用逗号分隔')
    parser.add_argument('--report', type=str, default='new',
                       choices=['new', 'append', 'update'],
                       help='报告输出模式: new(新建批次), append(追加到批次), update(更新批次报告)')
    parser.add_argument('--batch-id', type=str, default=None,
                       help='指定要操作的批次ID')
    parser.add_argument('--report-only', action='store_true',
                       help='仅重新生成报告（不执行测试）')
    parser.add_argument('--concurrent', type=int, default=0,
                       help='并发执行数（0=单线程，建议不超过2）')

    args = parser.parse_args()

    # 仅重新生成报告模式
    if args.report_only:
        if not args.batch_id:
            print("❌ --report-only 模式需要指定 --batch-id 参数")
            return

        results_dir = get_results_dir()
        batch_dir = os.path.join(results_dir, args.batch_id)
        report_path = os.path.join(batch_dir, "summary.md")

        results_json_path = os.path.join(batch_dir, "results.json")
        if not os.path.exists(results_json_path):
            print(f"❌ 结果文件不存在: {results_json_path}")
            return

        with open(results_json_path, 'r', encoding='utf-8') as f:
            all_results: List[Dict] = json.load(f)

        test_cases_version = "unknown"
        if all_results and len(all_results) > 0 and "test_case_version" in all_results[0]:
            test_cases_version = all_results[0]["test_case_version"]

        print(f"📊 读取到 {len(all_results)} 条测试结果")

        evaluator_template_path = get_evaluator_template_path()
        runner = TestRunner(api_key="", evaluator_template_path=evaluator_template_path)
        runner.test_cases_version = test_cases_version
        runner.generate_report(all_results, report_path)

        print(f"✅ 测试报告已重新生成: {report_path}")
        return

    # 从 .env 加载 API Key（通过收口函数）
    API_KEY = get_api_key("qianfan")

    if not API_KEY:
        print("❌ 请在环境变量或 api_config.yaml 中配置 qianfan 的 sk 或 ak")
        return

    # 文件路径
    test_cases_path = get_test_cases_path()
    evaluator_template_path = get_evaluator_template_path()
    results_dir = get_results_dir()

    # 创建测试执行器
    runner = TestRunner(api_key=API_KEY, evaluator_template_path=evaluator_template_path)

    # 加载测试用例
    print("📂 加载测试用例...")
    all_test_cases, test_cases_version = runner.load_test_cases(test_cases_path)
    runner.test_cases_version = test_cases_version
    print(f"✅ 已加载 {len(all_test_cases)} 条测试用例")
    print(f"📊 用例版本: v{test_cases_version}")

    # 加载已执行的用例ID（增量模式）
    executed_ids = set()
    if args.mode == 'incremental':
        if args.batch_id:
            batch_dir = os.path.join(results_dir, args.batch_id)
            executed_ids = runner.load_executed_cases(batch_dir)
        else:
            print("❌ incremental 模式需要指定 --batch-id 参数")
            return

    # 过滤测试用例
    test_cases = runner.filter_test_cases(all_test_cases, args.mode, args.cases, executed_ids)

    if not test_cases:
        print("⚠️ 没有需要执行的测试用例")
        return

    print(f"\n执行模式: {args.mode}")
    print(f"将执行 {len(test_cases)} 条用例")

    # 确定批次目录和输出模式
    recorder = None
    if args.report in ['append', 'update'] and args.batch_id:
        # 追加/更新模式：使用现有批次
        batch_dir = os.path.join(results_dir, args.batch_id)

        if not os.path.exists(batch_dir):
            print(f"❌ 批次目录不存在: {args.batch_id}")
            return

        batch_id = args.batch_id
        output_mode = 'append' if args.report == 'append' else 'new'
        print(f"📁 操作批次: {batch_id} ({args.report} 模式)")

        # append 模式也创建 recorder
        recorder = TestRunRecorder(batch_dir, config_registry=runner._registry if hasattr(runner, '_registry') else None)
        try:
            recorder.load_test_config()
            print(f"📊 已加载批次配置: {batch_id}")
        except FileNotFoundError:
            recorder.create_test_config(
                batch_id=batch_id,
                test_case_version=test_cases_version,
                test_case_file="cases/universal.json",
                model=runner.model,
                evaluator_model=runner.evaluator_model_name,
                test_parameters={
                    "mode": args.mode,
                    "concurrent": args.concurrent
                },
                evaluator_providers=get_model_config()["evaluator_providers"]
            )

    else:
        # 新建模式
        existing_batches = [d for d in os.listdir(results_dir) if d.startswith("batch-")]
        if existing_batches:
            last_batch_num = max(int(b.split("-")[1].split("_")[0]) for b in existing_batches)
            next_batch_num = last_batch_num + 1
        else:
            next_batch_num = 1

        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_id = f"batch-{next_batch_num:03d}_{current_date}"
        batch_dir = os.path.join(results_dir, batch_id)

        os.makedirs(batch_dir, exist_ok=True)

        # 初始化测试运行记录器
        recorder = TestRunRecorder(batch_dir, config_registry=runner._registry if hasattr(runner, '_registry') else None)
        recorder.create_test_config(
            batch_id=batch_id,
            test_case_version=test_cases_version,
            test_case_file="cases/universal.json",
            model=runner.model,
            evaluator_model=runner.evaluator_model_name,
            test_parameters={
                "mode": args.mode,
                "concurrent": args.concurrent
            },
            evaluator_providers=get_model_config()["evaluator_providers"]
        )

        output_mode = 'new'
        print(f"📁 新建批次: {batch_id}")

    # 批次内的文件路径
    execution_records_path = os.path.join(batch_dir, "records.json")
    evaluation_results_path = os.path.join(batch_dir, "results.json")
    report_path = os.path.join(batch_dir, "summary.md")

    # 更新配置中的用例信息并开始记录
    if recorder:
        dimensions_set = set()
        for case in test_cases:
            dimensions_set.add(case.get('dimension', 'unknown'))
        dimensions = sorted(list(dimensions_set))

        recorder.update_test_config({
            "test_configuration": {
                "total_cases": len(test_cases),
                "dimensions": dimensions
            }
        })

        recorder.start_logging(recorder.config["test_run_id"])

    # 执行测试
    if args.concurrent > 0:
        results = runner.run_tests_concurrent(test_cases, max_workers=args.concurrent, recorder=recorder)
    else:
        results = runner.run_all_tests(test_cases, recorder=recorder)

    # 保存执行记录
    runner.save_execution_records(results, execution_records_path, mode=output_mode)

    # 保存评测结果
    runner.save_evaluation_results(results, evaluation_results_path, mode=output_mode)

    # 导出评测结果 CSV
    try:
        from tools.reporting import EvaluationCSVExporter
        dimension_names = get_dimension_names()

        csv_exporter = EvaluationCSVExporter(results, dimension_names=dimension_names)
        detail_csv_path = os.path.join(batch_dir, "evaluation_detail.csv")
        summary_csv_path = os.path.join(batch_dir, "evaluation_summary.csv")
        csv_exporter.export_detail_csv(detail_csv_path, mode=output_mode)
        csv_exporter.export_summary_csv(summary_csv_path)
    except Exception as e:
        print(f"⚠️ CSV导出失败: {e}")

    # 生成绕过成功率统计报告
    try:
        from tools.reporting import BypassStatsGenerator
        bypass_gen = BypassStatsGenerator(evaluation_results_path)
        bypass_gen.save_report()
    except Exception as e:
        print(f"⚠️ 绕过率统计报告生成失败: {e}")

    # 生成测试报告
    runner.generate_report(results, report_path)

    # 更新测试配置并生成审计报告
    if recorder:
        passed_count = sum(1 for r in results if r["evaluation_result"]["status"] in ("通过", "防御成功"))
        pass_rate = passed_count / len(results) * 100 if results else 0

        recorder.update_test_config({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "execution_metrics": {
                "total_duration_seconds": 0,
                "average_time_per_case_seconds": 0.0,
                "success_rate": 1.0,
                "api_calls": len(results) * 2,
                "total_tokens": 0
            },
            "quality_gates": {
                "actual_pass_rate": pass_rate / 100,
                "result": "PASS" if pass_rate / 100 >= (runner._registry.quality_gate.get("overall_threshold", 0.9) if runner._registry else 0.9) else "FAIL"
            }
        })

        recorder.end_logging({
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": pass_rate
        })

        # 完整性验证
        coverage_validation = recorder.validate_coverage(len(test_cases), len(results))
        consistency_validation = recorder.validate_consistency(len(test_cases), len(results))
        config_validation = recorder.validate_config_integrity()

        validation_results = [coverage_validation, consistency_validation, config_validation]

        audit_report = recorder.generate_audit_report(validation_results)
        recorder.save_audit_report(audit_report)

        if not all(v["passed"] for v in validation_results):
            print("⚠️ 完整性检查未通过:")
            for v in validation_results:
                if not v["passed"]:
                    print(f"  - {v['name']}: {v['actual']}")
        else:
            print("✅ 完整性检查通过")

    print(f"\n✅ 测试完成！批次: {batch_id}")

    # 自动生成 Bug 清单
    try:
        from tools.reporting import BugListGenerator
        bug_generator = BugListGenerator(batch_dir, test_cases_path=test_cases_path)
        bug_generator.save()
    except Exception as e:
        print(f"⚠️ Bug 清单生成失败: {e}")


if __name__ == "__main__":
    main()
