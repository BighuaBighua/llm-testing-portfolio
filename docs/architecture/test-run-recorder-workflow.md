# TestRunRecorder 工作流程详解

> 本文档详细解释 `record_test_run.py` 模块的作用、调用时机、数据流向和运行机制

## 📋 目录

- [1. 核心作用](#1-核心作用)
- [2. 调用时机](#2-调用时机)
- [3. 数据流向](#3-数据流向)
- [4. 运行机制](#4-运行机制)
- [5. 实际案例](#5-实际案例)
- [6. 常见问题](#6-常见问题)

---

## 1. 核心作用

### 🎯 设计目标

`TestRunRecorder` 是一个**测试运行审计和追溯模块**，用于：

1. **记录测试配置基线** - 确保测试环境可追溯
2. **记录执行日志** - 实时跟踪测试进度
3. **验证执行完整性** - 确保测试没有遗漏
4. **检测异常情况** - 识别中断、版本变更等异常
5. **生成审计报告** - 提供完整的审计证据

### 📊 解决的问题

| 问题 | 传统方式 | TestRunRecorder 方式 |
|------|----------|---------------------|
| **环境不可追溯** | 不知道用了哪个模型、哪个版本 | ✅ 记录完整环境信息（模型、版本、Git hash） |
| **中断无法恢复** | 测试中断后不知道执行到哪了 | ✅ 实时记录每个用例的执行状态 |
| **结果难以验证** | 不知道测试是否完整执行 | ✅ 自动验证覆盖率、一致性 |
| **问题难以排查** | 缺少详细的执行日志 | ✅ 记录每个用例的开始/结束时间、状态 |
| **审计证据缺失** | 无法证明测试执行情况 | ✅ 生成完整的审计报告 |

---

## 2. 调用时机

### 🚀 什么时候被调用？

`TestRunRecorder` 在 **`run_tests.py` 执行测试时** 被调用。

### 📍 调用位置

在 `run_tests.py` 的主函数中：

```python
# 1. 创建批次目录
batch_dir = f"projects/01-ai-customer-service/results/{batch_id}_{timestamp}"
os.makedirs(batch_dir, exist_ok=True)

# 2. 初始化记录器（重点！）
recorder = TestRunRecorder(batch_dir)

# 3. 创建测试配置基线
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

# 4. 开始记录执行日志
recorder.start_logging(test_config["test_run_id"])

# 5. 执行测试（每个用例都会调用 recorder）
for test_case in test_cases:
    # 记录用例开始
    recorder.log_case_start(test_case['id'], i, len(test_cases))
    
    # 执行测试
    result = run_single_test(test_case)
    
    # 记录用例完成
    recorder.log_case_complete(test_case['id'], i, len(test_cases), result['status'])

# 6. 更新测试配置
recorder.update_test_config({
    "status": "completed",
    "execution_metrics": {
        "total_duration_seconds": duration,
        "success_rate": pass_rate
    }
})

# 7. 结束日志记录
recorder.end_logging({
    "total": len(test_cases),
    "passed": passed_count
})

# 8. 完整性验证
coverage_validation = recorder.validate_coverage(len(test_cases), len(results))
consistency_validation = recorder.validate_consistency(len(test_cases), len(results))
config_validation = recorder.validate_config_integrity()

# 9. 生成审计报告
audit_report = recorder.generate_audit_report(validation_results)
recorder.save_audit_report(audit_report)
```

### ⏰ 完整调用时间线

```
用户执行命令：python3 run_tests.py --mode full
    ↓
[时间点1] 初始化记录器
    recorder = TestRunRecorder(batch_dir)
    ├─ 创建 test_config.json（配置基线文件）
    └─ 创建 test_execution.log（执行日志文件）
    ↓
[时间点2] 创建测试配置基线
    recorder.create_test_config(...)
    └─ 写入 test_config.json
    ↓
[时间点3] 开始记录执行日志
    recorder.start_logging(test_run_id)
    └─ 写入 test_execution.log（开始标记）
    ↓
[时间点4] 执行每个测试用例
    for each test_case:
        recorder.log_case_start(...)      # 写入日志：用例开始
        ├─ 执行测试
        └─ recorder.log_case_complete(...) # 写入日志：用例完成
    ↓
[时间点5] 更新测试配置
    recorder.update_test_config({...})
    └─ 更新 test_config.json（状态、指标）
    ↓
[时间点6] 结束日志记录
    recorder.end_logging({...})
    └─ 写入 test_execution.log（结束标记）
    ↓
[时间点7] 完整性验证
    recorder.validate_coverage(...)       # 验证覆盖率
    recorder.validate_consistency(...)    # 验证一致性
    recorder.validate_config_integrity()  # 验证配置完整性
    ↓
[时间点8] 生成审计报告
    recorder.generate_audit_report(...)
    └─ recorder.save_audit_report(...)    # 保存审计报告
```

---

## 3. 数据流向

### 📂 生成的文件

`TestRunRecorder` 会生成以下文件：

```
projects/01-ai-customer-service/results/batch-XXX_YYYY-MM-DD/
├── test_config.json          # 测试配置基线（新增）⭐
├── test_execution.log        # 测试执行日志（新增）⭐
├── audit_report.json         # 审计报告（新增）⭐
├── records.json              # 测试执行记录（原有）
├── results.json              # 测试结果（原有）
└── summary.md                # 测试摘要（原有）
```

### 📄 文件说明

#### 1️⃣ **test_config.json** - 测试配置基线

**作用**：记录测试开始时的完整配置信息，确保环境可追溯

**生成时机**：`recorder.create_test_config()` 时创建

**内容结构**：

```json
{
  "batch_id": "batch-005",
  "test_run_id": "TR-2026-04-06-005",
  "created_at": "2026-04-06T11:30:00",
  "completed_at": "2026-04-06T14:45:32",
  "status": "completed",
  
  "test_configuration": {
    "test_case_version": "1.3",
    "test_case_file": "cases/universal.json",
    "test_case_hash": "a1b2c3d4",        // Git commit hash
    "total_cases": 80,
    "dimensions": ["accuracy", "completeness", ...]
  },
  
  "environment": {
    "model_under_test": "ernie-4.5-turbo-128k",
    "evaluator_model": "ernie-4.5-turbo-128k",
    "api_endpoint": "https://aip.baidubce.com/...",
    "python_version": "3.9.7",
    "os": "Darwin-21.6.0"
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
    "api_calls": 160,                    // 80条用例 × 2次调用
    "total_tokens": 125000
  },
  
  "quality_gates": {
    "pass_rate_threshold": 0.9,
    "actual_pass_rate": 0.95,
    "result": "PASS"                     // PASS / FAIL / PENDING
  }
}
```

**用途**：
- ✅ 环境追溯：知道测试用了哪个模型、哪个版本的用例
- ✅ 中断恢复：通过 `test_case_hash` 检查用例文件是否变更
- ✅ 版本对比：对比不同批次的配置差异

---

#### 2️⃣ **test_execution.log** - 测试执行日志

**作用**：实时记录每个用例的执行情况，类似航班跟踪系统

**生成时机**：`recorder.start_logging()` 时创建，后续追加

**内容示例**：

```log
[2026-04-06 11:30:00] INFO  Test run started: TR-2026-04-06-005
[2026-04-06 11:30:00] INFO  Loading test cases from: cases/universal.json (v1.3)
[2026-04-06 11:30:00] INFO  Test configuration loaded: 80 cases, 8 dimensions
[2026-04-06 11:30:00] INFO  Starting test execution...
[2026-04-06 11:30:05] INFO  [1/80] TC-ACC-001 started
[2026-04-06 11:32:45] INFO  [1/80] TC-ACC-001 completed - PASS
[2026-04-06 11:32:47] INFO  [2/80] TC-ACC-002 started
[2026-04-06 11:35:12] INFO  [2/80] TC-ACC-002 completed - PASS
...
[2026-04-06 14:45:30] INFO  [80/80] TC-IND-010 completed - PASS
[2026-04-06 14:45:32] INFO  Test run completed: 80 total, 76 passed, 4 failed
[2026-04-06 14:45:32] INFO  Execution duration: 14192 seconds
```

**用途**：
- ✅ 进度跟踪：实时查看测试执行到哪了
- ✅ 中断恢复：知道哪个用例是最后执行的
- ✅ 问题排查：快速定位执行异常的用例

---

#### 3️⃣ **audit_report.json** - 审计报告

**作用**：验证测试执行的完整性和一致性，提供审计证据

**生成时机**：`recorder.generate_audit_report()` 时创建

**内容结构**：

```json
{
  "audit_id": "AUDIT-2026-04-06-005",
  "audit_time": "2026-04-06T14:45:35",
  "batch_id": "batch-005",
  "test_run_id": "TR-2026-04-06-005",
  
  "validation_results": [
    {
      "check_type": "coverage",
      "status": "PASS",
      "details": {
        "expected": 80,
        "actual": 80,
        "coverage_rate": 1.0
      },
      "message": "所有用例已执行完成"
    },
    {
      "check_type": "consistency",
      "status": "PASS",
      "details": {
        "config_cases": 80,
        "executed_cases": 80,
        "results_cases": 80
      },
      "message": "配置、执行记录、结果记录三者一致"
    },
    {
      "check_type": "config_integrity",
      "status": "PASS",
      "details": {
        "has_batch_id": true,
        "has_test_run_id": true,
        "has_completed_at": true,
        "has_execution_metrics": true
      },
      "message": "配置文件完整，无缺失字段"
    }
  ],
  
  "overall_status": "PASS",
  "summary": "测试执行完整，数据一致，配置完整"
}
```

**用途**：
- ✅ 完整性验证：确保所有用例都执行了
- ✅ 一致性验证：确保配置、执行记录、结果记录三者一致
- ✅ 审计证据：提供给质量团队的审计证明

---

### 🔄 数据流向图

```
用户执行命令
    ↓
run_tests.py 主脚本
    ↓
    ├─→ TestRunRecorder 记录器
    │   ├─→ test_config.json       （配置基线）
    │   ├─→ test_execution.log     （执行日志）
    │   └─→ audit_report.json      （审计报告）
    │
    ├─→ 执行测试用例
    │   ├─→ records.json           （执行记录）
    │   └─→ results.json           （评测结果）
    │
    └─→ 生成测试报告
        └─→ summary.md             （测试摘要）
```

---

## 4. 运行机制

### 🔧 核心方法

#### 1️⃣ **配置基线管理**

```python
# 创建配置基线
config = recorder.create_test_config(
    batch_id="batch-005",
    test_case_version="1.3",
    test_case_file="cases/universal.json",
    model="ernie-4.5-turbo-128k",
    evaluator_model="ernie-4.5-turbo-128k",
    test_parameters={"mode": "full", "concurrent": 1}
)

# 加载配置基线
config = recorder.load_test_config()

# 更新配置基线
recorder.update_test_config({
    "status": "completed",
    "execution_metrics": {
        "total_duration_seconds": 14192,
        "success_rate": 0.95
    }
})
```

**作用**：
- 记录测试开始时的完整配置
- 后续可以更新配置（如状态、指标）
- 用于中断恢复时验证环境是否变更

---

#### 2️⃣ **执行日志管理**

```python
# 开始记录日志
recorder.start_logging(test_run_id="TR-2026-04-06-005")

# 记录用例开始执行
recorder.log_case_start(
    case_id="TC-ACC-001",
    index=1,
    total=80
)

# 记录用例执行完成
recorder.log_case_complete(
    case_id="TC-ACC-001",
    index=1,
    total=80,
    status="PASS"
)

# 记录错误
recorder.log_error(
    case_id="TC-ACC-005",
    error_type="API_TIMEOUT",
    error_message="API调用超时（60秒）"
)

# 结束记录日志
recorder.end_logging({
    "total": 80,
    "passed": 76,
    "failed": 4
})
```

**作用**：
- 实时记录每个用例的执行情况
- 类似航班跟踪系统，记录"起飞"和"降落"
- 用于中断恢复时定位最后执行的用例

---

#### 3️⃣ **完整性验证**

```python
# 验证覆盖率
coverage_result = recorder.validate_coverage(
    expected_count=80,
    actual_count=80
)
# 返回：{"valid": true, "coverage_rate": 1.0, "message": "所有用例已执行"}

# 验证一致性
consistency_result = recorder.validate_consistency(
    config_count=80,     # 配置中的用例数
    executed_count=80    # 实际执行的用例数
)
# 返回：{"valid": true, "message": "配置与执行记录一致"}

# 验证配置完整性
integrity_result = recorder.validate_config_integrity()
# 返回：{"valid": true, "missing_fields": [], "message": "配置完整"}
```

**作用**：
- 确保所有用例都执行了
- 确保配置、执行记录、结果记录三者一致
- 确保配置文件没有缺失关键字段

---

#### 4️⃣ **异常检测**

```python
# 检测中断
interruption = recorder.detect_interruption()
# 返回：{"detected": false} 或 {"detected": true, "completed": 45, "total": 80}

# 检查版本兼容性
compatibility = recorder.check_version_compatibility(
    current_version="1.3",
    expected_version="1.3"
)
# 返回：{"compatible": true} 或 {"compatible": false, "reason": "版本不匹配"}

# 检查环境一致性（用于中断恢复）
consistency = recorder.check_environment_consistency(
    current_model="ernie-4.5-turbo-128k",
    current_evaluator_model="ernie-4.5-turbo-128k",
    current_api_endpoint="https://aip.baidubce.com/..."
)
# 返回：{"consistent": true} 或 {"consistent": false, "inconsistencies": [...]}
```

**作用**：
- 检测测试是否中断
- 检测版本是否变更
- 检测环境是否变更（模型、API端点等）

---

#### 5️⃣ **审计报告生成**

```python
# 生成审计报告
validation_results = [
    coverage_validation,
    consistency_validation,
    config_validation
]
audit_report = recorder.generate_audit_report(validation_results)

# 保存审计报告
recorder.save_audit_report(audit_report)
```

**作用**：
- 汇总所有验证结果
- 生成完整的审计报告
- 提供给质量团队作为审计证据

---

### 🔄 完整运行流程

```
┌─────────────────────────────────────────────────────────┐
│           1. 初始化阶段（测试开始前）                      │
└─────────────────────────────────────────────────────────┘
    ↓
    创建批次目录
    ↓
    初始化记录器 → recorder = TestRunRecorder(batch_dir)
    ├─ 创建 test_config.json（空文件）
    └─ 创建 test_execution.log（空文件）
    ↓
    创建配置基线 → recorder.create_test_config(...)
    ├─ 记录批次ID、测试运行ID
    ├─ 记录用例版本、文件路径、Git hash
    ├─ 记录模型、API端点、环境信息
    └─ 写入 test_config.json
    ↓
    开始记录日志 → recorder.start_logging(...)
    └─ 写入 test_execution.log（开始标记）

┌─────────────────────────────────────────────────────────┐
│           2. 执行阶段（测试进行中）                        │
└─────────────────────────────────────────────────────────┘
    ↓
    for each test_case:
        ├─ 记录用例开始 → recorder.log_case_start(...)
        │   └─ 写入 test_execution.log：[时间] [1/80] TC-ACC-001 started
        │
        ├─ 执行测试
        │   ├─ 调用API获取AI回答
        │   ├─ 调用API进行评测
        │   └─ 解析评测结果
        │
        └─ 记录用例完成 → recorder.log_case_complete(...)
            └─ 写入 test_execution.log：[时间] [1/80] TC-ACC-001 completed - PASS

┌─────────────────────────────────────────────────────────┐
│           3. 结束阶段（测试完成后）                        │
└─────────────────────────────────────────────────────────┘
    ↓
    更新配置基线 → recorder.update_test_config({...})
    ├─ 更新状态：completed
    ├─ 更新完成时间
    ├─ 更新执行指标（总时长、成功率、API调用次数）
    └─ 写入 test_config.json
    ↓
    结束日志记录 → recorder.end_logging({...})
    └─ 写入 test_execution.log（结束标记：总计、通过、失败）
    ↓
    完整性验证：
    ├─ recorder.validate_coverage(...)           # 验证覆盖率
    ├─ recorder.validate_consistency(...)        # 验证一致性
    └─ recorder.validate_config_integrity()      # 验证配置完整性
    ↓
    生成审计报告 → recorder.generate_audit_report(...)
    └─ 保存审计报告 → recorder.save_audit_report(...)
        └─ 写入 audit_report.json

┌─────────────────────────────────────────────────────────┐
│           4. 审计阶段（测试结束后）                        │
└─────────────────────────────────────────────────────────┘
    ↓
    质量团队查看：
    ├─ test_config.json      → 了解测试环境配置
    ├─ test_execution.log    → 了解测试执行过程
    └─ audit_report.json     → 验证测试完整性
```

---

## 5. 实际案例

### 📋 场景1：正常执行完成

**命令**：
```bash
python3 run_tests.py --mode full --report new
```

**生成的文件**：
```
batch-005_2026-04-06/
├── test_config.json          # ✅ 配置完整
├── test_execution.log        # ✅ 日志完整
├── audit_report.json         # ✅ 审计通过
├── records.json
├── results.json
└── summary.md
```

**test_config.json**：
```json
{
  "status": "completed",
  "completed_at": "2026-04-06T14:45:32",
  "execution_metrics": {
    "total_duration_seconds": 14192,
    "success_rate": 0.95
  }
}
```

**test_execution.log**：
```log
[2026-04-06 11:30:00] INFO  Test run started: TR-2026-04-06-005
...
[2026-04-06 14:45:30] INFO  [80/80] TC-IND-010 completed - PASS
[2026-04-06 14:45:32] INFO  Test run completed: 80 total, 76 passed, 4 failed
```

**audit_report.json**：
```json
{
  "overall_status": "PASS",
  "summary": "测试执行完整，数据一致，配置完整"
}
```

---

### 📋 场景2：测试中断后恢复

**中断情况**：
```log
[2026-04-06 11:30:00] INFO  Test run started: TR-2026-04-06-006
...
[2026-04-06 12:15:30] INFO  [45/80] TC-ATT-005 started
# ⚠️ 程序崩溃或网络中断，只执行了45条用例
```

**恢复流程**：

```python
# 1. 检测中断
interruption = recorder.detect_interruption()
# 返回：{"detected": true, "completed": 45, "total": 80}

# 2. 检查环境是否变更
consistency = recorder.check_environment_consistency(
    current_model="ernie-4.5-turbo-128k",
    current_evaluator_model="ernie-4.5-turbo-128k",
    current_api_endpoint="https://aip.baidubce.com/..."
)
# 返回：{"consistent": true}

# 3. 恢复测试
python3 run_tests.py --mode incremental --batch-id batch-006
```

**恢复后的文件**：
```log
[2026-04-06 13:00:00] INFO  Resuming from interruption at case 45/80
[2026-04-06 13:00:05] INFO  [46/80] TC-ATT-006 started
...
[2026-04-06 15:30:30] INFO  [80/80] TC-IND-010 completed - PASS
[2026-04-06 15:30:32] INFO  Test run completed: 80 total, 76 passed, 4 failed
```

---

### 📋 场景3：环境变更导致不一致

**场景描述**：
- 初始测试使用模型：`ernie-4.5-turbo-128k`
- 中断期间模型升级为：`ernie-4.5-turbo-256k`

**检测结果**：
```python
consistency = recorder.check_environment_consistency(
    current_model="ernie-4.5-turbo-256k",  # 新模型
    current_evaluator_model="ernie-4.5-turbo-128k",
    current_api_endpoint="https://aip.baidubce.com/..."
)

# 返回：
{
  "consistent": false,
  "inconsistencies": [
    {
      "field": "model_under_test",
      "initial": "ernie-4.5-turbo-128k",
      "current": "ernie-4.5-turbo-256k"
    }
  ]
}
```

**处理方式**：
- ⚠️ 警告用户：环境已变更，建议重新测试
- ✅ 或者：允许用户强制恢复，但标记为"环境不一致"

---

## 6. 常见问题

### ❓ Q1: 为什么旧的批次没有 test_config.json 和 test_execution.log？

**答案**：
- `record_test_run.py` 是 **2026-04-06** 才添加的新功能
- 旧的批次（如 batch-004）是在这个功能之前创建的
- 只有 **2026-04-06 之后** 创建的批次才会有这些文件

---

### ❓ Q2: 如果我不想使用 TestRunRecorder，可以禁用吗？

**答案**：
可以！在 `run_tests.py` 中注释掉相关代码：

```python
# 不初始化记录器
# recorder = TestRunRecorder(batch_dir)
recorder = None

# 后续的 recorder.xxx() 调用都会被跳过（因为 recorder = None）
```

**但是**：不推荐禁用，因为会失去以下能力：
- ❌ 环境追溯
- ❌ 中断恢复
- ❌ 完整性验证
- ❌ 审计证据

---

### ❓ Q3: test_config.json 和 records.json 有什么区别？

**对比**：

| 文件 | 作用 | 内容 | 更新频率 |
|------|------|------|---------|
| **test_config.json** | 配置基线 | 环境、参数、指标 | 低频更新（开始、结束、关键节点） |
| **records.json** | 执行记录 | 每个用例的详细执行信息 | 高频更新（每个用例） |

**示例**：

```json
// test_config.json（配置基线）
{
  "environment": {
    "model": "ernie-4.5-turbo-128k"
  },
  "execution_metrics": {
    "total_duration_seconds": 14192
  }
}

// records.json（执行记录）
[
  {
    "test_case_id": "TC-ACC-001",
    "timestamp": "2026-04-06T11:30:05",
    "customer_response": "XX信息通常包含...",
    "evaluation_result": {...}
  }
]
```

---

### ❓ Q4: audit_report.json 是什么时候生成的？

**答案**：
- 在 **所有测试执行完成后** 生成
- 在 `run_tests.py` 的最后阶段：
  ```python
  # 完整性验证
  validation_results = [...]
  
  # 生成审计报告
  audit_report = recorder.generate_audit_report(validation_results)
  recorder.save_audit_report(audit_report)
  ```

---

### ❓ Q5: 如果测试中途失败，会有 audit_report.json 吗？

**答案**：
- **不会**。只有在测试完全执行完成后才会生成审计报告
- 如果测试中途失败，只有：
  - ✅ test_config.json（状态为 "running"）
  - ✅ test_execution.log（记录到失败前的用例）
  - ❌ audit_report.json（未生成）

---

### ❓ Q6: 如何查看测试是否中断？

**方法1：查看 test_config.json**
```json
{
  "status": "running",  // 如果是 "running" 说明未完成
  "completed_at": null  // 如果是 null 说明未完成
}
```

**方法2：调用检测方法**
```python
recorder = TestRunRecorder(batch_dir)
interruption = recorder.detect_interruption()
# 返回：{"detected": true, "completed": 45, "total": 80}
```

**方法3：查看 test_execution.log**
```log
[2026-04-06 12:15:30] INFO  [45/80] TC-ATT-005 started
# 如果最后一行是 "started" 而不是 "completed"，说明中断了
```

---

## 📚 相关文档

- [中断恢复用户指南](../user-guide/interruption-recovery.md)
- [测试报告解读指南](../user-guide/report-interpretation.md)
- [脚本使用说明](../../scripts/README.md)

---

**最后更新**：2026-04-06
