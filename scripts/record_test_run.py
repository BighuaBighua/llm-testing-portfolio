"""
记录测试运行模块

职责：
1. 记录测试配置基线（test_config.json）
2. 记录测试执行日志（test_execution.log）
3. 验证测试执行完整性
4. 检测异常情况（中断、版本变更等）
5. 生成审计报告

作者: BighuaBighua
日期: 2026-04-06
版本: 1.0
"""

import os
import json
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any


class TestRunRecorder:
    """
    记录测试运行
    
    核心功能：
    - 配置基线管理：create_test_config, load_test_config, update_test_config
    - 执行日志管理：start_logging, log_case_start, log_case_complete, log_error, end_logging
    - 完整性验证：validate_coverage, validate_consistency, generate_audit_report
    - 异常检测：check_version_compatibility, detect_interruption
    """
    
    def __init__(self, batch_dir: str):
        """
        初始化记录器
        
        Args:
            batch_dir: 批次目录路径
        """
        self.batch_dir = batch_dir
        self.config_file = os.path.join(batch_dir, "test_config.json")
        self.log_file = os.path.join(batch_dir, "test_execution.log")
        self.config: Optional[Dict[str, Any]] = None
        
        # 确保目录存在
        os.makedirs(batch_dir, exist_ok=True)
    
    # ==================== 配置基线管理 ====================
    
    def create_test_config(
        self,
        batch_id: str,
        test_case_version: str,
        test_case_file: str,
        model: str,
        evaluator_model: str,
        test_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建测试配置基线
        
        Args:
            batch_id: 批次ID
            test_case_version: 测试用例版本
            test_case_file: 测试用例文件路径
            model: 被测模型
            evaluator_model: 评测模型
            test_parameters: 测试参数字典
        
        Returns:
            dict: 测试配置基线
        """
        # 获取 Git commit hash
        test_case_hash = self._get_git_hash(test_case_file)
        
        # 生成测试运行ID
        test_run_id = f"TR-{datetime.now().strftime('%Y-%m-%d')}-{batch_id.split('-')[1]}"
        
        # 构建配置基线
        config = {
            "batch_id": batch_id,
            "test_run_id": test_run_id,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "status": "running",
            
            "test_configuration": {
                "test_case_version": test_case_version,
                "test_case_file": test_case_file,
                "test_case_hash": test_case_hash,
                "total_cases": 0,  # 后续更新
                "dimensions": []   # 后续更新
            },
            
            "environment": {
                "model_under_test": model,
                "evaluator_model": evaluator_model,
                "api_endpoint": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
                "python_version": platform.python_version(),
                "os": platform.platform()
            },
            
            "test_parameters": {
                "mode": test_parameters.get("mode", "full"),
                "concurrent": test_parameters.get("concurrent", 1),
                "timeout": test_parameters.get("timeout", 30),
                "retry_attempts": test_parameters.get("retry_attempts", 3)
            },
            
            "execution_metrics": {
                "total_duration_seconds": 0,
                "average_time_per_case_seconds": 0.0,
                "success_rate": 0.0,
                "api_calls": 0,
                "total_tokens": 0
            },
            
            "quality_gates": {
                "pass_rate_threshold": 0.9,
                "actual_pass_rate": 0.0,
                "result": "PENDING"
            }
        }
        
        # 保存配置
        self.config = config
        self._save_config()
        
        return config
    
    def load_test_config(self) -> Dict[str, Any]:
        """
        加载测试配置基线
        
        Returns:
            dict: 测试配置基线
        
        Raises:
            FileNotFoundError: 配置文件不存在
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        return self.config
    
    def update_test_config(self, updates: Dict[str, Any]):
        """
        更新测试配置基线
        
        Args:
            updates: 更新内容字典
        
        Example:
            recorder.update_test_config({
                "status": "completed",
                "completed_at": "2026-04-05T21:56:32",
                "execution_metrics": {
                    "total_duration_seconds": 14192,
                    "success_rate": 1.0
                }
            })
        """
        if self.config is None:
            self.config = self.load_test_config()
        
        # 深度合并更新
        def deep_update(base: dict, updates: dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self.config, updates)
        self._save_config()
    
    def _get_git_hash(self, file_path: str) -> str:
        """
        获取文件的 Git commit hash
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: Git commit hash（前8位）
        """
        try:
            # 获取文件相对于仓库根目录的路径
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def _save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    # ==================== 执行日志管理 ====================
    
    def start_logging(self, test_run_id: str):
        """
        开始记录执行日志
        
        Args:
            test_run_id: 测试运行ID
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"[{timestamp}] INFO  Test run started: {test_run_id}\n")
            
            if self.config:
                test_case_version = self.config["test_configuration"]["test_case_version"]
                test_case_file = self.config["test_configuration"]["test_case_file"]
                f.write(f"[{timestamp}] INFO  Loading test cases from: {test_case_file} (v{test_case_version})\n")
                
                total_cases = self.config["test_configuration"]["total_cases"]
                dimensions = self.config["test_configuration"]["dimensions"]
                f.write(f"[{timestamp}] INFO  Test configuration loaded: {total_cases} cases, {len(dimensions)} dimensions\n")
                f.write(f"[{timestamp}] INFO  Starting test execution...\n")
    
    def log_case_start(self, case_id: str, index: int, total: int):
        """
        记录用例开始执行
        
        Args:
            case_id: 用例ID
            index: 当前索引（从1开始）
            total: 总数
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] INFO  [{index}/{total}] {case_id} started\n")
    
    def log_case_complete(self, case_id: str, index: int, total: int, status: str):
        """
        记录用例执行完成
        
        Args:
            case_id: 用例ID
            index: 当前索引（从1开始）
            total: 总数
            status: 执行状态（PASS/FAIL）
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] INFO  [{index}/{total}] {case_id} completed - {status}\n")
    
    def log_error(self, case_id: str, error_message: str):
        """
        记录错误信息
        
        Args:
            case_id: 用例ID
            error_message: 错误信息
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] ERROR [{case_id}] {error_message}\n")
    
    def end_logging(self, summary: Dict[str, Any]):
        """
        结束记录执行日志
        
        Args:
            summary: 执行摘要字典，包含：
                - total: 总用例数
                - passed: 通过数
                - failed: 失败数
                - pass_rate: 通过率
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] INFO  Test run completed: {summary['total']}/{summary['total']} cases executed\n")
            f.write(f"[{timestamp}] INFO  Pass rate: {summary['pass_rate']:.1f}% ({summary['passed']}/{summary['total']})\n")
            
            # 质量门检查
            threshold = self.config["quality_gates"]["pass_rate_threshold"] if self.config else 0.9
            if summary['pass_rate'] / 100 >= threshold:
                f.write(f"[{timestamp}] INFO  Quality gate: PASS ({summary['pass_rate']:.1f}% >= {threshold*100:.1f}%)\n")
            else:
                f.write(f"[{timestamp}] WARN  Quality gate: FAIL ({summary['pass_rate']:.1f}% < {threshold*100:.1f}%)\n")
    
    def get_last_completed_case(self) -> Optional[str]:
        """
        获取最后完成的用例ID（用于断点续传）
        
        Returns:
            str: 用例ID，如果没有完成的用例则返回 None
        """
        if not os.path.exists(self.log_file):
            return None
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # 从后往前查找最后一个 completed 记录
            for line in reversed(lines):
                if "completed" in line:
                    # 提取用例ID，格式: [timestamp] INFO  [index/total] case_id completed - status
                    try:
                        # 找到用例ID的位置
                        parts = line.split("] ")
                        if len(parts) >= 3:
                            case_info = parts[2]  # [index/total] case_id completed - status
                            case_id = case_info.split()[1]  # 提取 case_id
                            return case_id
                    except Exception:
                        continue
        
        return None
    
    # ==================== 完整性验证 ====================
    
    def validate_coverage(self, expected_total: int, actual_completed: int) -> Dict[str, Any]:
        """
        验证用例覆盖率
        
        Args:
            expected_total: 预期总数
            actual_completed: 实际完成数
        
        Returns:
            dict: 验证结果
        """
        coverage = actual_completed / expected_total if expected_total > 0 else 0
        
        return {
            "name": "用例覆盖率",
            "expected": "100%",
            "actual": f"{coverage*100:.1f}%",
            "passed": coverage == 1.0
        }
    
    def validate_consistency(self, records_count: int, results_count: int) -> Dict[str, Any]:
        """
        验证结果一致性
        
        Args:
            records_count: records.json中的记录数
            results_count: results.json中的记录数
        
        Returns:
            dict: 验证结果
        """
        return {
            "name": "结果一致性",
            "expected": records_count,
            "actual": results_count,
            "passed": records_count == results_count
        }
    
    def validate_config_integrity(self) -> Dict[str, Any]:
        """
        验证配置基线完整性
        
        Returns:
            dict: 验证结果
        """
        if self.config is None:
            self.config = self.load_test_config()
        
        required_fields = [
            "test_configuration.test_case_version",
            "test_configuration.test_case_file",
            "environment.model_under_test",
            "environment.evaluator_model"
        ]
        
        missing_fields = []
        for field in required_fields:
            parts = field.split(".")
            value = self.config
            try:
                for part in parts:
                    value = value[part]
            except (KeyError, TypeError):
                missing_fields.append(field)
        
        return {
            "name": "配置基线完整性",
            "expected": "无缺失字段",
            "actual": f"缺失 {len(missing_fields)} 个字段" if missing_fields else "无缺失字段",
            "passed": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }
    
    def generate_audit_report(self, validation_results: List[Dict[str, Any]]) -> str:
        """
        生成审计报告
        
        Args:
            validation_results: 验证结果列表
        
        Returns:
            str: 审计报告（Markdown格式）
        """
        if self.config is None:
            self.config = self.load_test_config()
        
        report = f"""# 测试执行审计报告

## 批次信息
- 批次ID: {self.config['batch_id']}
- 测试运行ID: {self.config['test_run_id']}
- 执行时间: {self.config['created_at']} ~ {self.config.get('completed_at', 'N/A')}

## 完整性检查
| 检查项 | 期望值 | 实际值 | 状态 |
|--------|--------|--------|------|
"""
        
        for result in validation_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            report += f"| {result['name']} | {result['expected']} | {result['actual']} | {status} |\n"
        
        report += f"""
## 配置基线
- 用例版本: {self.config['test_configuration']['test_case_version']}
- 被测模型: {self.config['environment']['model_under_test']}
- 评测模型: {self.config['environment']['evaluator_model']}

## 结论
{'✅ 测试执行完整，符合审计要求' if all(r['passed'] for r in validation_results) else '❌ 测试执行不完整，需要处理'}
"""
        
        return report
    
    def save_audit_report(self, report: str):
        """
        保存审计报告
        
        Args:
            report: 审计报告内容
        """
        report_file = os.path.join(self.batch_dir, "audit_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    # ==================== 异常检测 ====================
    
    def check_version_compatibility(self, current_case_version: str) -> Dict[str, Any]:
        """
        检查版本兼容性
        
        Args:
            current_case_version: 当前用例版本
        
        Returns:
            dict: 兼容性检查结果
        """
        if self.config is None:
            self.config = self.load_test_config()
        
        batch_version = self.config["test_configuration"]["test_case_version"]
        
        return {
            "compatible": batch_version == current_case_version,
            "batch_version": batch_version,
            "current_version": current_case_version
        }
    
    def detect_interruption(self) -> Dict[str, Any]:
        """
        检测中断情况
        
        Returns:
            dict: 中断检测结果
        """
        if self.config is None:
            self.config = self.load_test_config()
        
        # 检查状态
        if self.config["status"] == "completed":
            return {
                "detected": False,
                "reason": "Batch already completed"
            }
        
        # 获取最后完成的用例
        last_completed = self.get_last_completed_case()
        total = self.config["test_configuration"]["total_cases"]
        
        if last_completed is None:
            return {
                "detected": True,
                "completed": 0,
                "total": total,
                "last_completed": None,
                "last_timestamp": None
            }
        
        # 从日志中获取最后时间戳
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_line = lines[-1] if lines else ""
            # 提取时间戳: [2026-04-05 18:00:00] ...
            last_timestamp = last_line[1:20] if len(last_line) > 20 else None
        
        # 计算已完成数量
        completed_count = 0
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "completed" in line:
                    completed_count += 1
        
        return {
            "detected": completed_count < total,
            "completed": completed_count,
            "total": total,
            "last_completed": last_completed,
            "last_timestamp": last_timestamp
        }
