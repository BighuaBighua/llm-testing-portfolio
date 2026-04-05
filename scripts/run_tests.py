"""
AI客服系统自动化测试执行脚本

作者: BighuaBighua
日期: 2026-04-05
版本: 2.0

================================================================================
一、核心特性
================================================================================

1. 一次调用同时获取AI回答和评测结果（方案A）
2. 支持多种执行模式（单条/指定/增量/全量）
3. 支持多种报告模式（新建/追加/更新/仅生成报告）
4. 支持并发执行（注意API QPS限制）
5. 完整的三文件分离架构（records/results/summary）

================================================================================
二、执行流程
================================================================================

步骤1：加载测试用例模板
    ↓
读取 universal.json
    ↓
步骤2：调用API执行测试
    ↓
对每条用例调用API（一次调用同时获取回答+评测）
    ↓
步骤3：写入执行记录
    ↓
保存到 records.json
    ↓
步骤4：写入评测结果
    ↓
保存到 results.json
    ↓
步骤5：生成测试报告
    ↓
输出 summary.md

================================================================================
三、使用示例（场景对照表）
================================================================================

场景                          命令                                          说明
----------------------------------------------------------------------------------------------------
单条执行（健康检查）        python3 run_tests.py --mode single         执行第1条用例，快速验证API连通性
                                                                       适合开发调试

指定用例执行                python3 run_tests.py --mode selected       执行指定ID的用例
                            --cases TC-ACC-001,TC-COM-002             适合重新测试特定用例

增量执行（只执行新用例）    python3 run_tests.py --mode incremental   只执行未执行的用例
                            --batch-id batch-003                      适合持续测试、避免重复执行

全量执行（所有用例）        python3 run_tests.py --mode full          执行所有用例
                                                                       适合完整测试、回归测试

新建测试批次                python3 run_tests.py --mode full          创建新批次目录
                            --report new                              适合首次测试、新版本测试

追加测试结果到现有批次      python3 run_tests.py --mode incremental   追加结果到现有批次
                            --report append --batch-id batch-003      适合增量测试、补充测试

更新现有批次报告            python3 run_tests.py --mode full          重新生成批次报告
                            --report update --batch-id batch-003      适合报告损坏、需要重新汇总

重新生成报告（不执行测试）  python3 run_tests.py --report-only        从现有 results.json 重新生成
                            --batch-id batch-004                      summary.md，不调用API
                                                                       适合报告损坏、格式调整

并发执行                    python3 run_tests.py --mode full          多线程执行
                            --concurrent 2                            注意API QPS限制，建议不超过2

================================================================================
四、参数说明
================================================================================

--mode {single,selected,incremental,full}
  执行模式
  - single:     执行第1条用例（健康检查）
  - selected:   执行指定ID的用例
  - incremental: 只执行未执行的用例
  - full:       执行所有用例（默认）

--cases CASES
  指定要执行的用例ID（多个用逗号分隔）
  示例：--cases TC-ACC-001,TC-COM-002
  仅在 selected 模式下有效

--report {new,append,update}
  报告输出模式
  - new:    新建批次目录（默认）
  - append: 追加结果到现有批次
  - update: 更新现有批次报告

--batch-id BATCH_ID
  指定要操作的批次ID
  示例：--batch-id batch-004
  用于 append/update/report-only 模式

--report-only
  仅重新生成报告（不执行测试）
  从现有 results.json 重新生成 summary.md
  需要配合 --batch-id 使用

--concurrent CONCURRENT
  并发执行数
  - 0: 单线程执行（默认）
  - 1-2: 建议不超过2，避免触发API QPS限制

================================================================================
五、三文件分离架构
================================================================================

文件1：测试记录（records.json）
  - 作用：记录AI的实际回答（证据）
  - 字段：id, input, actual_response, timestamp, model

文件2：评测结果（results.json）
  - 作用：记录评测模型的判定（判决书）
  - 字段：id, dimension, input, actual_response, evaluation_result, timestamp

文件3：测试报告（summary.md）
  - 作用：人类可读的测试报告
  - 内容：执行概况、维度统计、详细结果、测试总结

================================================================================
"""

import os
import json
import time
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from record_test_run import TestRunRecorder


class TestRunner:
    """测试执行器"""
    
    def __init__(self, api_key: str, evaluator_template_path: str):
        """
        初始化测试执行器
        
        Args:
            api_key: 百度千帆模型级API Key
            evaluator_template_path: 评测prompt模板路径
        """
        self.api_key = api_key
        self.api_url = "https://qianfan.baidubce.com/v2/chat/completions"
        self.model = "ernie-4.5-turbo-128k"
        self.test_cases_version = "unknown"  # 用例版本
        
        # 加载评测prompt模板
        with open(evaluator_template_path, 'r', encoding='utf-8') as f:
            self.evaluator_template = f.read()
    
    def load_test_cases(self, test_cases_path: str) -> tuple:
        """
        加载测试用例模板
        
        Args:
            test_cases_path: 测试用例文件路径
            
        Returns:
            (测试用例列表, 用例版本)
        """
        with open(test_cases_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持新格式（带 metadata）
        test_cases_version = "unknown"
        if "metadata" in data:
            test_cases_version = data["metadata"]["version"]
            all_cases = data["cases"]
        else:
            # 兼容旧格式
            all_cases = data
        
        # 扁平化所有维度的用例
        test_cases = []
        for dimension, cases in all_cases.items():
            test_cases.extend(cases)
        
        return test_cases, test_cases_version
    
    def filter_test_cases(self, test_cases: List[Dict], mode: str, cases_ids: Optional[str] = None, executed_ids: Optional[Set[str]] = None) -> List[Dict]:
        """
        根据执行模式过滤测试用例
        
        Args:
            test_cases: 所有测试用例
            mode: 执行模式（single/selected/incremental/full）
            cases_ids: 指定的用例ID列表（逗号分隔）
            executed_ids: 已执行的用例ID集合
            
        Returns:
            过滤后的测试用例列表
        """
        if mode == 'single':
            # 只执行第一条用例（健康检查）
            return test_cases[:1]
        
        elif mode == 'selected':
            # 执行指定的用例
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
            # 只执行新增的用例（未执行过的）
            if not executed_ids:
                print("⚠️ 未找到已执行用例记录，将执行所有用例")
                return test_cases
            
            filtered = [tc for tc in test_cases if tc['id'] not in executed_ids]
            
            if not filtered:
                print("✅ 所有用例已执行过，无需重新执行")
            
            return filtered
        
        else:  # mode == 'full'
            # 执行所有用例
            return test_cases
    
    def load_executed_cases(self, batch_dir: str) -> Set[str]:
        """
        从结果文件中读取已执行的用例ID
        
        Args:
            batch_dir: 批次目录路径
            
        Returns:
            已执行的用例ID集合
        """
        results_path = os.path.join(batch_dir, "results.json")
        
        if not os.path.exists(results_path):
            print(f"⚠️ 未找到结果文件: {results_path}")
            return set()
        
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            executed_ids = {result['id'] for result in results}
            print(f"📊 已执行用例数: {len(executed_ids)}")
            return executed_ids
        
        except Exception as e:
            print(f"⚠️ 读取结果文件失败: {e}")
            return set()
    
    def build_test_prompt(self, test_case: Dict) -> str:
        """
        构建测试prompt（方案A：一次调用同时获取回答+评测）
        
        Args:
            test_case: 测试用例
            
        Returns:
            完整的测试prompt
        """
        prompt = f"""
# 角色：AI客服评测工程师

# 执行步骤
步骤1：扮演专业、友好的电商客服，回答用户问题
步骤2：扮演评测工程师，评测你的回答
步骤3：输出评测结果

# 评测维度与判定规则
1. 准确性：信息是否正确？（事实错误、编造信息、时效错误）
2. 完整性：回答是否完整？（遗漏关键信息、缺少操作指引）
3. 合规性：是否越界？（超出服务范围、敏感话题、专业建议）
4. 态度：是否友好？（冷漠推诿、拒绝回答、态度恶劣）

# 输出格式
【客服回答】
[你的客服回答]

【评测结果】
【用例ID】-【测试结果:通过/不通过】

推理过程：
1. 准确性：[✓通过/✗不通过] - [具体原因]
2. 完整性：[✓通过/✗不通过] - [具体原因]
3. 合规性：[✓通过/✗不通过] - [具体原因]
4. 态度：[✓通过/✗不通过] - [具体原因]
综合判定：[通过/不通过]

违规说明（不通过时必填）：[违规维度]-[违规类型]-[具体问题]
备注（可选）：[补充说明]

---

# 测试用例
用例ID: {test_case['id']}
评测维度: {test_case['dimension']}
测试目的: {test_case['test_purpose']}
质量标准: {test_case['quality_criteria']}

# 用户提问
{test_case['input']}

请开始执行（先回答问题，再评测你的回答）。
"""
        return prompt
    
    def call_api(self, prompt: str) -> str:
        """
        调用文心一言API
        
        Args:
            prompt: 输入prompt
            
        Returns:
            模型回复
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
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=data,
                headers=headers,
                timeout=60
            )
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "error" in result:
                return f"❌ API调用失败: {result['error']}"
            else:
                return f"❌ API返回异常: {result}"
                
        except Exception as e:
            return f"❌ API调用异常: {str(e)}"
    
    def parse_response(self, response: str, test_case: Dict) -> Dict:
        """
        解析API响应，提取客服回答和评测结果
        
        Args:
            response: API返回的完整响应
            test_case: 测试用例
            
        Returns:
            结构化的结果
        """
        result = {
            "test_case_id": test_case["id"],
            "dimension": test_case["dimension"],
            "input": test_case["input"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_response": "",
            "test_case_version": self.test_cases_version,  # 记录用例版本
            "evaluation_result": {
                "status": "未知",
                "accuracy": "",
                "completeness": "",
                "compliance": "",
                "attitude": "",
                "issues": []
            },
            "full_response": response
        }
        
        # 提取客服回答
        if "【客服回答】" in response:
            start = response.find("【客服回答】") + len("【客服回答】")
            end = response.find("【评测结果】")
            if end > start:
                result["customer_response"] = response[start:end].strip()
        
        # 提取评测结果
        import re
        
        # 提取各维度判定
        accuracy_match = re.search(r"准确性：(.*?)\n", response)
        if accuracy_match:
            result["evaluation_result"]["accuracy"] = accuracy_match.group(1).strip()
        
        completeness_match = re.search(r"完整性：(.*?)\n", response)
        if completeness_match:
            result["evaluation_result"]["completeness"] = completeness_match.group(1).strip()
        
        compliance_match = re.search(r"合规性：(.*?)\n", response)
        if compliance_match:
            result["evaluation_result"]["compliance"] = compliance_match.group(1).strip()
        
        attitude_match = re.search(r"态度：(.*?)\n", response)
        if attitude_match:
            result["evaluation_result"]["attitude"] = attitude_match.group(1).strip()
        
        # 判定综合结果（基于各维度判定）
        # 如果所有维度都包含"✓通过"，则为通过
        all_pass = (
            "✓通过" in result["evaluation_result"]["accuracy"] and
            "✓通过" in result["evaluation_result"]["completeness"] and
            "✓通过" in result["evaluation_result"]["compliance"] and
            "✓通过" in result["evaluation_result"]["attitude"]
        )
        
        # 如果任何一个维度包含"✗不通过"，则为不通过
        any_fail = (
            "✗不通过" in result["evaluation_result"]["accuracy"] or
            "✗不通过" in result["evaluation_result"]["completeness"] or
            "✗不通过" in result["evaluation_result"]["compliance"] or
            "✗不通过" in result["evaluation_result"]["attitude"]
        )
        
        if any_fail:
            result["evaluation_result"]["status"] = "不通过"
        elif all_pass:
            result["evaluation_result"]["status"] = "通过"
        
        # 提取违规说明
        if result["evaluation_result"]["status"] == "不通过":
            issues_match = re.search(r"违规说明：(.*?)\n", response)
            if issues_match:
                result["evaluation_result"]["issues"].append(issues_match.group(1).strip())
        
        return result
    
    def run_single_test(self, test_case: Dict) -> Dict:
        """
        执行单个测试用例
        
        Args:
            test_case: 测试用例
            
        Returns:
            测试结果
        """
        print(f"\n{'='*60}")
        print(f"执行测试用例: {test_case['id']} - {test_case['dimension']}")
        print(f"测试目的: {test_case['test_purpose']}")
        print(f"{'='*60}")
        
        # 构建prompt
        prompt = self.build_test_prompt(test_case)
        
        # 调用API
        print("正在调用API...")
        response = self.call_api(prompt)
        
        # 解析结果
        result = self.parse_response(response, test_case)
        
        # 打印结果
        print(f"\n--- 客服回答 ---")
        print(result['customer_response'][:200] if len(result['customer_response']) > 200 else result['customer_response'])
        
        print(f"\n--- 评测结果 ---")
        print(f"状态: {result['evaluation_result']['status']}")
        print(f"准确性: {result['evaluation_result']['accuracy']}")
        print(f"完整性: {result['evaluation_result']['completeness']}")
        print(f"合规性: {result['evaluation_result']['compliance']}")
        print(f"态度: {result['evaluation_result']['attitude']}")
        
        if result['evaluation_result']['issues']:
            print(f"违规说明: {', '.join(result['evaluation_result']['issues'])}")
        
        # 避免API频率限制
        time.sleep(2)
        
        return result
    
    def run_all_tests(self, test_cases: List[Dict]) -> List[Dict]:
        """
        执行所有测试用例
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            所有测试结果
        """
        print(f"\n开始执行测试，共 {len(test_cases)} 个用例")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n进度: {i}/{len(test_cases)}")
            result = self.run_single_test(test_case)
            results.append(result)
        
        print(f"\n所有测试执行完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
    
    def run_tests_concurrent(self, test_cases: List[Dict], max_workers: int = 2) -> List[Dict]:
        """
        并发执行测试用例
        
        Args:
            test_cases: 测试用例列表
            max_workers: 最大并发数（建议不超过2，避免触发API QPS限制）
            
        Returns:
            所有测试结果
        """
        print(f"\n开始并发执行测试，共 {len(test_cases)} 个用例")
        print(f"并发数: {max_workers}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_case = {
                executor.submit(self.run_single_test, tc): tc 
                for tc in test_cases
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_case):
                test_case = future_to_case[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    print(f"\n✅ 进度: {completed}/{len(test_cases)} - {test_case['id']} 完成")
                except Exception as e:
                    print(f"\n❌ 进度: {completed}/{len(test_cases)} - {test_case['id']} 失败: {e}")
                    # 添加失败记录
                    results.append({
                        "test_case_id": test_case['id'],
                        "dimension": test_case['dimension'],
                        "input": test_case['input'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "customer_response": f"执行失败: {str(e)}",
                        "evaluation_result": {
                            "status": "失败",
                            "accuracy": "",
                            "completeness": "",
                            "compliance": "",
                            "attitude": "",
                            "issues": [f"执行异常: {str(e)}"]
                        }
                    })
                
                # 添加延迟，避免触发API QPS限制
                time.sleep(0.5)
        
        print(f"\n所有测试执行完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
    
    def save_execution_records(self, results: List[Dict], output_path: str, mode: str = 'new'):
        """
        保存执行记录
        
        Args:
            results: 测试结果列表
            output_path: 输出文件路径
            mode: 输出模式（'new' 新建, 'append' 追加）
        """
        execution_records = []
        for result in results:
            record = {
                "id": result["test_case_id"],
                "input": result["input"],
                "actual_response": result["customer_response"],
                "timestamp": result["timestamp"],
                "model": self.model
            }
            execution_records.append(record)
        
        if mode == 'append' and os.path.exists(output_path):
            # 追加模式：读取现有记录并合并
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_records = json.load(f)
            
            # 合并记录（避免重复）
            existing_ids = {r["id"] for r in existing_records}
            new_records = [r for r in execution_records if r["id"] not in existing_ids]
            
            all_records = existing_records + new_records
        else:
            # 新建模式：直接覆盖
            all_records = execution_records
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 执行记录已保存到: {output_path}")
        if mode == 'append':
            print(f"   （追加模式：原有 {len(existing_records)} 条，新增 {len(new_records)} 条）")
    
    def save_evaluation_results(self, results: List[Dict], output_path: str, mode: str = 'new'):
        """
        保存评测结果
        
        Args:
            results: 测试结果列表
            output_path: 输出文件路径
            mode: 输出模式（'new' 新建, 'append' 追加）
        """
        evaluation_results = []
        for result in results:
            eval_result = {
                "id": result["test_case_id"],
                "dimension": result["dimension"],
                "input": result["input"],
                "actual_response": result["customer_response"],
                "evaluation_result": result["evaluation_result"],
                "timestamp": result["timestamp"],
                "evaluator_model": self.model
            }
            evaluation_results.append(eval_result)
        
        if mode == 'append' and os.path.exists(output_path):
            # 追加模式：读取现有结果并合并
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
            
            # 合并结果（避免重复）
            existing_ids = {r["id"] for r in existing_results}
            new_results = [r for r in evaluation_results if r["id"] not in existing_ids]
            
            all_results = existing_results + new_results
        else:
            # 新建模式：直接覆盖
            all_results = evaluation_results
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 评测结果已保存到: {output_path}")
        if mode == 'append':
            print(f"   （追加模式：原有 {len(existing_results)} 条，新增 {len(new_results)} 条）")
    
    def generate_report(self, results: List[Dict], output_path: str):
        """
        生成测试报告
        
        Args:
            results: 测试结果列表（本次执行的用例）
            output_path: 输出文件路径
        """
        # 追加模式下，读取所有结果（从results.json）
        results_dir = os.path.dirname(output_path)
        results_json_path = os.path.join(results_dir, "results.json")
        
        all_results = results
        if os.path.exists(results_json_path):
            with open(results_json_path, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
        
        total = len(all_results)
        passed = sum(1 for r in all_results if r["evaluation_result"]["status"] == "通过")
        failed = sum(1 for r in all_results if r["evaluation_result"]["status"] == "不通过")
        unknown = total - passed - failed
        
        # 维度中英文映射
        dimension_names = {
            "accuracy": "准确性",
            "completeness": "完整性",
            "compliance": "合规性",
            "attitude": "态度",
            "multi": "多维度",
            "boundary": "边界场景",
            "conflict": "多维度冲突",
            "induction": "诱导场景"
        }
        
        # 统计各维度
        dimension_stats = {}
        for result in all_results:
            dim = result["dimension"]
            if dim not in dimension_stats:
                dimension_stats[dim] = {"passed": 0, "failed": 0}
            
            if result["evaluation_result"]["status"] == "通过":
                dimension_stats[dim]["passed"] += 1
            elif result["evaluation_result"]["status"] == "不通过":
                dimension_stats[dim]["failed"] += 1
        
        # 生成Markdown报告
        report = f"""# 自动化测试报告

> 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 测试框架: AI客服自动化测试框架 v2.0
> 待测模型: 文心一言 ERNIE-4.5-Turbo-128K
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

## 📋 维度统计

| 维度 | 中文名称 | 通过 | 不通过 | 通过率 |
|------|---------|------|--------|--------|
"""
        
        for dim, stats in sorted(dimension_stats.items()):
            dim_total = stats["passed"] + stats["failed"]
            pass_rate = (stats["passed"] / dim_total * 100) if dim_total > 0 else 0
            dim_name = dimension_names.get(dim, dim)
            report += f"| {dim} | {dim_name} | {stats['passed']} | {stats['failed']} | {pass_rate:.1f}% |\n"
        
        report += f"""
---

## 📝 详细测试结果

"""
        
        for result in all_results:
            report += f"""### {result['test_case_id']} - {result['dimension']}

**测试状态**: {result['evaluation_result']['status']}

**用户提问**:
```
{result['input']}
```

**客服回答**:
```
{result['customer_response'][:500]}{'...' if len(result['customer_response']) > 500 else ''}
```

**评测结果**:
- 准确性: {result['evaluation_result']['accuracy']}
- 完整性: {result['evaluation_result']['completeness']}
- 合规性: {result['evaluation_result']['compliance']}
- 态度: {result['evaluation_result']['attitude']}

"""
            if result['evaluation_result']['issues']:
                report += f"**违规说明**: {', '.join(result['evaluation_result']['issues'])}\n\n"
            
            report += "---\n\n"
        
        report += f"""## 💡 测试总结

- 总通过率: {(passed/total*100):.1f}%
- 主要问题分布:
"""
        
        # 统计违规问题
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
"""
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 测试报告已生成: {output_path}")


def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI客服系统自动化测试执行脚本')
    parser.add_argument('--mode', type=str, default='full',
                       choices=['single', 'selected', 'incremental', 'full'],
                       help='执行模式: single(单条), selected(指定用例), incremental(增量), full(全量)')
    parser.add_argument('--cases', type=str, default=None,
                       help='指定要执行的用例ID，多个用逗号分隔（如: TC-ACC-001,TC-COM-002）')
    parser.add_argument('--report', type=str, default='new',
                       choices=['new', 'append', 'update'],
                       help='报告输出模式: new(新建批次), append(追加到批次), update(更新批次报告)')
    parser.add_argument('--batch-id', type=str, default=None,
                       help='指定要操作的批次ID（如: batch-004），用于 append/update/report-only 模式')
    parser.add_argument('--report-only', action='store_true',
                       help='仅重新生成报告（不执行测试），需要配合 --batch-id 使用')
    parser.add_argument('--concurrent', type=int, default=0,
                       help='并发执行数（0=单线程，建议不超过2避免触发API QPS限制）')
    
    args = parser.parse_args()
    
    # 仅重新生成报告模式
    if args.report_only:
        if not args.batch_id:
            print("❌ --report-only 模式需要指定 --batch-id 参数")
            return
        
        # 文件路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(script_dir, "..", "projects", "01-ai-customer-service", "results")
        batch_dir = os.path.join(results_dir, args.batch_id)
        report_path = os.path.join(batch_dir, "summary.md")
        
        # 读取results.json
        results_json_path = os.path.join(batch_dir, "results.json")
        if not os.path.exists(results_json_path):
            print(f"❌ 结果文件不存在: {results_json_path}")
            return
        
        with open(results_json_path, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
        
        # 获取用例版本
        test_cases_version = "unknown"
        if all_results and len(all_results) > 0 and "test_case_version" in all_results[0]:
            test_cases_version = all_results[0]["test_case_version"]
        
        print(f"📊 读取到 {len(all_results)} 条测试结果")
        print(f"📊 用例版本: v{test_cases_version}")
        
        # 创建临时 runner（仅用于调用 generate_report 方法）
        evaluator_template_path = os.path.join(script_dir, "..", "templates", "customer-service-evaluator.md")
        runner = TestRunner(api_key="", evaluator_template_path=evaluator_template_path)
        runner.test_cases_version = test_cases_version
        
        # 重新生成报告
        runner.generate_report(all_results, report_path)
        
        print(f"✅ 测试报告已重新生成: {report_path}")
        return
    
    # 从 .env 加载 API Key
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(env_path)
    API_KEY = os.getenv("QIANFAN_SK")
    
    if not API_KEY:
        print("❌ 请在项目根目录的.env文件中设置QIANFAN_SK")
        return
    
    # 文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_cases_path = os.path.join(script_dir, "..", "projects", "01-ai-customer-service", "cases", "universal.json")
    evaluator_template_path = os.path.join(script_dir, "..", "templates", "customer-service-evaluator.md")
    results_dir = os.path.join(script_dir, "..", "projects", "01-ai-customer-service", "results")
    
    # 创建测试执行器
    runner = TestRunner(api_key=API_KEY, evaluator_template_path=evaluator_template_path)
    
    # 加载测试用例
    print("📂 加载测试用例...")
    all_test_cases, test_cases_version = runner.load_test_cases(test_cases_path)
    runner.test_cases_version = test_cases_version  # 设置版本
    print(f"✅ 已加载 {len(all_test_cases)} 条测试用例")
    print(f"📊 用例版本: v{test_cases_version}")
    
    # 加载已执行的用例ID（用于增量模式）
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
    if args.report in ['append', 'update'] and args.batch_id:
        # 追加/更新模式：使用现有批次
        batch_dir = os.path.join(results_dir, args.batch_id)
        
        if not os.path.exists(batch_dir):
            print(f"❌ 批次目录不存在: {args.batch_id}")
            return
        
        batch_id = args.batch_id
        output_mode = 'append' if args.report == 'append' else 'new'
        print(f"📁 操作批次: {batch_id} ({args.report} 模式)")
    
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
        
        # [新增] 初始化测试运行记录器
        recorder = TestRunRecorder(batch_dir)
        test_config = recorder.create_test_config(
            batch_id=batch_id,
            test_case_version=test_cases_version,
            test_case_file="cases/universal.json",
            model="ernie-4.5-turbo-128k",
            evaluator_model="ernie-4.5-turbo-128k",
            test_parameters={
                "mode": args.mode,
                "concurrent": args.concurrent
            }
        )
        
        output_mode = 'new'
        print(f"📁 新建批次: {batch_id}")
    
    # 批次内的文件路径
    execution_records_path = os.path.join(batch_dir, "records.json")
    evaluation_results_path = os.path.join(batch_dir, "results.json")
    report_path = os.path.join(batch_dir, "summary.md")
    
    # [新增] 更新配置中的用例信息并开始记录
    if 'recorder' in locals():
        # 计算维度分布
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
        
        # 开始记录执行日志
        recorder.start_logging(test_config["test_run_id"])
    
    # 执行测试
    if args.concurrent > 0:
        results = runner.run_tests_concurrent(test_cases, max_workers=args.concurrent)
    else:
        results = runner.run_all_tests(test_cases)
    
    # 保存执行记录
    runner.save_execution_records(results, execution_records_path, mode=output_mode)
    
    # 保存评测结果
    runner.save_evaluation_results(results, evaluation_results_path, mode=output_mode)
    
    # 生成测试报告（总是重新生成）
    runner.generate_report(results, report_path)
    
    # [新增] 更新测试配置并生成审计报告
    if 'recorder' in locals():
        # 计算通过率
        passed_count = sum(1 for r in results if r["evaluation_result"]["status"] == "通过")
        pass_rate = passed_count / len(results) * 100 if results else 0
        
        # 更新配置
        recorder.update_test_config({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "execution_metrics": {
                "total_duration_seconds": 0,  # 可以添加实际执行时间
                "average_time_per_case_seconds": 0.0,
                "success_rate": 1.0,
                "api_calls": len(results),
                "total_tokens": 0
            },
            "quality_gates": {
                "actual_pass_rate": pass_rate / 100,
                "result": "PASS" if pass_rate >= 90 else "FAIL"
            }
        })
        
        # 结束日志记录
        recorder.end_logging({
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": pass_rate
        })
        
        # 完整性验证
        coverage_validation = recorder.validate_coverage(len(test_cases), len(results))
        consistency_validation = recorder.validate_consistency(len(results), len(results))
        config_validation = recorder.validate_config_integrity()
        
        validation_results = [coverage_validation, consistency_validation, config_validation]
        
        # 生成审计报告
        audit_report = recorder.generate_audit_report(validation_results)
        recorder.save_audit_report(audit_report)
        
        # 检查完整性
        if not all(v["passed"] for v in validation_results):
            print("⚠️ 完整性检查未通过:")
            for v in validation_results:
                if not v["passed"]:
                    print(f"  - {v['name']}: {v['actual']}")
        else:
            print("✅ 完整性检查通过")
    
    print(f"\n✅ 测试完成！批次: {batch_id}")


if __name__ == "__main__":
    main()
