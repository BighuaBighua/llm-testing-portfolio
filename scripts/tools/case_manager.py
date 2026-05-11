"""CaseManager - 测试用例加载、过滤与增量判断

职责：
1. 加载测试用例模板（JSON格式）
2. 按执行模式过滤用例（single/selected/incremental/full）
3. 读取已执行用例ID集合（增量执行模式）
4. 组合方法：一次完成加载+过滤+增量判断

从 TestRunner 迁移而来，实现单一职责分离。
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple

from tools.config import get_test_cases_path, get_results_dir


class CaseManager:

    def __init__(self, project_name: str = None):
        self._project_name = project_name

    def load_test_cases(self, test_cases_path: str = None) -> Tuple[List[Dict], str]:
        """加载测试用例模板

        Args:
            test_cases_path: 测试用例文件路径，为空时从配置获取

        Returns:
            (测试用例列表, 用例版本)
        """
        if not test_cases_path:
            test_cases_path = str(get_test_cases_path())

        with open(test_cases_path, 'r', encoding='utf-8') as f:
            data: Dict = json.load(f)

        test_cases_version = "unknown"
        if "metadata" in data:
            test_cases_version = data["metadata"]["version"]
            all_cases = data["cases"]
        else:
            all_cases = data

        test_cases = []
        for _, cases in all_cases.items():
            test_cases.extend(cases)

        return test_cases, test_cases_version

    def filter_test_cases(self, test_cases: List[Dict], mode: str,
                          cases_ids: Optional[str] = None,
                          executed_ids: Optional[Set[str]] = None) -> List[Dict]:
        """根据执行模式过滤测试用例

        Args:
            test_cases: 全量测试用例列表
            mode: 执行模式 - single/selected/incremental/full
            cases_ids: selected模式下的用例ID（逗号分隔）
            executed_ids: 已执行的用例ID集合（incremental模式使用）
        """
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
        """从批次结果文件中读取已执行的用例ID集合（用于增量执行模式）"""
        results_path = os.path.join(batch_dir, "results.json")

        if not os.path.exists(results_path):
            print(f"⚠️ 未找到结果文件: {results_path}")
            return set()

        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                results: List[Dict] = json.load(f)
            if not isinstance(results, list):
                print(f"⚠️ 结果文件格式异常：期望列表，得到 {type(results).__name__}")
                return set()
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

    def load_and_filter(self, mode: str = "full", cases_ids: Optional[str] = None,
                        batch_id: Optional[str] = None) -> Tuple[List[Dict], str]:
        """组合方法：加载 + 过滤 + 增量判断，一次完成

        Args:
            mode: 执行模式
            cases_ids: selected模式下的用例ID
            batch_id: 用于增量执行的批次ID

        Returns:
            (过滤后的测试用例列表, 用例版本)
        """
        test_cases, version = self.load_test_cases()

        executed_ids = None
        if mode == 'incremental' and batch_id:
            results_dir = str(get_results_dir())
            batch_dir = os.path.join(results_dir, batch_id)
            executed_ids = self.load_executed_cases(batch_dir)

        filtered = self.filter_test_cases(test_cases, mode, cases_ids, executed_ids)
        return filtered, version
