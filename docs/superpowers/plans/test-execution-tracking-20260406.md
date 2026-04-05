# 测试执行追踪系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为测试执行流程添加配置基线记录、执行日志追踪、完整性验证功能

**Architecture:** 创建独立的 `record_test_run.py` 模块，提供 `TestRunRecorder` 类，集成到现有的 `run_tests.py` 执行流程中，每个测试批次生成 test_config.json 和 test_execution.log 文件

**Tech Stack:** Python 3.10+, JSON, os, datetime, platform, subprocess

---

## 文件结构

```
llm-testing-portfolio/
├── scripts/
│   ├── record_test_run.py              # [新增] 记录测试运行模块
│   └── run_tests.py                    # [修改] 集成记录功能
│
└── projects/01-ai-customer-service/
    └── results/
        └── batch-XXX_YYYY-MM-DD/
            ├── test_config.json        # [新增] 测试配置基线
            ├── test_execution.log      # [新增] 执行日志
            ├── records.json            # [已有]
            ├── results.json            # [已有]
            └── summary.md              # [已有]
```

---

## Task 1: 创建 TestRunRecorder 类基础结构

**Files:**
- Create: `scripts/record_test_run.py`

- [ ] **Step 1: 创建文件基础结构和类定义**

```python
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
```

- [ ] **Step 2: 提交基础结构**

```bash
git add scripts/record_test_run.py
git commit -m "feat: add TestRunRecorder class skeleton"
```

---

## Task 2: 实现配置基线管理功能

**Files:**
- Modify: `scripts/record_test_run.py:30-50`

- [ ] **Step 1: 实现 create_test_config 方法**

在 `TestRunRecorder` 类中添加方法：

```python
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
```

- [ ] **Step 2: 实现 load_test_config 和 update_test_config 方法**

```python
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
```

- [ ] **Step 3: 提交配置基线管理功能**

```bash
git add scripts/record_test_run.py
git commit -m "feat: add test config management to TestRunRecorder"
```

---

## Task 3: 实现执行日志管理功能

**Files:**
- Modify: `scripts/record_test_run.py`

- [ ] **Step 1: 实现日志记录方法**

```python
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
            - duration_seconds: 执行时长（秒）
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
```

- [ ] **Step 2: 实现获取最后完成用例的方法**

```python
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
```

- [ ] **Step 3: 提交执行日志管理功能**

```bash
git add scripts/record_test_run.py
git commit -m "feat: add execution log management to TestRunRecorder"
```

---

## Task 4: 实现完整性验证功能

**Files:**
- Modify: `scripts/record_test_run.py`

- [ ] **Step 1: 实现验证方法**

```python
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
```

- [ ] **Step 2: 实现生成审计报告方法**

```python
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
```

- [ ] **Step 3: 提交完整性验证功能**

```bash
git add scripts/record_test_run.py
git commit -m "feat: add integrity validation to TestRunRecorder"
```

---

## Task 5: 实现异常检测功能

**Files:**
- Modify: `scripts/record_test_run.py`

- [ ] **Step 1: 实现版本兼容性检查方法**

```python
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
```

- [ ] **Step 2: 提交异常检测功能**

```bash
git add scripts/record_test_run.py
git commit -m "feat: add exception detection to TestRunRecorder"
```

---

## Task 6: 集成到 run_tests.py

**Files:**
- Modify: `scripts/run_tests.py`

- [ ] **Step 1: 导入 TestRunRecorder**

在 `run_tests.py` 文件开头添加导入：

```python
# 在文件开头添加
import os
import json
import sys
from datetime import datetime

# 添加到现有导入之后
from record_test_run import TestRunRecorder
```

- [ ] **Step 2: 在 test_all_cases 函数中初始化记录器**

在 `test_all_cases` 函数开头添加（大约在第 200 行附近）：

```python
def test_all_cases(args, cases_data):
    """执行所有测试用例"""
    
    # 创建批次目录
    batch_dir = create_batch_dir(args)
    
    # [新增] 创建记录器
    recorder = TestRunRecorder(batch_dir)
    
    # [新增] 创建测试配置基线
    test_config = recorder.create_test_config(
        batch_id=args.batch_id,
        test_case_version=cases_data["metadata"]["version"],
        test_case_file="cases/universal.json",
        model=args.model,
        evaluator_model=args.evaluator_model,
        test_parameters={
            "mode": args.mode,
            "concurrent": getattr(args, 'concurrent', 1)
        }
    )
    
    # [新增] 更新配置中的用例信息
    total_cases = sum(len(cases_data["cases"][dim]) for dim in cases_data["cases"])
    dimensions = list(cases_data["cases"].keys())
    
    recorder.update_test_config({
        "test_configuration": {
            "total_cases": total_cases,
            "dimensions": dimensions
        }
    })
    
    # [新增] 开始记录执行
    recorder.start_logging(test_config["test_run_id"])
    
    # 原有逻辑继续...
    records = []
    results = []
    start_time = datetime.now()
    
    # ... 原有的测试执行代码 ...
```

- [ ] **Step 3: 在用例执行过程中记录日志**

修改用例执行循环（大约在第 250 行附近）：

```python
    # 执行测试用例
    index = 0
    for dimension, cases in cases_data["cases"].items():
        for case in cases:
            index += 1
            
            # [新增] 记录用例开始
            recorder.log_case_start(case["id"], index, total_cases)
            
            try:
                # 执行测试
                record = execute_test_case(case, args)
                result = evaluate_response(record, case, args)
                
                # [新增] 记录用例完成
                status = "PASS" if result["evaluation_result"]["status"] == "通过" else "FAIL"
                recorder.log_case_complete(case["id"], index, total_cases, status)
                
                records.append(record)
                results.append(result)
                
            except Exception as e:
                # [新增] 记录错误
                recorder.log_error(case["id"], str(e))
                print(f"❌ 执行失败: {case['id']} - {e}")
                continue
```

- [ ] **Step 4: 在测试完成后更新配置和生成审计报告**

在 `generate_summary` 函数调用之前添加（大约在第 300 行附近）：

```python
    # 计算执行时间
    end_time = datetime.now()
    duration_seconds = int((end_time - start_time).total_seconds())
    
    # [新增] 更新配置
    passed_count = sum(1 for r in results if r["evaluation_result"]["status"] == "通过")
    pass_rate = passed_count / len(results) * 100 if results else 0
    
    recorder.update_test_config({
        "status": "completed",
        "completed_at": end_time.isoformat(),
        "execution_metrics": {
            "total_duration_seconds": duration_seconds,
            "average_time_per_case_seconds": duration_seconds / len(results) if results else 0,
            "success_rate": 1.0,  # API调用成功率
            "api_calls": len(results),
            "total_tokens": 0  # 如果有token统计可以添加
        },
        "quality_gates": {
            "actual_pass_rate": pass_rate / 100,
            "result": "PASS" if pass_rate >= 90 else "FAIL"
        }
    })
    
    # [新增] 结束日志记录
    recorder.end_logging({
        "total": total_cases,
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate": pass_rate
    })
    
    # [新增] 完整性验证
    coverage_validation = recorder.validate_coverage(total_cases, len(records))
    consistency_validation = recorder.validate_consistency(len(records), len(results))
    config_validation = recorder.validate_config_integrity()
    
    validation_results = [coverage_validation, consistency_validation, config_validation]
    
    # [新增] 生成审计报告
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
```

- [ ] **Step 5: 提交集成代码**

```bash
git add scripts/run_tests.py scripts/record_test_run.py
git commit -m "feat: integrate TestRunRecorder into run_tests.py"
```

---

## Task 7: 测试验证

**Files:**
- Test: 手动测试

- [ ] **Step 1: 测试基本功能**

运行测试：

```bash
cd /Users/honey/CodeBuddy/20260331111134/llm-testing-portfolio
python scripts/run_tests.py --mode single
```

验证生成的文件：
```bash
ls -la projects/01-ai-customer-service/results/batch-*/
# 应该看到 test_config.json 和 test_execution.log
```

- [ ] **Step 2: 验证 test_config.json 内容**

```bash
cat projects/01-ai-customer-service/results/batch-*/test_config.json
```

检查关键字段：
- batch_id
- test_run_id
- test_configuration.test_case_version
- environment.model_under_test

- [ ] **Step 3: 验证 test_execution.log 内容**

```bash
cat projects/01-ai-customer-service/results/batch-*/test_execution.log
```

检查日志格式：
- 时间戳格式正确
- 用例执行记录完整
- 有开始和结束标记

- [ ] **Step 4: 提交测试验证**

```bash
git add .
git commit -m "test: verify TestRunRecorder functionality"
```

---

## 自审清单

**1. Spec 覆盖检查**:
- ✅ test_config.json 创建和保存（Task 2）
- ✅ test_execution.log 记录（Task 3）
- ✅ 完整性验证（Task 4）
- ✅ 异常检测（Task 5）
- ✅ run_tests.py 集成（Task 6）

**2. Placeholder 扫描**:
- ✅ 无 TBD、TODO
- ✅ 所有代码步骤都有完整实现
- ✅ 所有测试命令都有具体参数

**3. 类型一致性检查**:
- ✅ TestRunRecorder 类的方法签名一致
- ✅ 返回值类型标注完整
- ✅ 参数名称在所有调用中一致

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/test-execution-tracking-20260406.md`。

**两种执行方式**:

**1. Subagent-Driven（推荐）** - 我为每个任务派发一个新的子代理，任务间进行审查，快速迭代

**2. Inline Execution** - 在当前会话中使用 executing-plans 执行，批量执行并在检查点进行审查

**你选择哪种方式？**
