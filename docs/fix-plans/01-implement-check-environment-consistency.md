# 任务1：实现 check_environment_consistency() 方法

> **优先级**: 高
> **预计工作量**: 2小时
> **涉及文件**: `scripts/record_test_run.py`

---

## 问题描述

**当前状态**：
- `record_test_run.py` 中没有 `check_environment_consistency()` 方法
- 中断恢复时无法验证环境是否变更

**影响**：
- 如果模型、API端点、配置在中断期间发生变化
- 会导致测试结果不一致，无法追溯问题原因

---

## 修改方案

### 步骤1：添加环境一致性检查方法

**文件**: `scripts/record_test_run.py`

**在第 451 行后添加**：

```python
def check_environment_consistency(
    self,
    current_model: str,
    current_evaluator_model: str,
    current_api_endpoint: str
) -> Dict[str, Any]:
    """
    检查环境一致性（用于中断恢复）
    
    Args:
        current_model: 当前被测模型
        current_evaluator_model: 当前评测模型
        current_api_endpoint: 当前API端点
    
    Returns:
        dict: 一致性检查结果
    """
    if self.config is None:
        self.config = self.load_test_config()
    
    # 提取初始环境配置
    initial_model = self.config["environment"]["model_under_test"]
    initial_evaluator = self.config["environment"]["evaluator_model"]
    initial_endpoint = self.config["environment"]["api_endpoint"]
    
    # 检查一致性
    inconsistencies = []
    
    if current_model != initial_model:
        inconsistencies.append({
            "field": "model_under_test",
            "initial": initial_model,
            "current": current_model
        })
    
    if current_evaluator_model != initial_evaluator:
        inconsistencies.append({
            "field": "evaluator_model",
            "initial": initial_evaluator,
            "current": current_evaluator_model
        })
    
    if current_api_endpoint != initial_endpoint:
        inconsistencies.append({
            "field": "api_endpoint",
            "initial": initial_endpoint,
            "current": current_api_endpoint
        })
    
    return {
        "consistent": len(inconsistencies) == 0,
        "inconsistencies": inconsistencies,
        "checked_at": datetime.now().isoformat()
    }
```

### 步骤2：在 run_tests.py 中调用检查

**文件**: `scripts/run_tests.py`

**在主函数中添加中断恢复逻辑**（约在第 900 行附近）：

```python
# 如果是 append 模式，检查环境一致性
if args.report == 'append' and args.batch_id:
    # 加载现有配置
    recorder = TestRunRecorder(batch_dir)
    recorder.load_test_config()
    
    # 检查环境一致性
    env_check = recorder.check_environment_consistency(
        current_model="ernie-4.5-turbo-128k",
        current_evaluator_model="ernie-4.5-turbo-128k",
        current_api_endpoint="https://qianfan.baidubce.com/v2/chat/completions"
    )
    
    if not env_check["consistent"]:
        print("⚠️ 环境一致性检查失败:")
        for inconsistency in env_check["inconsistencies"]:
            print(f"  - {inconsistency['field']}: {inconsistency['initial']} → {inconsistency['current']}")
        print("⚠️ 建议新建批次而不是追加到现有批次")
        
        # 询问用户是否继续
        response = input("是否继续执行？(y/n): ")
        if response.lower() != 'y':
            print("❌ 测试已取消")
            return
    else:
        print("✅ 环境一致性检查通过")
```

---

## 测试验证

### 测试用例1：环境一致

```bash
# 1. 新建批次
python3 run_tests.py --mode single --report new

# 2. 追加测试（环境一致）
python3 run_tests.py --mode incremental --report append --batch-id batch-001
# 预期输出: ✅ 环境一致性检查通过
```

### 测试用例2：环境不一致

修改模型名后测试：

```bash
# 修改 run_tests.py 中的 model 参数
# 重新运行
python3 run_tests.py --mode incremental --report append --batch-id batch-001
# 预期输出: ⚠️ 环境一致性检查失败
```

---

## 修复效果

| 修复前 | 修复后 |
|--------|--------|
| ❌ 无法检测环境变化 | ✅ 自动检测环境变化 |
| ❌ 中断恢复后测试结果不可靠 | ✅ 提示用户环境不一致 |
| ❌ 无法追溯问题原因 | ✅ 记录环境变更历史 |

---

## 预计工作量

- 编码: 30 分钟
- 测试: 30 分钟
- 文档更新: 15 分钟
- **总计**: 1.5 小时

---

*创建时间: 2026-04-06*
