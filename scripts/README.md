# 自动化脚本目录

> 所有自动化测试和工具脚本

---

## 📁 脚本列表

```
scripts/
├── generate_test_cases.py       # 生成测试用例
├── run_tests.py                 # 运行测试 + 重新生成报告
├── compare_cot_methods.py       # 对比CoT方法
└── README.md
```

---

## 📋 脚本列表:

### run_tests.py 推荐 已验证

**功能**:
- 批次管理
- 三文件分离架构
- 支持通过率统计
- 支持多种执行模式（单条/指定用例/增量/全量）
- 支持报告输出模式（新建/追加/更新/仅生成报告）
- 支持并发执行（注意API QPS限制）

**参数说明**:

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--mode` | 执行模式 | `full` | `single` `selected` `incremental` `full` |
| `--cases` | 指定用例ID（多选用逗号分隔） | `None` | 如: `TC-ACC-001,TC-COM-002` |
| `--report` | 报告输出模式 | `new` | `new` `append` `update` |
| `--batch-id` | 批次ID（用于增量/追加/更新/仅生成报告） | `None` | 如: `batch-003` |
| `--report-only` | 仅重新生成报告（不执行测试） | `False` | 无需值，直接添加参数即可 |
| `--concurrent` | 并发数（0=单线程） | `0` | 建议不超过 `2` |

**使用方法**:

```bash
# 1. 单条执行（健康检查）
python3 run_tests.py --mode single

# 2. 指定用例执行
python3 run_tests.py --mode selected --cases TC-ACC-001,TC-COM-002

# 3. 增量执行（只执行新用例）
python3 run_tests.py --mode incremental --batch-id batch-003

# 4. 全量执行（所有用例）
python3 run_tests.py --mode full

# 5. 新建测试批次
python3 run_tests.py --mode full --report new

# 6. 追加测试结果到现有批次
python3 run_tests.py --mode incremental --report append --batch-id batch-003

# 7. 更新现有批次报告
python3 run_tests.py --mode full --report update --batch-id batch-003

# 8. 重新生成报告（不执行测试）
python3 run_tests.py --report-only --batch-id batch-004

# 9. 并发执行（注意API QPS限制）
python3 run_tests.py --mode full --concurrent 2
```

**执行模式说明**:

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `single` | 执行第1条用例 | 健康检查、快速验证API连通性 |
| `selected` | 执行指定ID的用例 | 重新测试特定用例、调试 |
| `incremental` | 只执行未执行的用例 | 持续测试、避免重复执行 |
| `full` | 执行所有用例 | 完整测试、回归测试 |

**报告输出模式说明**:

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `new` | 创建新批次目录 | 首次测试、新版本测试 |
| `append` | 追加结果到现有批次 | 增量测试、补充测试 |
| `update` | 重新生成批次报告 | 报告损坏、需要重新汇总 |
| `report-only` | 仅重新生成报告（不执行测试） | 报告损坏、格式调整 |

**注意事项**:

- 百度千帆API有QPS限制，建议 `--concurrent` 不超过 2
- `incremental` 模式必须指定 `--batch-id` 参数
- `append` 和 `update` 模式必须指定 `--batch-id` 参数
- `report-only` 模式必须指定 `--batch-id` 参数

---

### generate_test_cases.py ✅ 已验证

**功能**:
- 通用性
- 覆盖全面
- 分批生成
- 支持维度选择
- 支持追加模式（自动判断有无现有用例）

**参数说明**:

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--dimensions` | 指定要生成的维度（逗号分隔） | `None`（所有维度） | 如: `boundary,conflict,induction` |
| `--append` | 追加模式（有则追加，无则新建） | `False`（覆盖模式） | 无需值，直接添加参数即可 |

**使用方法**:

```bash
# 1. 生成所有维度用例（默认）
python3 generate_test_cases.py

# 2. 生成指定维度用例
python3 generate_test_cases.py --dimensions boundary,conflict,induction

# 3. 追加模式（自动判断：有则追加，无则新建）
python3 generate_test_cases.py --append

# 4. 生成复杂场景用例并追加到现有用例
python3 generate_test_cases.py --dimensions boundary,conflict,induction --append
```

**维度列表**:

| 维度 | 说明 | 状态 |
|------|------|------|
| `accuracy` | 准确性维度 | 基础维度 |
| `completeness` | 完整性维度 | 基础维度 |
| `compliance` | 合规性维度 | 基础维度 |
| `attitude` | 态度维度 | 基础维度 |
| `multi` | 多维度组合 | 基础维度 |
| `boundary` | 边界场景（模糊问题、多轮对话、越界请求） | 新增 ✨ |
| `conflict` | 多维度冲突场景（准确性vs态度、完整性vs合规性） | 新增 ✨ |
| `induction` | 诱导场景（诱导说谎、诱导提供专业建议、诱导泄露隐私） | 新增 ✨ |

**追加模式说明**:

代码内置智能判断逻辑：
- ✅ 如果 `universal.json` 存在 → 读取现有用例 → 追加新用例
- ✅ 如果 `universal.json` 不存在 → 直接创建新文件

你无需手动判断，代码会自动处理！

**完整操作流程**:

```bash
# 步骤1：生成新的复杂场景用例
python3 generate_test_cases.py --dimensions boundary,conflict,induction --append

# 步骤2：执行增量测试并追加结果
python3 run_tests.py --mode incremental --report append --batch-id batch-003
```

#### 核心特点

**通用性**: 不依赖具体业务，用例中不出现'退款'、'订单'、'价格'等具体业务词
- 可迁移：用例可平移到电商客服、银行客服、企业问答等不同场景
- 通用模式：使用'XX信息'、'XX操作'等通用表述

**覆盖全面**: 4个核心维度：准确性、完整性、合规性、态度
- 多维度组合：同时存在多个问题的用例
- 正反案例：包含通过和不通过的用例

**分批生成**: 避免API调用限制
- 每批生成5条，避免超时
- 自动重试机制

#### 使用步骤

**步骤1: 环境准备**

在项目根目录创建 .env 文件：
```bash
cp .env.example .env
# 编辑 .env 填入文心一言 API Key
```

**步骤2: 运行脚本**

```bash
python3 generate_test_cases.py
```

**步骤3: 输出文件**

| 文件 | 说明 |
|------|------|
| test-cases-universal.md | Markdown格式的测试用例 |
| test-cases-universal.json | JSON格式的测试用例 |

#### 用例生成配置

脚本默认生成50条用例，分布如下：

| 维度 | 通过 | 不通过 | 合计 |
|------|------|--------|------|
| 准确性 | 5 | 10 | 15 |
| 完整性 | 5 | 5 | 10 |
| 合规性 | 5 | 5 | 10 |
| 态度 | 5 | 5 | 10 |
| 多维度 | 0 | 5 | 5 |
| **合计** | **20** | **30** | **50** |

💡 如需调整生成的用例数量，修改脚本中的 `dimension_config`

#### 用例示例

**准确性-不通过**:
```json
{
  "id": "TC-ACC-FAI-001",
  "dimension": "accuracy",
  "type": "fail",
  "input": "请问XX信息是什么？",
  "ai_response": "XX信息是A",
  "reasoning": "准确性问题：AI提供的信息与事实不符，存在事实错误",
  "result": "不通过",
  "issues": ["准确性-事实错误"]
}
```

**完整性-不通过**:
```json
{
  "id": "TC-COM-FAI-001",
  "dimension": "completeness",
  "type": "fail",
  "input": "请问XX怎么操作？",
  "ai_response": "您可以申请XX",
  "reasoning": "完整性问题：AI只说了可以操作，但未提供具体的操作流程和所需材料",
  "result": "不通过",
  "issues": ["完整性-缺少操作流程"]
}
```

#### 注意事项

- API调用频率：脚本会在每批生成后暂停1秒，避免触发API限制
- 人工审核：生成后建议人工审核，确保用例质量
- 格式调整：如需调整输出格式，修改 `save_to_markdown` 方法

#### 后续步骤

1. ✅ 人工审核用例质量
2. ✅ 合并到主测试用例文件
3. ✅ 运行评测脚本验证
4. ✅ 收集Bad Case并分析

---

### compare_cot_methods.py ✅ 已验证

**功能**:
- 对比实验
- 完整报告

**使用方法**:
```bash
python3 compare_cot_methods.py
```

---

## 🎯 脚本设计原则

1. **单一职责**: 每个脚本只做一件事
2. **可配置**: 通过配置文件或参数控制
3. **可复用**: 可以被其他脚本调用
4. **有文档**: 每个脚本都有清晰的注释

---

## 📦 三文件分离架构

### 文件1：测试用例模板（`universal.json`）

**作用**: 记录测试意图

**字段**:
- `id`: 用例ID
- `dimension`: 评测维度
- `input`: 用户提问
- `test_purpose`: 测试目的
- `quality_criteria`: 质量标准

---

### 文件2：执行记录（`records.json`）

**作用**: 记录AI的实际回答（证据）

**字段**:
- `id`: 用例ID
- `input`: 用户提问
- `actual_response`: AI的实际回答
- `timestamp`: 执行时间
- `model`: 使用的模型

---

### 文件3：评测结果（`results.json`）

**作用**: 记录评测模型的判定（判决书）

**字段**:
- `id`: 用例ID
- `dimension`: 评测维度
- `input`: 用户提问
- `actual_response`: AI的实际回答
- `evaluation_result`: 评测结果（通过/不通过 + 各维度判定）
- `timestamp`: 评测时间
- `evaluator_model`: 评测模型

---

## 📜 历史版本

> **automated_test.py** 已移至 `archive/deprecated-scripts/`
>
> 废弃原因：不支持批次管理和三文件分离架构
>
> 建议使用 `run_tests.py`

---

## 🔧 文档生成器使用指南

> 本文件由 `generate_docs.py` 自动生成，请勿手动修改

---

### 🚀 快速开始

#### 方式1：启用 Git Hook（推荐）

```bash
# 启用 Git Hook
bash tools/setup_git_hooks.sh

# 之后每次 git commit 时会自动检查并更新文档
git add .
git commit -m "update project"
```

**效果**：
- 如果 `.codebuddy/project_data.json` 有变化，会自动运行文档生成器
- 更新后的文档会自动添加到暂存区

---

#### 方式2：手动运行

```bash
# 查看生成的文档内容（不自动替换）
python3 tools/generate_docs.py

# 自动更新所有文档
python3 tools/generate_docs.py --auto-update
```

---

### 📝 使用流程

#### 1. 更新数据源

编辑 `.codebuddy/project_data.json`：

```json
{
  "scripts": [
    {
      "name": "new_script.py",
      "status": "✅",
      "description": "新脚本功能",
      "features": ["功能1", "功能2"],
      "api_integrated": false
    }
  ]
}
```

#### 2. 更新文档

**方式A（自动）**：
```bash
# 如果启用了 Git Hook，直接提交即可
git add .codebuddy/project_data.json
git commit -m "add new script"
# Git Hook 会自动运行文档生成器
```

**方式B（手动）**：
```bash
# 手动运行文档生成器
python3 tools/generate_docs.py --auto-update
```

#### 3. 验证更新

```bash
# 检查文档是否已更新
git status
git diff README.md
```

---

### 🔧 数据源格式

#### scripts 字段

```json
{
  "scripts": [
    {
      "name": "脚本名称.py",           # 必填：脚本文件名
      "status": "✅",                  # 必填：✅ 或 推荐
      "description": "脚本功能描述",   # 必填：简短描述
      "features": [                    # 必填：功能列表
        "功能1",
        "功能2"
      ],
      "api_integrated": true           # 可选：是否集成 API
    }
  ]
}
```

---

### 💡 最佳实践

#### 1. 数据源优先原则

> **"所有项目信息只在一处维护：project_data.json"**

- ✅ 新增脚本 → 先更新 project_data.json
- ✅ 修改描述 → 只修改 project_data.json
- ✅ 然后运行文档生成器

#### 2. Git Hook 可选原则

> **"Git Hook 是可选的便利工具，不是强制要求"**

- 如果团队协作，建议启用 Git Hook
- 如果个人项目，可以手动运行生成器

---

### 🐛 常见问题

#### Q1: Git Hook 没有自动运行？

**检查**：
```bash
# 检查 Git Hook 是否启用
git config --get core.hooksPath

# 应该输出: .githooks
```

**解决**：
```bash
# 重新启用 Git Hook
bash tools/setup_git_hooks.sh
```

---

#### Q2: 文档生成失败？

**检查**：
```bash
# 手动运行文档生成器，查看错误信息
python3 tools/generate_docs.py --auto-update
```

**常见错误**：
- `project_data.json` 格式错误 → 检查 JSON 格式
- 文件权限不足 → `chmod +x tools/generate_docs.py`

---

### 🎯 面试时这样说

> "我的项目采用单一数据源策略，所有项目信息存储在 project_data.json 中，通过文档生成器自动生成多个 README.md。我还实现了 Git Hook，在每次提交前自动检查数据源变化并更新文档，确保文档和代码始终保持同步。这样可以避免手动维护多个文档导致的不一致问题。"

---

### 📝 金句箴言

> **"所有项目信息只在一处维护：project_data.json"**

> **"文档生成器是'单一数据源'思想的体现，让信息只在一处维护。"**

> **"Git Hook 是可选的便利工具，不是强制要求。"**

> **"自动化是为了减少错误，不是为了增加复杂度。"**

---

*最后更新: 2026-04-05*
