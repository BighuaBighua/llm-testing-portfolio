# 📋 后续修改清单总览

> **创建时间**: 2026-04-06
> **更新时间**: 2026-04-06
> **优先级分类**: 近期修复 + 后续优化

---

## 📊 修改任务概览

```
┌─────────────────────────────────────────────────────────┐
│                  后续修改任务清单                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔴 近期修复（建议下周完成）                             │
│  ├─ 1️⃣ 实现 check_environment_consistency() 方法      │
│  ├─ 2️⃣ 统一版本号管理                                  │
│  ├─ 3️⃣ 消除硬编码配置                                  │
│  └─ 4️⃣ 补充缺失文档                                    │
│                                                         │
│  🟡 后续优化（持续改进）                                │
│  ├─ 5️⃣ 重构重复代码                                    │
│  ├─ 6️⃣ 优化模板使用逻辑                                │
│  ├─ 7️⃣ 补充类型提示                                    │
│  └─ 8️⃣ 改进错误处理                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔴 近期修复任务（建议下周完成）

### 任务1：实现 check_environment_consistency() 方法

**📄 详细方案**: [01-implement-check-environment-consistency.md](./01-implement-check-environment-consistency.md)

**问题说明**：
- 中断恢复时无法验证环境是否变更
- 可能导致测试结果不可靠

**修改内容**：
```python
# 在 record_test_run.py 中添加方法
def check_environment_consistency(
    self,
    current_model: str,
    current_evaluator_model: str,
    current_api_endpoint: str
) -> Dict[str, Any]:
    # 检查环境一致性
    # 返回检查结果
```

**工作量**: 1.5 小时

**影响范围**: 
- `scripts/record_test_run.py`（添加方法）
- `scripts/run_tests.py`（调用检查）

---

### 任务2：统一版本号管理

**📄 详细方案**: [02-unify-version-management.md](./02-unify-version-management.md)

**问题说明**：
- `universal.json` version="1.1"
- `results.json` version="2.0" 
- 版本号混乱，无法追溯

**修改方案**（推荐方案B）：
```json
{
  "metadata": {
    "version": "1.1",
    "changelog": [
      {
        "version": "1.0",
        "changes": "初始版本"
      },
      {
        "version": "1.1",
        "changes": "修正 compliance 用例 ID 冲突"
      }
    ]
  }
}
```

**工作量**: 0.5 小时（方案B）

**影响范围**:
- `projects/01-ai-customer-service/cases/universal.json`

---

### 任务3：消除硬编码配置

**📄 详细方案**: [03-eliminate-hardcoded-config.md](./03-eliminate-hardcoded-config.md)

**问题说明**：
- 模型名 `ernie-4.5-turbo-128k` 硬编码 7 处
- API URL、延迟时间等配置分散
- 修改配置需要改动多处

**修改方案**：
```python
# 创建 scripts/config.py
MODEL_UNDER_TEST = "ernie-4.5-turbo-128k"
EVALUATOR_MODEL = "ernie-4.5-turbo-128k"
API_ENDPOINT = "https://qianfan.baidubce.com/v2/chat/completions"
SINGLE_THREAD_DELAY = 2.0
CONCURRENT_DELAY = 0.5

# 在 run_tests.py 中导入使用
from config import MODEL_UNDER_TEST, API_ENDPOINT
```

**工作量**: 1 小时

**影响范围**:
- `scripts/config.py`（新建）
- `scripts/run_tests.py`（修改 7 处）

---

### 任务4：补充缺失文档

**📄 详细方案**: [04-add-missing-documents.md](./04-add-missing-documents.md)

**问题说明**：
- 缺少中断恢复用户指南
- 缺少测试报告解读指南
- 缺少 Bad Case 分析文档

**修改内容**：
```
docs/
├── user-guide/
│   ├── interruption-recovery.md      # 中断恢复指南
│   └── report-interpretation.md      # 报告解读指南
└── technical-analysis/
    └── bad-case-analysis.md          # Bad Case 分析
```

**工作量**: 3 小时

**影响范围**:
- 新建 3 个文档文件

---

## 🟡 后续优化任务（持续改进）

### 任务5：重构重复代码

**问题说明**：
- `save_execution_records()` 和 `save_evaluation_results()` 有大量重复逻辑
- 代码冗余，维护成本高

**修改方案**：
```python
def save_data_to_file(
    self,
    data: List[Dict],
    output_path: str,
    mode: str = 'new',
    id_field: str = 'id'
):
    """通用数据保存方法"""
    if mode == 'append' and os.path.exists(output_path):
        existing_data = self._load_existing_data(output_path)
        data = self._merge_data(existing_data, data, id_field)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**工作量**: 1 小时

---

### 任务6：优化模板使用逻辑

**问题说明**：
- `run_tests.py` 加载了 `evaluator_template` 但未使用
- `build_test_prompt()` 完全重写了 prompt
- 模板加载逻辑冗余

**修改方案**：
```python
# 方案A：使用模板
def build_test_prompt(self, test_case: Dict) -> str:
    return self.evaluator_template.format(
        case_id=test_case['id'],
        dimension=test_case['dimension'],
        input=test_case['input'],
        # ...
    )

# 方案B：删除模板加载
def __init__(self, api_key: str):
    # 删除 evaluator_template_path 参数
    # 删除模板加载逻辑
```

**工作量**: 0.5 小时

---

### 任务7：补充类型提示

**问题说明**：
- 部分方法缺少类型提示
- 不利于代码维护和 IDE 提示

**修改方案**：
```python
# 修改前
def parse_response(self, response, test_case):
    # ...

# 修改后
def parse_response(self, response: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
    # ...
```

**工作量**: 1 小时

---

### 任务8：改进错误处理

**问题说明**：
- `_get_git_hash()` 异常时只返回 "unknown"
- 缺少日志警告
- 错误信息不够详细

**修改方案**：
```python
def _get_git_hash(self, file_path: str) -> str:
    try:
        result = subprocess.run(...)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git 命令执行失败: {e}")
        return "unknown"
    except FileNotFoundError:
        logger.warning("Git 未安装或不在 PATH 中")
        return "unknown"
    except Exception as e:
        logger.error(f"获取 Git hash 时发生未知错误: {e}")
        return "unknown"
```

**工作量**: 0.5 小时

---

## 📈 工作量统计

### 近期修复任务

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| 1. 实现 check_environment_consistency() | 1.5 小时 | 高 |
| 2. 统一版本号管理 | 0.5 小时 | 高 |
| 3. 消除硬编码配置 | 1 小时 | 中 |
| 4. 补充缺失文档 | 3 小时 | 中 |
| **小计** | **6 小时** | - |

### 后续优化任务

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| 5. 重构重复代码 | 1 小时 | 低 |
| 6. 优化模板使用逻辑 | 0.5 小时 | 低 |
| 7. 补充类型提示 | 1 小时 | 低 |
| 8. 改进错误处理 | 0.5 小时 | 低 |
| **小计** | **3 小时** | - |

### 总计

- **近期修复**: 6 小时
- **后续优化**: 3 小时
- **总计**: 9 小时

---

## 🎯 建议执行顺序

### 第1周（重点）

```
Day 1-2: 任务1（check_environment_consistency）
Day 3:   任务2（版本号管理）
Day 4:   任务3（硬编码配置）
Day 5:   任务4（补充文档）
```

### 第2周（优化）

```
Day 1-2: 任务5-6（代码重构）
Day 3-4: 任务7-8（类型提示和错误处理）
Day 5:   整体测试和文档更新
```

---

## ✅ 验收标准

### 近期修复任务

- ✅ 所有修复任务完成
- ✅ Lint 检查通过（0 错误）
- ✅ 功能测试通过
- ✅ 文档已更新

### 后续优化任务

- ✅ 代码重构完成
- ✅ 类型提示完整
- ✅ 错误处理完善
- ✅ 代码可维护性提升

---

## 📝 相关文档

- [高优先级问题修复记录](../fix-records/2026-04-06-high-priority-fixes.md)
- [项目全局自查报告](../fix-records/2026-04-06-high-priority-fixes.md#后续建议)

---

*创建时间: 2026-04-06*
*预计完成时间: 2026-04-20*
