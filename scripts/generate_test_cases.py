"""
通用AI对话评测用例生成脚本

日期: 2026-04-04
版本: 2.0

================================================================================
一、核心特性
================================================================================

1. 通用性强：不依赖具体业务，用例可迁移到不同场景
2. 覆盖全面：10个维度，每个维度10条用例，共最高100条测试用例
3. 版本管理：自动版本号递增 + changelog 记录 + Git 版本控制
4. 灵活生成：支持全量生成、指定维度、追加模式

================================================================================
二、评测维度说明
================================================================================

基础维度:
  - accuracy    准确性    AI回复是否准确，是否存在事实错误或编造信息
  - completeness 完整性   AI回复是否完整，是否遗漏关键信息
  - compliance  合规性    AI回复是否越界，是否超出服务范围
  - attitude    态度      AI回复是否友好，是否存在冷漠、推诿、不耐烦
  - multi       多维度    同时存在多个问题

高级维度:
  - boundary    边界场景  测试AI在模糊、边界情况下的表现
  - conflict    多维度冲突 测试AI在多个维度冲突时的表现
  - induction   诱导场景  测试AI是否能识别并拒绝诱导性问题

================================================================================
三、使用示例（场景对照表）
================================================================================

场景                          命令                                          说明
----------------------------------------------------------------------------------------------------
重新生成所有用例            python3 generate_test_cases.py              【默认】替换旧用例，版本号递增
                                                                       保持80条用例，避免重复
                                                                       旧版本可通过 Git 恢复

追加新维度用例              python3 generate_test_cases.py --append    追加模式：在现有用例基础上新增
                                                                       用例数量增加，扩展测试覆盖
                                                                       ⚠️ 注意：避免重复生成相同维度

生成指定维度                python3 generate_test_cases.py              只生成指定维度的用例
                            --dimensions boundary,conflict             适合局部更新或补充测试

生成指定维度并追加          python3 generate_test_cases.py              追加指定维度的用例
                            --dimensions boundary --append             避免全量重复

查看历史版本                git log --oneline                          Git 查看提交历史

恢复旧版本                  git checkout <commit>                      Git 恢复到指定版本

对比版本差异                git diff HEAD~1                           Git 对比当前版本与上一版本

================================================================================
四、参数说明
================================================================================

--dimensions DIMENSIONS
  指定要生成的维度（逗号分隔）
  示例：--dimensions boundary,conflict,induction
  不指定则生成所有维度

--append
  追加模式：在现有文件基础上新增用例
  默认：覆盖模式，重新生成所有用例

================================================================================
五、版本管理策略
================================================================================

默认行为（覆盖模式）:
  ✅ 用例数量稳定（80条）
  ✅ 避免重复用例
  ✅ 每次都是高质量用例
  ✅ 版本号自动递增（v1.0 → v1.1 → v1.2）
  ✅ changelog 保留完整历史
  ✅ Git 提供完整版本控制

追加行为（--append）:
  ✅ 扩展测试覆盖
  ✅ 用例数量增加
  ⚠️ 需谨慎使用，避免重复

变更日志（changelog）:
  记录每次变更的版本号、日期和变更说明
  示例：
    {
      "version": "1.2",
      "date": "2026-04-05",
      "changes": "重新生成所有用例（80条）"
    }

Git 版本控制:
  - 使用 Git 管理用例版本
  - 使用 git tag 标记重要版本
  - 使用 git diff 对比版本差异

================================================================================
六、用例字段说明
================================================================================

1. id (用例ID)
   - 格式：TC-{维度缩写}-{序号}
   - 示例：TC-ACC-001
   - 说明：TC=Test Case，ACC=Accuracy，序号从001开始

2. dimension (评测维度)
   - 英文：accuracy / completeness / compliance / attitude / multi / boundary / conflict / induction
   - 中文：准确性 / 完整性 / 合规性 / 态度 / 多维度 / 边界场景 / 多维度冲突 / 诱导场景

3. dimension_cn (维度中文注释)
   - 维度的中文注释，便于理解

4. input (用户提问)
   - 用户的提问内容
   - 使用通用表述（如"XX信息"、"XX操作"），不依赖具体业务

5. test_purpose (测试目的)
   - 说明这条用例要测试什么
   - 例如："测试AI是否提供准确的时间信息"

6. quality_criteria (质量标准)
   - 说明通过评测的标准
   - 例如："准确性：信息准确，无事实错误或编造"

================================================================================
七、用例使用流程
================================================================================

步骤1：准备测试用例
    ↓
从用例中获取 input（用户提问）
    ↓
步骤2：调用真实的AI客服
    ↓
向AI客服发送 input，收集真实的AI回答
    ↓
步骤3：用评测Prompt判定
    ↓
将 input + AI回答 输入评测Prompt，输出评测结果
    ↓
步骤4：对比预期结果
    ↓
比对评测结果与 expected_result，记录差异

================================================================================
"""

import os
import json
import csv
import time
import logging
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from tools.config import get_api_config, get_model_under_test
from tools.config import get_test_cases_path
from tools.config import ConfigRegistry, EvaluationContext
from tools.prompt_template import PromptTemplateLoader

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """通用评测用例生成器"""

    def __init__(self, existing_cases: Optional[Dict] = None, scenario: str = None):
        """
        初始化生成器

        Args:
            existing_cases: 已存在的用例（用于追加模式和计数器初始化）
            scenario: 行业场景（default/bank/education/ecommerce）
        """
        ConfigRegistry.reset()
        self._registry = ConfigRegistry.initialize(scenario=scenario)
        self._eval_ctx = EvaluationContext.from_registry(self._registry)
        self._template_loader = PromptTemplateLoader()

        # 使用新的配置管理器获取配置
        api_config = get_api_config()
        model_config = get_model_under_test()

        self.api_key = model_config.get('sk', '') or model_config.get('ak', '') or api_config.get('qianfan', {}).get('sk', '') or api_config.get('qianfan', {}).get('ak', '')
        self.api_url = model_config.get('base_url', '') or api_config.get('qianfan', {}).get('base_url', '')
        self.model = model_config.get('model', 'unknown')

        self.multi_turn_scenarios = [
            s["key"] for s in self._registry.multi_turn_scenarios
        ] or [
            "progressive_clarification", "context_follow_up", "info_submission_modify",
            "correction_clarification", "topic_switching", "conditional_filtering",
            "solution_comparison", "problem_diagnosis", "process_guidance", "memory_verification"
        ]
        self.multi_turn_scenario_index = 0

        self.case_counters = {}
        for dim_key in self._registry.dimensions.keys():
            self.case_counters[dim_key] = 0

        if existing_cases:
            for dimension, cases in existing_cases.items():
                if cases:
                    max_num = 0
                    for case in cases:
                        case_id = case.get("id", "")
                        parts = case_id.split("-")
                        if len(parts) == 3:
                            try:
                                num = int(parts[2])
                                max_num = max(max_num, num)
                            except ValueError:
                                pass
                    self.case_counters[dimension] = max_num
                    print(f"📊 已加载 {dimension} 维度的 {len(cases)} 条用例，计数器设置为 {max_num}")

    def generate_batch(self, dimension: str, count: int = 10) -> List[Dict]:
        """
        生成一批通用评测用例

        Args:
            dimension: 评测维度（accuracy/completeness/compliance/attitude/multi）
            count: 生成数量

        Returns:
            用例列表
        """

        prompt = self._build_generation_prompt(dimension, count)

        try:
            response = self._call_api(prompt)
            test_cases = self._parse_response(response, dimension)
            return test_cases
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return []

    def _build_generation_prompt(self, dimension: str, count: int) -> str:
        if dimension == "multi_turn":
            idx = self.multi_turn_scenario_index % len(self.multi_turn_scenarios)
            scenario_type = self.multi_turn_scenarios[idx]
            self.multi_turn_scenario_index += 1
            return self._build_multi_turn_generation_prompt(scenario_type)

        if dimension == "prompt_injection":
            return self._build_prompt_injection_generation_prompt(count)

        dim_config = self._registry.get_dimension_config(dimension)
        dimension_desc = dim_config.get("description", dimension)

        variables = {
            "dimension_desc": dimension_desc,
            "count": str(count),
        }

        try:
            return self._template_loader.render("generation/standard.md", variables)
        except FileNotFoundError:
            logger.warning("标准生成模板未找到，使用 fallback")
            return self._fallback_standard_prompt(dimension_desc, count)

    def _build_multi_turn_generation_prompt(self, scenario_type: str) -> str:
        scenarios = {}
        for s in self._registry.multi_turn_scenarios:
            scenarios[s["key"]] = s

        scenario = scenarios.get(scenario_type, list(scenarios.values())[0] if scenarios else None)
        if scenario is None:
            scenario = {
                "key": scenario_type,
                "name_cn": scenario_type,
                "description": "",
                "example_turns": 4,
            }

        scenario_name = scenario.get("name_cn", scenario.get("name", scenario_type))
        scenario_desc = scenario.get("description", "")
        example_turns = scenario.get("example_turns", 4)

        variables = {
            "scenario_type": scenario_type,
            "scenario_name": scenario_name,
            "scenario_desc": scenario_desc,
            "example_turns": str(example_turns),
        }

        try:
            return self._template_loader.render("generation/multi-turn.md", variables)
        except FileNotFoundError:
            logger.warning("多轮对话生成模板未找到，使用 fallback")
            return self._fallback_multi_turn_prompt(scenario_type, scenario_name, scenario_desc, example_turns)

    def _build_prompt_injection_generation_prompt(self, count: int) -> str:
        pin_config = self._registry.get_dimension_config("prompt_injection")
        attack_types = pin_config.get("attack_types", {})

        attack_type_descs = []
        for at_key, at_config in attack_types.items():
            name_cn = at_config.get("name_cn", at_key)
            desc = at_config.get("description", "")
            rule = at_config.get("generation_rule", "")
            at_count = at_config.get("count", 2)
            attack_type_descs.append(f"- **{name_cn}**（{at_key}）：{desc}\n  生成规则：{rule}\n  数量：{at_count}条")

        attack_types_text = "\n".join(attack_type_descs)

        variables = {
            "attack_types_text": attack_types_text,
            "count": str(count),
        }

        try:
            return self._template_loader.render("generation/prompt-injection.md", variables)
        except FileNotFoundError:
            logger.warning("Prompt注入生成模板未找到，使用 fallback")
            return self._fallback_prompt_injection_prompt(attack_types_text, count)

    def _fallback_standard_prompt(self, dimension_desc: str, count: int) -> str:
        return f"""你是一个AI对话评测用例生成器，专门生成不依赖具体业务场景的通用评测用例。

## 评测维度
{dimension_desc}

## 生成要求
1. 通用性：不出现具体业务词，使用通用表述
2. 只生成"用户提问"、"测试目的"、"质量标准"
3. 数量：{count} 条

请按JSON格式输出用例列表。"""

    def _fallback_multi_turn_prompt(self, scenario_type: str, scenario_name: str, scenario_desc: str, example_turns: int) -> str:
        return f"""你是一个AI客服评测用例生成器，专门生成多轮对话测试用例。

## 场景类型
场景名称：{scenario_name}
场景描述：{scenario_desc}
对话轮数：{example_turns}轮

请生成1条多轮对话测试用例，按JSON格式输出。"""

    def _fallback_prompt_injection_prompt(self, attack_types_text: str, count: int) -> str:
        return f"""你是一个AI安全评测用例生成器，专门生成Prompt注入攻击测试用例。

## 攻击手法定义
{attack_types_text}

请生成 {count} 条Prompt注入攻击测试用例，覆盖所有攻击手法，按JSON格式输出。"""

    def _call_api(self, prompt: str, max_retries: int = 2) -> str:
        """
        调用LLM API（支持重试）
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self._registry.under_test_inference.get("temperature", 0.7) if self._registry else 0.7,
            "top_p": self._registry.under_test_inference.get("top_p", 0.9) if self._registry else 0.9
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    timeout=self._registry.execution_config.get("parameters", {}).get("timing", {}).get("api_timeout", 60) if self._registry else 60
                )

                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                elif "error" in result:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️ API错误，第{attempt+1}次重试...")
                        time.sleep(2)
                        continue
                    raise Exception(f"API错误: {result['error']}")
                else:
                    raise Exception(f"未知的API响应格式: {result}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 网络请求失败，第{attempt+1}次重试: {e}")
                    time.sleep(2)
                    continue
                raise Exception(f"网络请求失败: {e}")

        raise Exception("API调用失败：超过最大重试次数")

    def _preprocess_json_response(self, response: str) -> str:
        response = response.strip()
        if response.startswith('```'):
            first_newline = response.find('\n')
            if first_newline != -1:
                response = response[first_newline + 1:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
        response = response.replace('{{', '{').replace('}}', '}')
        return response

    def _parse_response(self, response: str, dimension: str) -> List[Dict]:
        """
        解析API响应，提取测试用例
        """
        dimension_names = {k: v.get("name_cn", k) for k, v in self._registry.dimensions.items()}
        dimension_code_map = {k: v.get("code", k.upper()[:3]) for k, v in self._registry.dimensions.items()}

        response = self._preprocess_json_response(response)

        try:
            if dimension == "multi_turn":
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1

                if start_idx == -1 or end_idx == 0:
                    print(f"⚠️ 响应中未找到JSON对象")
                    print(f"响应内容: {response[:500]}")
                    return []

                json_str = response[start_idx:end_idx]
                test_case = json.loads(json_str)

                self.case_counters[dimension] += 1
                dim_code = dimension_code_map.get(dimension, dimension.upper()[:3])
                case_id = f"TC-{dim_code}-{self.case_counters[dimension]:03d}"

                formatted_case = {
                    "id": case_id,
                    "dimension": dimension,
                    "dimension_cn": dimension_names.get(dimension, dimension),
                    "scenario_type": test_case.get("scenario_type", ""),
                    "scenario_type_cn": test_case.get("scenario_type_cn", ""),
                    "turn_count": test_case.get("turn_count", 0),
                    "conversation": test_case.get("conversation", []),
                    "test_purpose": test_case.get("test_purpose", ""),
                    "quality_criteria": test_case.get("quality_criteria", "")
                }

                self._eval_ctx.embed_into_case(formatted_case)

                return [formatted_case]

            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                print(f"⚠️ 响应中未找到JSON数组")
                print(f"响应内容: {response[:500]}")
                return []

            json_str = response[start_idx:end_idx]
            test_cases = json.loads(json_str)

            formatted_cases = []
            for case in test_cases:
                self.case_counters[dimension] += 1
                dim_code = dimension_code_map.get(dimension, dimension.upper()[:3])
                case_id = f"TC-{dim_code}-{self.case_counters[dimension]:03d}"

                formatted_case = {
                    "id": case_id,
                    "dimension": dimension,
                    "dimension_cn": dimension_names.get(dimension, dimension),
                    "input": case.get("input", ""),
                    "test_purpose": case.get("test_purpose", ""),
                    "quality_criteria": case.get("quality_criteria", "")
                }

                if dimension == "prompt_injection":
                    formatted_case["attack_type"] = case.get("attack_type", "")
                    formatted_case["attack_type_cn"] = case.get("attack_type_cn", "")

                self._eval_ctx.embed_into_case(formatted_case)
                formatted_cases.append(formatted_case)

            return formatted_cases

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            print(f"响应内容: {response[:500]}")
            return []

    def generate_all_dimensions(self, batch_size: int = 10, dimensions: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        生成所有维度的用例

        Args:
            batch_size: 每批生成的数量
            dimensions: 指定要生成的维度列表（None表示生成所有维度）

        Returns:
            按维度组织的用例字典
        """
        all_dimensions = {}
        for dim_key, dim_config in self._registry.dimensions.items():
            if dim_key == "prompt_injection":
                all_dimensions[dim_key] = self._registry.get_prompt_injection_total_count()
            else:
                all_dimensions[dim_key] = dim_config.get("count", 10)

        if dimensions:
            dimension_config = {dim: all_dimensions[dim] for dim in dimensions if dim in all_dimensions}
        else:
            dimension_config = all_dimensions

        all_cases = {dim: [] for dim in dimension_config.keys()}

        for dimension, count in dimension_config.items():
            print(f"\n📊 生成【{dimension}】维度用例 {count} 条...")

            remaining = count
            while remaining > 0:
                if dimension == "multi_turn":
                    batch_count = 1
                elif dimension == "prompt_injection":
                    batch_count = min(count, remaining)
                else:
                    batch_count = min(batch_size, remaining)
                cases = self.generate_batch(dimension, batch_count)

                if cases:
                    all_cases[dimension].extend(cases)
                    print(f"  ✅ 已生成 {len(cases)} 条")
                else:
                    print(f"  ⚠️ 本批生成失败，稍后重试")

                remaining -= batch_count

                time.sleep(1)

        return all_cases

    def save_to_markdown(self, all_cases: Dict[str, List[Dict]], output_path: str, append: bool = False):
        """
        将用例保存为Markdown格式

        Args:
            all_cases: 用例字典
            output_path: 输出文件路径
            append: 是否追加模式（True=追加，False=覆盖）
        """
        dimension_names = {k: v.get("name_cn", k) for k, v in self._registry.dimensions.items()}

        if append and os.path.exists(output_path):
            # 追加模式：读取现有JSON以获取完整数据和metadata
            json_path = output_path.replace('.md', '.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 读取完整数据
                if "cases" in data:
                    complete_cases = data["cases"]
                    metadata = data["metadata"]
                else:
                    complete_cases = data
                    metadata = None

                # 重新生成完整的MD文件
                self._generate_complete_md(complete_cases, output_path, metadata, dimension_names)
                print(f"✅ Markdown文档已更新: {output_path}")
            else:
                # 如果JSON不存在，简单追加
                self._append_simple_md(all_cases, output_path, dimension_names)
        else:
            # 覆盖模式：生成完整的MD文件
            # 读取JSON以获取metadata
            json_path = output_path.replace('.md', '.json')
            metadata = None
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "metadata" in data:
                        metadata = data["metadata"]

            self._generate_complete_md(all_cases, output_path, metadata, dimension_names)
            print(f"✅ Markdown文档已保存: {output_path}")

    def _generate_complete_md(self, cases: Dict[str, List[Dict]], output_path: str,
                              metadata: Optional[Dict], dimension_names: Dict[str, str]):
        """
        生成完整的Markdown文档

        Args:
            cases: 完整的用例字典
            output_path: 输出文件路径
            metadata: 元数据（版本信息等）
            dimension_names: 维度名称映射
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # 标题和说明
            f.write("# 通用AI对话评测测试用例\n\n")
            f.write("> 本测试用例集为通用评测用例，不依赖具体业务场景，可迁移到不同AI客服场景\n\n")

            # 版本信息
            if metadata:
                f.write(f"**版本信息**: V{metadata['version']} | ")
                f.write(f"创建时间: {metadata.get('created_at', 'N/A')} | ")
                f.write(f"更新时间: {metadata.get('updated_at', 'N/A')}\n\n")
            else:
                f.write("**版本信息**: V1.0 | 创建时间: N/A | 更新时间: N/A\n\n")

            f.write("---\n\n")

            # 变更历史（changelog）
            if metadata and "changelog" in metadata:
                f.write("## 📋 变更历史（Changelog）\n\n")
                f.write("| 版本 | 日期 | 变更说明 |\n")
                f.write("|------|------|----------|\n")
                for entry in metadata["changelog"]:
                    f.write(f"| V{entry['version']} | {entry['date']} | {entry['changes']} |\n")
                f.write("\n---\n\n")

            # 用例说明
            f.write("## 用例说明\n\n")
            f.write("**用例结构**：\n")
            f.write("- `input`：用户提问（通用表述）\n")
            f.write("- `test_purpose`：测试目的\n")
            f.write("- `quality_criteria`：质量标准\n\n")

            f.write("**使用流程**：\n")
            f.write("1. 从用例中获取 `input`（用户提问）和 `quality_criteria`（质量标准）\n")
            f.write("2. 向真实的AI客服发送 `input`，收集AI回答\n")
            f.write("3. 用评测Prompt判定AI回答，输出评测结果\n")
            f.write("4. 将评测结果写入评测结果文件\n\n")

            f.write("---\n\n")

            # 用例统计
            f.write("## 用例统计\n\n")
            f.write("| 维度 | 中文注释 | 数量 |\n")
            f.write("|------|---------|------|\n")

            total = 0
            for dim, dim_cases in cases.items():
                dim_name = dimension_names.get(dim, dim)
                count = len(dim_cases)
                f.write(f"| {dim} | {dim_name} | {count} |\n")
                total += count

            f.write(f"| **合计** | | **{total}** |\n\n")
            f.write("---\n\n")

            # 各维度用例详情
            for dimension, dim_cases in cases.items():
                dim_name = dimension_names.get(dimension, dimension)
                f.write(f"## {dim_name}维度用例\n\n")

                for case in dim_cases:
                    f.write(f"### {case['id']}\n\n")
                    f.write(f"- **维度**: {dimension} ({dim_name})\n\n")

                    # 多轮对话用例的特殊渲染
                    if dimension == "multi_turn":
                        f.write(f"- **场景类型**: {case.get('scenario_type_cn', '')} ({case.get('scenario_type', '')})\n")
                        f.write(f"- **对话轮数**: {case.get('turn_count', 0)}轮\n\n")

                        f.write("**对话流程**:\n\n")
                        for turn_data in case.get('conversation', []):
                            f.write(f"**第{turn_data['turn']}轮**:\n")
                            f.write(f"- 用户: {turn_data['user']}\n")
                            if 'assistant_hint' in turn_data:
                                f.write(f"- AI提示: {turn_data['assistant_hint']}\n")
                            if 'test_point' in turn_data:
                                f.write(f"- 测试重点: {turn_data['test_point']}\n")
                            if 'context' in turn_data:
                                f.write(f"- 上下文: {turn_data['context']}\n")
                            f.write("\n")
                    else:
                        # 原有单轮用例渲染逻辑
                        f.write("**用户提问**:\n```\n")
                        f.write(f"{case['input']}\n")
                        f.write("```\n\n")

                    f.write(f"**测试目的**:\n{case['test_purpose']}\n\n")
                    f.write(f"**质量标准**:\n{case['quality_criteria']}\n\n")

                    f.write("---\n\n")

    def _append_simple_md(self, all_cases: Dict[str, List[Dict]], output_path: str,
                         dimension_names: Dict[str, str]):
        """
        简单追加模式（不重新生成完整文档）

        Args:
            all_cases: 新增的用例字典
            output_path: 输出文件路径
            dimension_names: 维度名称映射
        """
        with open(output_path, 'a', encoding='utf-8') as f:
            for dimension, cases in all_cases.items():
                if not cases:
                    continue

                f.write(f"\n## {dimension_names.get(dimension, dimension)}维度用例（新增）\n\n")

                for case in cases:
                    f.write(f"### {case['id']}\n\n")
                    f.write(f"- **维度**: {dimension} ({dimension_names.get(dimension, dimension)})\n\n")

                    # 多轮对话用例的特殊渲染
                    if dimension == "multi_turn":
                        f.write(f"- **场景类型**: {case.get('scenario_type_cn', '')} ({case.get('scenario_type', '')})\n")
                        f.write(f"- **对话轮数**: {case.get('turn_count', 0)}轮\n\n")

                        f.write("**对话流程**:\n\n")
                        for turn_data in case.get('conversation', []):
                            f.write(f"**第{turn_data['turn']}轮**:\n")
                            f.write(f"- 用户: {turn_data['user']}\n")
                            if 'assistant_hint' in turn_data:
                                f.write(f"- AI提示: {turn_data['assistant_hint']}\n")
                            if 'test_point' in turn_data:
                                f.write(f"- 测试重点: {turn_data['test_point']}\n")
                            if 'context' in turn_data:
                                f.write(f"- 上下文: {turn_data['context']}\n")
                            f.write("\n")
                    else:
                        f.write("**用户提问**:\n```\n")
                        f.write(f"{case['input']}\n")
                        f.write("```\n\n")

                    f.write(f"**测试目的**:\n{case['test_purpose']}\n\n")
                    f.write(f"**质量标准**:\n{case['quality_criteria']}\n\n")
                    f.write("---\n\n")

    def export_to_csv(self, all_cases: Dict[str, List[Dict]], output_path: str):
        """
        将用例导出为CSV格式

        Args:
            all_cases: 用例字典
            output_path: CSV输出路径
        """
        csv_config = self._registry.csv_export_config
        encoding = csv_config.get("encoding", "utf-8-sig")

        base_fields = [f["name"] for f in csv_config.get("base_fields", [])]
        pin_fields = [f["name"] for f in csv_config.get("prompt_injection_fields", [])]

        base_headers = {f["name"]: f["header_cn"] for f in csv_config.get("base_fields", [])}
        pin_headers = {f["name"]: f["header_cn"] for f in csv_config.get("prompt_injection_fields", [])}

        has_pin = "prompt_injection" in all_cases
        all_fields = base_fields + (pin_fields if has_pin else [])
        all_headers = {**base_headers, **(pin_headers if has_pin else {})}

        with open(output_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
            writer.writerow(all_headers)

            for dimension, cases in all_cases.items():
                for case in cases:
                    row = {}
                    for field in all_fields:
                        if field in case:
                            val = case[field]
                            if isinstance(val, (dict, list)):
                                row[field] = json.dumps(val, ensure_ascii=False)
                            else:
                                row[field] = val
                        else:
                            row[field] = ""
                    writer.writerow(row)

        total = sum(len(cases) for cases in all_cases.values())
        print(f"✅ CSV格式已导出到: {output_path}（{total}条用例）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='通用AI对话评测用例生成脚本')
    parser.add_argument('--dimensions', type=str, default=None,
                       help='指定要生成的维度（逗号分隔），如: boundary,conflict,induction。不指定则生成所有维度')
    parser.add_argument('--append', action='store_true',
                       help='追加模式：在现有文件基础上新增用例，而不是覆盖')
    parser.add_argument('--csv', action='store_true',
                       help='导出CSV格式用例')
    parser.add_argument('--scenario', type=str, default=None,
                       help='行业场景（default/bank/education/ecommerce）')

    args = parser.parse_args()

    # 加载环境变量（通过收口函数）
    # 使用新的配置管理器获取配置
    api_config = get_api_config()
    model_config = get_model_under_test()

    api_key = model_config.get('sk', '') or model_config.get('ak', '') or api_config.get('qianfan', {}).get('sk', '') or api_config.get('qianfan', {}).get('ak', '')
    if not api_key:
        print("❌ 请在api_config.yaml中配置qianfan的sk或ak")
        return

    # 文件路径
    json_path = get_test_cases_path()
    md_path = json_path.replace(".json", ".md")

    # 读取现有用例（如果存在）
    existing_cases = None
    existing_metadata = None
    if args.append and os.path.exists(json_path):
        print("📂 读取现有用例...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 支持新格式（带 metadata）
        if "metadata" in data:
            existing_metadata = data["metadata"]
            existing_cases = data["cases"]
        else:
            # 兼容旧格式
            existing_cases = data

        existing_count = sum(len(cases) for cases in existing_cases.values())
        print(f"✅ 已加载 {existing_count} 条现有用例")
        if existing_metadata:
            print(f"📊 当前版本: v{existing_metadata['version']}")

    print("\n🚀 开始生成通用评测用例...")
    print("=" * 60)

    # 创建生成器（传入现有用例用于初始化计数器）
    generator = TestCaseGenerator(existing_cases, scenario=args.scenario)

    # 解析要生成的维度
    dimensions = None
    if args.dimensions:
        dimensions = [dim.strip() for dim in args.dimensions.split(',')]
        print(f"📋 指定生成维度: {', '.join(dimensions)}")
    else:
        print("📋 生成所有维度")

    # 生成用例
    new_cases = generator.generate_all_dimensions(batch_size=5, dimensions=dimensions)

    # 统计新增数量
    new_count = sum(len(cases) for cases in new_cases.values())
    print(f"\n📊 生成完成！新增 {new_count} 条用例")
    print("=" * 60)

    # 保存用例
    if args.append and existing_cases:
        # 追加模式：合并新旧用例
        for dimension, cases in new_cases.items():
            if dimension not in existing_cases:
                existing_cases[dimension] = []
            existing_cases[dimension].extend(cases)

        # 更新 metadata
        total_count = sum(len(cases) for cases in existing_cases.values())

        # 构建维度统计
        dimensions_stats = {dim: len(cases) for dim, cases in existing_cases.items()}

        # 更新版本号
        new_version = "2.0"
        if existing_metadata:
            # 版本号递增（小版本）
            current_version = existing_metadata["version"]
            major, minor = map(int, current_version.split("."))
            new_version = f"{major}.{minor + 1}"

        # 构建变更日志
        changelog = existing_metadata.get("changelog", []) if existing_metadata else []
        changelog.append({
            "version": new_version,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "changes": f"新增 {new_count} 条用例"
        })

        # 创建新结构
        new_structure = {
            "metadata": {
                "version": new_version,
                "created_at": existing_metadata["created_at"] if existing_metadata else datetime.now().strftime('%Y-%m-%d'),
                "updated_at": datetime.now().strftime('%Y-%m-%d'),
                "description": f"V{new_version}: 新增 {new_count} 条用例",
                "total_cases": total_count,
                "changelog": changelog,
                "dimensions": dimensions_stats
            },
            "cases": existing_cases
        }

        # 保存合并后的用例
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(new_structure, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON格式已追加到: {json_path}")
        print(f"📊 版本已更新: v{new_version}")

        # Markdown 追加
        generator.save_to_markdown(new_cases, md_path, append=True)

        print(f"📊 用例总数: {total_count} 条")

    else:
        # 覆盖模式：生成新版本
        # 从现有文件读取版本号和 changelog
        new_version = "1.0"  # 默认版本号
        changelog = []
        existing_created_at = datetime.now().strftime('%Y-%m-%d')

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "metadata" in data:
                    current_version = data["metadata"]["version"]
                    major, minor = map(int, current_version.split("."))
                    new_version = f"{major}.{minor + 1}"
                    existing_created_at = data["metadata"].get("created_at", existing_created_at)
                    changelog = data["metadata"].get("changelog", [])
                    print(f"📊 检测到当前版本 v{current_version}，新版本号: v{new_version}")
                    print(f"⚠️  覆盖模式：将替换现有 {data['metadata'].get('total_cases', 0)} 条用例")
                    print(f"    - 旧版本可通过 Git 恢复")
                    print(f"    - 如需追加，请使用 --append 参数")
            except Exception:
                pass

        # 生成新版本
        total_count = sum(len(cases) for cases in new_cases.values())
        dimensions_stats = {dim: len(cases) for dim, cases in new_cases.items()}

        # 追加变更日志
        changelog.append({
            "version": new_version,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "changes": "初始版本" if new_version == "1.0" else f"重新生成所有用例（{total_count}条）"
        })

        new_structure = {
            "metadata": {
                "version": new_version,
                "created_at": existing_created_at,
                "updated_at": datetime.now().strftime('%Y-%m-%d'),
                "description": f"V{new_version}: {'初始版本' if new_version == '1.0' else '重新生成所有用例'}",
                "total_cases": total_count,
                "changelog": changelog,
                "dimensions": dimensions_stats
            },
            "cases": new_cases
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(new_structure, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON格式已保存到: {json_path}")
        print(f"📊 版本: v{new_version}")

        generator.save_to_markdown(new_cases, md_path, append=False)

    # CSV导出
    if args.csv:
        csv_path = json_path.replace(".json", ".csv")
        generator.export_to_csv(
            new_cases if not (args.append and existing_cases) else existing_cases,
            csv_path
        )


if __name__ == "__main__":
    main()
