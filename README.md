# LLM Testing Portfolio

> 大模型质量保障作品集

---

## 关于我
**技术方向**：大模型测试（Prompt工程、API测试、模型评估、数据处理）

**核心能力**：
- ✅ Prompt工程与评测用例设计
- ✅ Python自动化测试开发
- ✅ 大模型评估指标与A/B测试
- ✅ 评测数据处理与可视化

**联系方式**：
- 技术博客：[掘金主页](https://juejin.cn/user/854784222958441/posts)
- GitHub：[BighuaBighua](https://github.com/BighuaBighua/llm-testing-portfolio.git)

---

## 项目结构

```
llm-testing-portfolio/
├── docs/                           # 项目文档库
│   ├── prompt-engineering-guide.md # Prompt 工程技术方案
│   ├── bad-case-analysis.md        # Bad Case 分析报告
│   ├── test-run-recorder-workflow.md # 测试运行记录工作流程
│   ├── report-interpretation.md    # 测试报告解读指南
│   └── interruption-recovery.md    # 中断恢复指南
├── projects/                       # 项目案例
│   └── 01-ai-customer-service/     # AI 客服系统评测项目
│       ├── cases/                  # 测试用例库
│       │   ├── universal.json      # 通用评测用例
│       │   └── universal.md        # 用例说明文档
│       └── results/                # 测试结果（按批次存储）
│           └── batch-006_2026-04-06/
├── scripts/                        # 自动化脚本
│   ├── run_tests.py               # 主入口：运行测试
│   ├── generate_test_cases.py     # 入口：生成测试用例
│   └── tools/                     # 辅助模块
│       ├── model_config.py        # 配置管理
│       └── record_test_run.py     # 执行记录
├── templates/                      # Prompt 模板库
│   └── customer-service-evaluator.md # AI客服评测器
├── .env.example                    # 环境变量示例
├── requirements.txt                # Python 依赖
├── AI_CODING_RULES.md              # AI 编码规范
├── LICENSE                         # MIT 许可证
└── README.md                       # 本文件
```

---

## 快速开始

### 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/BighuaBighua/llm-testing-portfolio.git
或
git clone https://gitee.com/fangfang007/llm-testing-portfolio

cd llm-testing-portfolio

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的文心一言 API Key
# 如何获取 API Key：
# 1. 访问百度智能云控制台：https://console.bce.baidu.com/qianfan/
# 2. 创建应用，获取 API Key 和 Secret Key
# 3. 将 QIANFAN_AK 和 QIANFAN_SK 替换为你的实际值

# 3. 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 进入项目目录
cd projects/01-ai-customer-service

# 单条执行（健康检查）
python3 ../../scripts/run_tests.py --mode single

# 全量执行（所有用例）
python3 ../../scripts/run_tests.py --mode full

# 增量执行（只执行新用例）
python3 ../../scripts/run_tests.py --mode incremental --batch-id batch-003

# 查看最新测试报告
cat results/batch-*/summary.md
```

---

## 自动化脚本

### run_tests.py ✅ 推荐 已验证

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

---

## Prompt 模板库

### 已验证模板

#### customer-service-evaluator.md

**场景**: AI 客服系统合规评测

**核心设计**:
- 角色锚定: 电商 AI 客服系统合规评测工程师
- 评测维度: 服务范围 / 服务态度 / 内容真实性
- 输出格式: 固定结构，支持脚本解析

**使用方法**:
```bash
cd ../scripts
python run_tests.py  # 运行测试用例
```

### 模板设计原则

1. **规则刚性化**: 可量化、无歧义、非黑即白
2. **Few-shot 单测点**: 每个示例只覆盖一个规则点
3. **格式统一**: 示例格式 = 输出格式，支持脚本解析
4. **CoT 强制校验**: 多规则场景必须分步校验

---

## 文档库

### 核心技术文档

- [Prompt 工程技术方案](./docs/prompt-engineering-guide.md) - AI 评测场景下的 Prompt 设计方法论
- [学习路线图](./docs/roadmap.md) - 8-12 周学习规划

### 架构设计

- [TestRunRecorder 工作流程](./docs/architecture/test-run-recorder-workflow.md) - 测试运行审计和追溯模块

### 技术分析

- [Bad Case 分析报告](./docs/technical-analysis/bad-case-analysis.md) - 失败用例深度分析
- [Few-shot 设计分析](./docs/technical-analysis/fewshot-design-analysis.md) - Few-shot 示例设计思路
- [测试用例版本管理逻辑](./docs/technical-analysis/test-case-version-management-logic.md) - 版本管理方案

### 使用指南

- [测试报告解读指南](./docs/user-guide/report-interpretation.md) - 如何理解测试报告
- [中断恢复指南](./docs/user-guide/interruption-recovery.md) - 测试中断后的恢复策略

### 文档价值说明

**面试官最关心的文档**：
1. ⭐⭐⭐⭐⭐ Prompt 工程技术方案 - 展示核心能力
2. ⭐⭐⭐⭐⭐ 架构设计 - 展示系统设计思维
3. ⭐⭐⭐⭐ 技术分析 - 展示问题分析能力

**用户最关心的文档**：
- 使用指南 - 如何使用项目

---

## 可复用性

### 模板迁移

当前模板可直接应用于：

| 场景 | 迁移成本 | 验证状态 |
|------|---------|---------|
| 内容审核 | 低（修改规则部分） | 📅 待验证 |
| 对话质量评估 | 中（增加评分维度） | 📅 待验证 |
| 幻觉检测 | 低（替换知识库部分） | 📅 待验证 |

### 工具开源

- ✅ 自动化评测脚本：`scripts/run_tests.py`（推荐）
- ✅ CoT 对比脚本：`scripts/compare_cot_methods.py`
- ✅ Prompt 模板库：`templates/`

---

## 三文件分离架构

### 文件1：测试用例模板（`universal.json`）

**作用**: 记录测试意图

**字段**:
- `id`: 用例ID
- `dimension`: 评测维度
- `input`: 用户提问
- `test_purpose`: 测试目的
- `quality_criteria`: 质量标准

### 文件2：执行记录（`records.json`）

**作用**: 记录AI的实际回答（证据）

**字段**:
- `id`: 用例ID
- `input`: 用户提问
- `actual_response`: AI的实际回答
- `timestamp`: 执行时间
- `model`: 使用的模型

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

## Bad Case 分析

> **注**: 当前测试用例均通过，暂无失败案例。  
> **待补充**: 扩充用例后，整理典型失败案例及优化方案。

---

## 下一步计划

| 优先级 | 任务 | 预计时间 |
|--------|------|---------|
| 🔥 高 | 收集 Bad Case 并分析 | 本周 |
| 🔶 中 | 优化 Prompt 模板 | 下周 |
| 🔶 中 | 扩展到其他评测场景 | 下周 |
| 📅 低 | 开发 Web 可视化界面 | 后续 |

---

## 许可证

本项目采用 MIT 许可证 - 详情见 [LICENSE](LICENSE) 文件。

---

*项目开始时间: 2026-03-25*  
*最后更新: 2026-04-06*  
*如果这个作品集对你有帮助，欢迎 Star ⭐*
