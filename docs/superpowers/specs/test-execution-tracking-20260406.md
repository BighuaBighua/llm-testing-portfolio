# 测试执行追踪系统设计文档

> 基于 IEEE 829 测试文档标准和 ISO/IEC 29119 软件测试标准

---

## 文档信息

- **设计日期**: 2026-04-06
- **设计者**: CodeBuddy
- **审核状态**: 待审核
- **实施优先级**: 高

---

## 一、背景与目标

### 1.1 问题现状

当前 LLM 测试项目的 results 目录管理存在以下问题：

1. **版本追溯困难**: 无法快速定位每个批次使用的测试用例版本
2. **可审计性不足**: 缺少完整的测试环境、配置、执行过程记录
3. **异常处理不完善**: 中断、版本变更等场景缺乏明确的处理策略
4. **完整性保障缺失**: 无法自动验证测试执行是否完整

### 1.2 设计目标

参考专业软件测试标准（IEEE 829、ISO/IEC 29119），实现：

1. **版本追溯能力**: 能追溯到每个批次用的是哪个版本的用例
2. **测试结果可审计性**: 能清楚看到每次测试的环境、配置、结果
3. **异常处理合理性**: 中断、版本变更等场景的处理策略明确
4. **测试执行完整性**: 确保所有用例都被执行，且结果可复现

---

## 二、总体架构

### 2.1 核心设计理念

**"测试配置基线 + 执行过程追踪 + 完整性验证"**

借鉴 IEEE 829 测试文档标准，为每个测试批次建立完整的审计记录，确保：
- **可追溯**: 每个批次都能追溯到用例版本、环境配置、测试参数
- **可审计**: 完整记录测试过程、环境、结果，满足合规审计要求
- **可重现**: 基于相同配置基线，可以重现测试结果

### 2.2 架构设计

```
测试执行审计系统
│
├── TestRunRecorder (record_test_run.py)
│   ├── 配置基线管理
│   │   ├── create_test_config()      # 创建配置基线
│   │   ├── load_test_config()        # 加载配置
│   │   └── update_test_config()      # 更新配置
│   │
│   ├── 执行日志管理
│   │   ├── start_logging()           # 开始记录
│   │   ├── log_case_start()          # 记录用例开始
│   │   ├── log_case_complete()       # 记录用例完成
│   │   ├── log_error()               # 记录错误
│   │   └── end_logging()             # 结束记录
│   │
│   ├── 完整性验证
│   │   ├── validate_coverage()       # 验证覆盖率
│   │   ├── validate_consistency()    # 验证一致性
│   │   └── generate_audit_report()   # 生成审计报告
│   │
│   └── 异常检测
│       ├── check_version_compatibility()  # 版本兼容性检查
│       ├── check_environment_consistency() # 环境一致性检查
│       └── detect_interruption()          # 中断检测
│
└── run_tests.py 集成
    ├── 初始化记录器
    ├── 记录配置基线
    ├── 记录执行过程
    ├── 验证完整性
    └── 生成审计报告
```

---

## 三、详细设计

### 3.1 文件结构

```
llm-testing-portfolio/
├── scripts/
│   ├── run_tests.py                    # [修改] 集成审计功能
│   └── record_test_run.py              # [新增] 记录测试运行模块
│
└── projects/01-ai-customer-service/
    └── results/
        └── batch-XXX_YYYY-MM-DD/
            ├── test_config.json        # [新增] 测试配置基线
            ├── test_execution.log      # [新增] 执行日志
            ├── records.json            # [保留] 测试记录
            ├── results.json            # [保留] 评测结果
            └── summary.md              # [保留] 测试报告
```

### 3.2 test_config.json 设计

**生成时机**: 每次创建新批次时自动生成

**数据结构**:

```json
{
  "batch_id": "batch-001",
  "test_run_id": "TR-2026-04-05-001",
  "created_at": "2026-04-05T18:00:00",
  "completed_at": "2026-04-05T21:56:32",
  "status": "completed",
  
  "test_configuration": {
    "test_case_version": "1.1",
    "test_case_file": "cases/universal.json",
    "test_case_hash": "a1b2c3d4",
    "total_cases": 80,
    "dimensions": ["accuracy", "completeness", "compliance", "attitude", "multi", "boundary", "conflict", "induction"]
  },
  
  "environment": {
    "model_under_test": "ernie-4.5-turbo-128k",
    "evaluator_model": "ernie-4.5-turbo-128k",
    "api_endpoint": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
    "python_version": "3.10.0",
    "os": "macOS 13.0"
  },
  
  "test_parameters": {
    "mode": "full",
    "concurrent": 1,
    "timeout": 30,
    "retry_attempts": 3
  },
  
  "execution_metrics": {
    "total_duration_seconds": 14192,
    "average_time_per_case_seconds": 177.4,
    "success_rate": 1.0,
    "api_calls": 80,
    "total_tokens": 125000
  },
  
  "quality_gates": {
    "pass_rate_threshold": 0.9,
    "actual_pass_rate": 1.0,
    "result": "PASS"
  }
}
```

**字段说明**:

| 字段路径 | 类型 | 说明 | 必填 |
|---------|------|------|------|
| batch_id | string | 批次ID | 是 |
| test_run_id | string | 测试运行ID（符合IEEE 829标准） | 是 |
| created_at | datetime | 创建时间 | 是 |
| completed_at | datetime | 完成时间 | 否 |
| status | string | 批次状态（running/completed/failed） | 是 |
| test_configuration.test_case_version | string | 测试用例版本 | 是 |
| test_configuration.test_case_file | string | 测试用例文件路径 | 是 |
| test_configuration.test_case_hash | string | 测试用例Git commit hash | 是 |
| test_configuration.total_cases | integer | 用例总数 | 是 |
| test_configuration.dimensions | array | 测试维度列表 | 是 |
| environment.model_under_test | string | 被测模型 | 是 |
| environment.evaluator_model | string | 评测模型 | 是 |
| environment.api_endpoint | string | API端点 | 是 |
| environment.python_version | string | Python版本 | 是 |
| environment.os | string | 操作系统 | 是 |
| test_parameters.mode | string | 执行模式 | 是 |
| test_parameters.concurrent | integer | 并发数 | 是 |
| execution_metrics.total_duration_seconds | integer | 总执行时长（秒） | 否 |
| execution_metrics.average_time_per_case_seconds | float | 平均每条用例执行时长 | 否 |
| quality_gates.pass_rate_threshold | float | 通过率阈值 | 是 |
| quality_gates.actual_pass_rate | float | 实际通过率 | 否 |
| quality_gates.result | string | 质量门结果（PASS/FAIL） | 否 |

### 3.3 test_execution.log 设计

**生成时机**: 测试执行过程中实时追加

**格式**: 时间戳 + 日志级别 + 消息内容

**示例**:

```
[2026-04-05 18:00:00] INFO  Test run started: TR-2026-04-05-001
[2026-04-05 18:00:00] INFO  Loading test cases from: cases/universal.json (v1.1)
[2026-04-05 18:00:00] INFO  Test configuration loaded: 80 cases, 8 dimensions
[2026-04-05 18:00:01] INFO  Starting test execution...
[2026-04-05 18:00:01] INFO  [1/80] TC-ACC-001 started
[2026-04-05 18:00:18] INFO  [1/80] TC-ACC-001 completed - PASS
[2026-04-05 18:00:18] INFO  [2/80] TC-ACC-002 started
[2026-04-05 18:00:35] INFO  [2/80] TC-ACC-002 completed - PASS
...
[2026-04-05 21:56:32] INFO  [80/80] TC-IND-010 completed - PASS
[2026-04-05 21:56:32] INFO  Test run completed: 80/80 cases executed
[2026-04-05 21:56:32] INFO  Pass rate: 100.0% (80/80)
[2026-04-05 21:56:32] INFO  Quality gate: PASS (100.0% >= 90%)
```

**日志级别**:

| 级别 | 说明 | 示例 |
|------|------|------|
| INFO | 一般信息 | 用例开始、完成、批次状态 |
| WARN | 警告信息 | 重试、超时、配置变更 |
| ERROR | 错误信息 | API调用失败、解析错误 |

### 3.4 record_test_run.py 模块设计

**模块职责**:
1. 记录测试配置基线（test_config.json）
2. 记录测试执行日志（test_execution.log）
3. 验证测试执行完整性
4. 检测异常情况（中断、版本变更等）
5. 生成审计报告

**核心类设计**:

```python
class TestRunRecorder:
    """记录测试运行"""
    
    def __init__(self, batch_dir):
        """
        初始化记录器
        
        Args:
            batch_dir: 批次目录路径
        """
        self.batch_dir = batch_dir
        self.config_file = os.path.join(batch_dir, "test_config.json")
        self.log_file = os.path.join(batch_dir, "test_execution.log")
        self.config = None
    
    # ========== 配置基线管理 ==========
    
    def create_test_config(self, batch_id, test_case_version, test_case_hash,
                          model, evaluator_model, environment_info, test_parameters):
        """
        创建测试配置基线
        
        Args:
            batch_id: 批次ID
            test_case_version: 测试用例版本
            test_case_hash: 测试用例Git commit hash
            model: 被测模型
            evaluator_model: 评测模型
            environment_info: 环境信息字典
            test_parameters: 测试参数字典
        
        Returns:
            dict: 测试配置基线
        """
        pass
    
    def load_test_config(self):
        """
        加载测试配置基线
        
        Returns:
            dict: 测试配置基线
        """
        pass
    
    def update_test_config(self, updates):
        """
        更新测试配置基线
        
        Args:
            updates: 更新内容字典
        """
        pass
    
    # ========== 执行日志管理 ==========
    
    def start_logging(self, test_run_id):
        """
        开始记录执行日志
        
        Args:
            test_run_id: 测试运行ID
        """
        pass
    
    def log_case_start(self, case_id, index, total):
        """
        记录用例开始执行
        
        Args:
            case_id: 用例ID
            index: 当前索引
            total: 总数
        """
        pass
    
    def log_case_complete(self, case_id, index, total, status):
        """
        记录用例执行完成
        
        Args:
            case_id: 用例ID
            index: 当前索引
            total: 总数
            status: 执行状态（PASS/FAIL）
        """
        pass
    
    def log_error(self, case_id, error_message):
        """
        记录错误信息
        
        Args:
            case_id: 用例ID
            error_message: 错误信息
        """
        pass
    
    def end_logging(self, summary):
        """
        结束记录执行日志
        
        Args:
            summary: 执行摘要字典
        """
        pass
    
    # ========== 完整性验证 ==========
    
    def validate_coverage(self, expected_total, actual_completed):
        """
        验证用例覆盖率
        
        Args:
            expected_total: 预期总数
            actual_completed: 实际完成数
        
        Returns:
            dict: 验证结果
        """
        pass
    
    def validate_consistency(self, records_count, results_count):
        """
        验证结果一致性
        
        Args:
            records_count: records.json中的记录数
            results_count: results.json中的记录数
        
        Returns:
            dict: 验证结果
        """
        pass
    
    def generate_audit_report(self, validation_results):
        """
        生成审计报告
        
        Args:
            validation_results: 验证结果列表
        
        Returns:
            str: 审计报告（Markdown格式）
        """
        pass
    
    # ========== 异常检测 ==========
    
    def check_version_compatibility(self, current_case_version):
        """
        检查版本兼容性
        
        Args:
            current_case_version: 当前用例版本
        
        Returns:
            dict: 兼容性检查结果
        """
        pass
    
    def check_environment_consistency(self, current_environment):
        """
        检查环境一致性
        
        Args:
            current_environment: 当前环境信息
        
        Returns:
            dict: 一致性检查结果
        """
        pass
    
    def detect_interruption(self):
        """
        检测中断情况
        
        Returns:
            dict: 中断检测结果
        """
        pass
```

### 3.5 run_tests.py 集成设计

**改动点**:

#### 改动点 1: 导入模块

```python
# 在文件开头添加
from record_test_run import TestRunRecorder
```

#### 改动点 2: 初始化记录器

```python
# 在 test_all_cases() 函数开头
def test_all_cases(args, cases_data):
    # 创建批次目录
    batch_dir = create_batch_dir(args)
    
    # [新增] 创建记录器
    recorder = TestRunRecorder(batch_dir)
    
    # [新增] 创建测试配置基线
    test_config = recorder.create_test_config(
        batch_id=args.batch_id,
        test_case_version=cases_data["metadata"]["version"],
        test_case_hash=get_git_hash("cases/universal.json"),
        model=args.model,
        evaluator_model=args.evaluator_model,
        environment_info=get_environment_info(),
        test_parameters={
            "mode": args.mode,
            "concurrent": args.concurrent
        }
    )
    
    # [新增] 开始记录执行
    recorder.start_logging(test_config["test_run_id"])
    
    # 原有逻辑...
```

#### 改动点 3: 记录执行过程

```python
# 在 execute_test_case() 函数中
def execute_test_case(case, args, recorder, index, total):
    # [新增] 记录用例开始
    recorder.log_case_start(case["id"], index, total)
    
    try:
        # 原有执行逻辑
        response = call_api(case, args)
        result = evaluate_response(response, case, args)
        
        # [新增] 记录用例完成
        status = "PASS" if result["evaluation_result"]["status"] == "通过" else "FAIL"
        recorder.log_case_complete(case["id"], index, total, status)
        
        return result
    except Exception as e:
        # [新增] 记录错误
        recorder.log_error(case["id"], str(e))
        raise
```

#### 改动点 4: 完整性验证

```python
# 在 generate_summary() 函数之前
def validate_execution_integrity(batch_dir, recorder, expected_total, records, results):
    # [新增] 验证覆盖率
    coverage_validation = recorder.validate_coverage(expected_total, len(records))
    
    # [新增] 验证一致性
    consistency_validation = recorder.validate_consistency(len(records), len(results))
    
    # [新增] 生成审计报告
    validation_results = [coverage_validation, consistency_validation]
    audit_report = recorder.generate_audit_report(validation_results)
    
    # 保存审计报告
    save_audit_report(batch_dir, audit_report)
    
    # 返回验证结果
    return all(v["passed"] for v in validation_results)
```

#### 改动点 5: 中断恢复处理

```python
# 在 main() 函数中
def handle_existing_batch(args, recorder):
    """
    处理已存在的批次
    
    Returns:
        str: 处理动作（CONTINUE/RESTART/NEW_BATCH/ABORT）
    """
    # 加载配置
    config = recorder.load_test_config()
    
    # 检查版本兼容性
    current_case_version = get_current_case_version()
    version_check = recorder.check_version_compatibility(current_case_version)
    
    if not version_check["compatible"]:
        print(f"❌ 版本冲突检测:")
        print(f"  - 批次用例版本: {version_check['batch_version']}")
        print(f"  - 当前用例版本: {version_check['current_version']}")
        print("根据软件测试最佳实践（IEEE 829），版本变更必须创建新批次")
        return "NEW_BATCH"
    
    # 检测中断
    interruption = recorder.detect_interruption()
    
    if interruption["detected"]:
        print(f"⚠️ 批次状态分析:")
        print(f"  - 已完成: {interruption['completed']}/{interruption['total']}")
        print(f"  - 用例版本: {config['test_configuration']['test_case_version']}")
        print(f"  - 中断时间: {interruption['last_timestamp']}")
        print()
        print("选择操作:")
        print("[A] 从断点继续执行（符合IEEE 829标准）")
        print("[B] 重新执行所有用例（更安全，但会覆盖已有结果）")
        print("[C] 创建新批次重新测试")
        
        choice = input("请选择 [A/B/C]: ").upper()
        
        if choice == "A":
            return "CONTINUE"
        elif choice == "B":
            return "RESTART"
        else:
            return "NEW_BATCH"
    
    # 批次已完成
    if config["status"] == "completed":
        print(f"batch-{args.batch_id} 已完成，是否创建新批次？[Y/n]")
        choice = input().upper()
        if choice != "N":
            return "NEW_BATCH"
        else:
            return "ABORT"
    
    return "CONTINUE"
```

---

## 四、异常场景处理

### 4.1 场景分类

| 场景 | 检测条件 | 处理策略 | 用户确认 |
|------|---------|---------|---------|
| 全新测试 | 批次不存在 | 创建新批次，执行所有用例 | 无需确认 |
| 中断后继续 | 批次存在 + status=running | 提示选择：继续/重新执行/新批次 | 需要（默认选A） |
| 重新评测 | status=completed + --report-only | 重新评分 | 无需确认 |
| 版本变更 | test_case_version 不匹配 | 强制创建新批次 | 无需确认（自动退出） |
| 回归测试 | status=completed + 无参数 | 创建新批次 | 提示确认 |

### 4.2 版本变更处理流程

```python
# 版本变更检测流程
def check_version_change_on_continue(batch_id, current_case_version):
    recorder = TestRunRecorder(get_batch_dir(batch_id))
    config = recorder.load_test_config()
    
    batch_version = config["test_configuration"]["test_case_version"]
    
    if batch_version != current_case_version:
        print(f"❌ 错误：用例版本已变更（{batch_version} → {current_case_version}）")
        print(f"batch-{batch_id} 是基于 {batch_version} 的测试，不能继续")
        print("必须创建新批次重新测试")
        print(f"建议：python scripts/run_tests.py --batch-id batch-{get_next_batch_id()}")
        exit(1)
```

### 4.3 中断恢复处理流程

```python
# 中断恢复流程
def handle_interruption(batch_id):
    recorder = TestRunRecorder(get_batch_dir(batch_id))
    
    # 检测中断位置
    last_completed = recorder.get_last_completed_case()
    total = recorder.config["test_configuration"]["total_cases"]
    
    # 检查环境一致性
    environment_check = recorder.check_environment_consistency(get_current_environment())
    
    if not environment_check["consistent"]:
        print("⚠️ 环境已变更，无法继续")
        print("建议：创建新批次重新测试")
        return "ABORT"
    
    # 提供选择
    print(f"📊 批次状态分析:")
    print(f"  - 已完成: {last_completed}/{total}")
    print(f"  - 环境: 一致")
    print()
    print("[A] 从断点继续执行（符合IEEE 829标准）")
    print("[B] 重新执行所有用例（更安全）")
    print("[C] 创建新批次")
    
    choice = input("请选择 [A/B/C]: ").upper()
    
    if choice == "A":
        return "CONTINUE"
    elif choice == "B":
        return "RESTART"
    else:
        return "NEW_BATCH"
```

---

## 五、完整性保障机制

### 5.1 验证检查项

| 检查项 | 期望值 | 实际值 | 状态 |
|--------|--------|--------|------|
| 用例覆盖率 | 100% | 根据实际计算 | PASS/FAIL |
| 结果一致性 | records数 = results数 | 根据实际计算 | PASS/FAIL |
| 配置基线完整性 | 无缺失字段 | 检查必需字段 | PASS/FAIL |

### 5.2 审计报告示例

```markdown
# 测试执行审计报告

## 批次信息
- 批次ID: batch-001
- 测试运行ID: TR-2026-04-05-001
- 执行时间: 2026-04-05T18:00:00 ~ 2026-04-05T21:56:32

## 完整性检查
| 检查项 | 期望值 | 实际值 | 状态 |
|--------|--------|--------|------|
| 用例覆盖率 | 100% | 100.0% | PASS |
| 结果一致性 | 80 | 80 | PASS |
| 配置基线完整性 | 无缺失字段 | 无缺失字段 | PASS |

## 配置基线
- 用例版本: 1.1
- 被测模型: ernie-4.5-turbo-128k
- 评测模型: ernie-4.5-turbo-128k

## 结论
✅ 测试执行完整，符合审计要求
```

---

## 六、实施计划

### 6.1 实施步骤

1. **创建 record_test_run.py 模块**
   - 实现 TestRunRecorder 类
   - 实现配置基线管理功能
   - 实现执行日志管理功能
   - 实现完整性验证功能
   - 实现异常检测功能

2. **修改 run_tests.py**
   - 导入 record_test_run 模块
   - 集成记录功能到执行流程
   - 添加完整性验证
   - 添加异常处理逻辑

3. **测试验证**
   - 测试全新测试场景
   - 测试中断恢复场景
   - 测试版本变更场景
   - 测试完整性验证

### 6.2 预估工作量

- 新增代码行数: ~500 行（record_test_run.py）
- 修改代码行数: ~150 行（run_tests.py）
- 预估开发时间: 4-6 小时
- 预估测试时间: 2-3 小时

---

## 七、风险评估

| 风险项 | 影响程度 | 发生概率 | 缓解措施 |
|--------|---------|---------|---------|
| 现有测试流程中断 | 高 | 低 | 保持向后兼容，现有功能不变 |
| 性能影响 | 中 | 低 | 日志写入采用追加模式，性能影响小 |
| 用户学习成本 | 低 | 中 | 提供详细文档和使用示例 |

---

## 八、后续优化

1. **支持 Git Hook 自动化**: 提交时自动验证测试执行完整性
2. **支持历史对比**: 自动对比不同批次的测试结果
3. **支持趋势分析**: 生成测试质量趋势报告
4. **支持导出功能**: 导出审计报告为 PDF/HTML 格式

---

## 附录

### A. IEEE 829 标准对照

本设计符合 IEEE 829 测试文档标准的以下要求：

- **测试计划**: test_config.json 记录测试计划信息
- **测试用例说明**: cases/universal.json 已有
- **测试规程说明**: run_tests.py 已有
- **测试日志**: test_execution.log 新增
- **测试事件报告**: test_execution.log 包含
- **测试总结报告**: summary.md 已有

### B. 相关文档

- [scripts/README.md](../../scripts/README.md) - 脚本使用说明
- [docs/prompt-engineering-guide.md](../prompt-engineering-guide.md) - Prompt 工程设计指南

---

*文档版本: 1.0*
*最后更新: 2026-04-06*
