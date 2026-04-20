# LLM Testing Portfolio

> 大模型质量保障作品集 — 自动化评测框架，解决 AI 输出概率性带来的测试难题

---

## 关于我

**技术方向**：大模型测试（Prompt工程、API测试、模型评估、数据处理）

**核心能力**：
- Prompt工程与评测用例设计
- Python自动化测试开发
- 大模型评估指标与A/B测试
- 评测数据处理与可视化

**联系方式**：
- 技术博客：[掘金主页](https://juejin.cn/user/854784222958441/posts)
- GitHub：[BighuaBighua](https://github.com/BighuaBighua/llm-testing-portfolio.git)

---

## 项目定位

**核心问题**：AI 输出是概率性的，无法像传统测试那样对比预期结果。

```
传统测试: 输入 → 确定性输出 → 对比预期结果 → 通过/失败
AI 测试:  输入 → 概率性输出 → 评测判定     → 判定结果（有灰度）
```

**解决方案**：通过**三文件分离架构**将非结构化对话转化为可量化、可追溯的工程化资产。

**技术关注点**：

| 关注点 | 本项目体现 | 代码位置 |
|--------|-----------|---------|
| Prompt工程能力 | 模块化模板架构 + 12维度评测Prompt + 动态组装 | `templates/`, `evaluation.py` |
| 架构设计能力 | 三文件分离 + ConfigRegistry + EvaluationContext + 项目级/共享层模板分离 | `config.py`, `execution.py` |
| 工程化能力 | 全流程自动化 + 批次管理 + 审计报告 + Bad Case管理 + 项目脚手架 | `run_tests.py`, `reporting.py`, `init_project.py` |
| 安全测试能力 | Prompt注入攻击5类手法 + 敏感话题6类+4种绕过 + 偏见公平性6类 + 统一安全路由 | `prompt-injection-rules.md`, `sensitive-topic-rules.md`, `bias-fairness-rules.md`, `SecurityStatsGenerator` |
| 可扩展性 | 多项目支持 + 多场景切换(通用/银行/电商) + YAML配置外置 + 项目脚手架 | `business_rules.yaml`, `ConfigRegistry`, `init_project.py` |

---

## 项目结构

```
llm-testing-portfolio/
├── configs/                              # 配置中心（4个YAML）
│   ├── api_config.yaml                   # API密钥（不提交Git，三模型独立配置）
│   ├── api_config_example.yaml           # API密钥模板（占位符）
│   ├── business_rules.yaml              # 业务规则与场景定义
│   ├── execution.yaml                    # 执行参数配置
│   └── test_generation.yaml             # 用例生成配置（12维度）
├── scripts/                              # 自动化脚本
│   ├── generate_test_cases.py            # 入口1：用例生成
│   ├── run_tests.py                      # 入口2：测试执行（V3.1）
│   ├── init_project.py                   # 入口3：项目脚手架
│   └── tools/                            # 工具模块（8个）
│       ├── config.py                     # 配置管理（核心枢纽，含项目级路径管理）
│       ├── evaluation.py                 # 评测逻辑（Prompt组装/解析/独立性策略）
│       ├── execution.py                  # 执行记录（运行记录器）
│       ├── reporting.py                  # 报告生成（BadCase/Bug/CSV/安全统计/安全报告）
│       ├── prompt_template.py            # 模板加载（变量渲染+缓存）
│       ├── under_test_prompt_assembler.py # 被测Prompt组装
│       ├── split_evaluator_template.py   # 评测模板拆分工具
│       └── utils.py                      # 通用工具（异常体系+日志+IO）
├── templates/                            # Prompt模板库（共享层+模块化架构）
│   ├── customer-service-evaluator.md     # 评测器完整模板
│   ├── evaluator-prompts/                # 评测Prompt外壳模板
│   │   ├── standard.md                   # 标准单轮评测
│   │   └── multi-turn.md                 # 多轮评测
│   ├── evaluator-sections/               # 共享层评测片段（安全维度+通用片段，10个）
│   │   ├── auto_enhance.md               # 自动增强机制
│   │   ├── bias-fairness-rules.md        # 偏见公平性评测规则（共享层）
│   │   ├── constraints.md                # 强制约束
│   │   ├── design.md                     # 设计要点
│   │   ├── multi-dimension-focus.md      # 高级维度焦点
│   │   ├── multi-turn-focus.md           # 多轮焦点提示
│   │   ├── multi_turn.md                 # 多轮4子任务拆解
│   │   ├── output.md                     # 3种输出格式定义
│   │   ├── prompt-injection-rules.md     # Prompt注入规则（共享层）
│   │   └── sensitive-topic-rules.md      # 敏感话题评测规则（共享层）
│   ├── generation/                       # 用例生成模板
│   │   ├── standard.md                   # 标准维度生成
│   │   ├── multi-turn.md                 # 多轮对话生成
│   │   ├── prompt-injection.md           # Prompt注入生成
│   │   ├── sensitive-topic.md            # 敏感话题生成
│   │   └── bias-fairness.md              # 偏见公平性生成
│   └── under-test/                       # 被测模型Prompt模板
│       ├── single-turn.md                # 单轮对话
│       └── multi-turn-system.md          # 多轮System Prompt
├── projects/                             # 项目案例（多项目支持）
│   ├── 01-ai-customer-service/           # AI客服评测项目
│   │   ├── project_config.yaml           # 项目配置（模板参数+业务场景）
│   │   ├── evaluator-sections/           # 项目级评测片段（覆盖共享层）
│   │   │   ├── role.md                   # 角色定义
│   │   │   ├── rules.md                  # 判定规则
│   │   │   ├── example.md                # 评测示例
│   │   │   ├── fewshot.md                # Few-shot示例
│   │   │   ├── portability.md            # 场景迁移对照
│   │   │   └── prompt-injection-rules.md # Prompt注入规则（项目级覆盖）
│   │   ├── cases/                        # 测试用例库
│   │   │   ├── universal.json            # 通用评测用例（含metadata）
│   │   │   ├── universal.md              # 用例说明文档
│   │   │   ├── universal.csv             # CSV格式
│   │   │   └── bad_cases/                # Bad Case沉淀库
│   │   └── results/                      # 测试结果（按批次存储）
│   │       └── batch-016_2026-04-13/     # 示例批次
│   └── 02-chat-companion/                # 聊天助手评测项目
│       ├── project_config.yaml           # 项目配置
│       └── evaluator-sections/           # 项目级评测片段
│           ├── role.md
│           ├── rules.md
│           ├── fewshot.md
│           └── prompt-injection-rules.md
├── knowledge-base/                       # 项目知识库
│   ├── 01-架构设计/                      # 架构设计文档
│   ├── 02-技术实现/                      # 技术实现文档
│   ├── 03-使用指南/                      # 使用指南文档
│   └── 04-最佳实践/                      # 最佳实践文档
├── requirements.txt                      # Python依赖
├── LICENSE                               # MIT许可证
└── README.md                             # 本文件
```

---

## 核心架构：三文件分离

**核心洞察**：AI 输出是概率性的，测试用例**不包含预期结果**——这是与传统测试的根本差异。

```
时间轴:  ───────────→ before ── during ── after ── summary ──→

文件1: universal.json (意图/before)
  - 内容: 用户输入 + 测试目的 + 质量标准
  - 特点: 不含预期结果（AI输出是概率性的）
  - 作用: 定义"我们要测什么"

文件2: records.json (证据/during)
  - 内容: AI的实际回答（原始输出）
  - 特点: 忠实记录，不做任何加工
  - 作用: 提供可审计的证据链

文件3: results.json (判决/after)
  - 内容: 评测模型的判定（通过/不通过 + 违规说明）
  - 特点: 由独立评测模型给出，有灰度
  - 作用: 给出质量裁决
```

| 文件 | 作用 | 关键字段 |
|------|------|---------|
| `universal.json` | 测试用例模板（测试意图） | id, dimension, input, test_purpose, quality_criteria |
| `records.json` | 执行记录（AI实际回答/证据） | id, input, actual_response, timestamp, model |
| `results.json` | 评测结果（判定/判决书） | id, dimension, evaluation_result, evaluator_model |

**核心价值**：
- **可追溯**：任何判定都能回溯到原始证据
- **可复现**：相同用例 + 相同模型 = 可复现的结果
- **可对比**：不同批次间可横向对比模型表现变化

---

## 数据流与两阶段调用

```
                    ┌─────────────────────┐
                    │  configs/           │
                    │  (YAML配置中心)      │
                    └──────────┬──────────┘
                               │ 加载配置
                               ▼
┌──────────────────┐   ┌───────────────────┐   ┌──────────────────┐
│ generate_test_   │──▶│ TestCaseGenerator  │──▶│ universal.json   │
│ cases.py         │   │ (用例生成器)        │   │ (测试用例库)      │
└──────────────────┘   └───────────────────┘   └────────┬─────────┘
                                                         │ 加载用例
                                                         ▼
┌──────────────────┐   ┌───────────────────┐   ┌──────────────────┐
│ run_tests.py     │──▶│ TestRunner         │──▶│ results/         │
│ (测试执行入口)    │   │ (测试执行器V3.1)    │   │ batch-XXX/       │
└──────────────────┘   └───────────────────┘   │  ├ records.json  │
                                │               │  ├ results.json  │
                    ┌───────────┤               │  ├ summary.md    │
                    │           │               │  ├ bug_list.*    │
                    ▼           ▼               │  ├ audit_report  │
           ┌────────────┐ ┌────────────┐       │  ├ evaluation_*  │
           │ 被测模型    │ │ 评测模型    │       │  └ bypass_stats  │
           │ (千帆API)  │ │ (多Provider)│       └──────────────────┘
           └────────────┘ └────────────┘
```

**两阶段调用流程**：
1. **阶段1**：调用被测模型（千帆）获取 AI 回答
2. **阶段2**：调用评测模型（DashScope/ModelScope/千帆兜底）评测回答质量

**三模型独立配置**：case_generator（用例生成）→ model_under_test（被测模型）→ evaluator（评测模型），各模型独立配置API和fallback

**评测Provider优先级**：DashScope (qwen-turbo) → ModelScope (Qwen3.5-35B-A3B) → 千帆 (ernie-4.5-turbo-128k，兜底)

---

## 模块设计详解

### 配置管理模块 (`scripts/tools/config.py`)

配置中心是整个框架的核心枢纽，采用**依赖注入 + 单例 + 门面**模式，支持多项目路径管理。

| 类 | 职责 | 设计模式 |
|----|------|---------|
| `ConfigLoader` | YAML配置文件加载器，带缓存和fallback | 缓存+策略模式 |
| `ConfigRegistry` | 配置注册中心，不可变单例（`__setattr__`冻结） | 依赖注入+单例模式 |
| `EvaluationContext` | 评测上下文，场景信息持久化与传递（含fingerprint校验） | 嵌入式元数据模式 |
| `ConfigManager` | 统一配置管理器，整合Loader和Registry | 门面模式 |

**关键常量**：
- `MODEL_UNDER_TEST = "ernie-4.5-turbo-128k"`（被测模型）
- `EVALUATOR_MODEL = "qwen-turbo"`（评测模型）
- `SECURITY_DIMENSIONS = {"prompt_injection", "sensitive_topic", "bias_fairness"}`（安全维度集合）
- `DEFAULT_PROJECT = "01-ai-customer-service"`（默认项目）

**项目级路径管理**：`set_current_project()`, `get_current_project()`, `get_project_dir()`, `get_project_cases_dir()`, `ensure_project_dirs()`

**便捷函数**（统一访问接口）：`get_api_config()`, `get_api_key(service)`, `get_business_rules()`, `get_test_generation_config()`, `get_evaluation_dimensions()`, `get_dimension_names()`, `get_evaluator_providers()`, `get_model_under_test()`, `get_execution_config()`, `get_test_cases_path()`, `get_evaluator_template_path()`, `get_results_dir()`, `get_evaluator_config()`, `get_model_under_test_config()`

### 评测模块 (`scripts/tools/evaluation.py`)

评测模块负责Prompt动态组装、响应解析和独立性保障。

| 类 | 职责 |
|----|------|
| `IndependencePolicy` | 枚举类，定义 strict/warn/relaxed 三种独立性策略 |
| `EvaluatorPolicy` | 评测独立性策略检查器（默认strict：被测模型与评测模型必须不同） |
| `EvaluationParser` | 统一评测响应解析器（3层解析：结构化格式 → 关键词匹配 → 正则兜底） |
| `EvaluatorPromptAssembler` | 评测Prompt动态组装器（按维度从evaluator-sections/加载片段） |

**Prompt动态组装流程**：
1. 从 `evaluator-sections/` 按维度加载所需片段（role, rules, output, fewshot等）
2. 注入场景信息（从 `EvaluationContext` 恢复）
3. 填入待评测的用户输入和AI回答
4. 请求评测模型输出判定

**EvaluationParser 3层解析策略**：
- 结构化格式：`【用例ID】-【测试结果:通过/不通过】`
- 关键词匹配：通过/不通过/防御成功/绕过成功
- 正则兜底：提取各维度判定结果

### 执行记录模块 (`scripts/tools/execution.py`)

| 类 | 职责 |
|----|------|
| `TestRunRecorder` | 测试运行记录器 |

**核心功能**：
- 配置基线管理：`create_test_config` / `load_test_config` / `update_test_config`
- 执行日志管理：`start_logging` / `log_case_start` / `log_case_complete` / `end_logging`
- 完整性验证：`validate_coverage` / `validate_consistency` / `validate_config_integrity`
- 异常检测：`check_version_compatibility` / `detect_interruption`
- 断点续传：`get_last_completed_case`
- 审计报告：`generate_audit_report` / `save_audit_report`

### 报告模块 (`scripts/tools/reporting.py`)

| 类 | 职责 |
|----|------|
| `BadCaseManager` | Bad Case管理器（提取/去重/累积/状态流转/多格式输出） |
| `BugListGenerator` | Bug清单生成器（Markdown+JSON，含复现步骤和环境信息） |
| `SecurityStatsGenerator` | 安全维度统一统计生成器（Prompt注入+敏感话题+偏见公平性） |
| `BypassStatsGenerator` | 绕过成功率统计工具（已弃用，组合为SecurityStatsGenerator） |
| `SecurityReportGenerator` | 安全专项总报告生成器（总体评估+维度详情+风险评级+建议） |
| `EvaluationCSVExporter` | 评测结果CSV导出工具（明细CSV+统计汇总CSV） |

**Bad Case 严重程度**：P0（合规性不通过/绕过成功）、P1（其他不通过）

**Bad Case 状态流转**：open → fixed → verified → closed

### 用例生成模块 (`scripts/generate_test_cases.py`)

**类**：`TestCaseGenerator`

**12个评测维度**：

| 维度 | 代码 | 中文名 | 类型 | 每维度用例数 |
|------|------|--------|------|------------|
| accuracy | ACC | 准确性 | 基础 | 10 |
| completeness | CMP | 完整性 | 基础 | 10 |
| compliance | CPM | 合规性 | 基础 | 10 |
| attitude | ATT | 态度 | 基础 | 10 |
| multi | MUL | 多维度 | 基础 | 10 |
| boundary | BOU | 边界场景 | 高级 | 10 |
| conflict | CFL | 多维度冲突 | 高级 | 10 |
| induction | IND | 诱导场景 | 高级 | 10 |
| multi_turn | MTD | 多轮对话 | 高级 | 10（10种场景各1条） |
| prompt_injection | PIN | Prompt注入攻击 | 安全 | 10（5种攻击手法各2条） |
| sensitive_topic | STP | 敏感话题安全防御 | 安全 | 30（6类话题×5条，含4种绕过手法） |
| bias_fairness | BFN | 偏见公平性 | 安全 | 30（6类偏见×5条） |

**用例ID格式**：`TC-{维度代码}-{序号}`，如 `TC-ACC-001`

**输出格式**：universal.json（带metadata和changelog）+ universal.md + universal.csv

### 测试执行模块 (`scripts/run_tests.py`)

**类**：`TestRunner`（V3.1）

**核心特性**：
- EvaluatorPromptAssembler 动态组装评测Prompt
- EvaluationParser 多策略解析评测响应
- EvaluatorPolicy 评测独立性保障（strict/warn/relaxed）
- 安全维度统一路由（prompt_injection → 防御成功/绕过成功，sensitive_topic → 拦截成功/拦截失败/误拦截，bias_fairness → 无偏见/隐性偏见/显性偏见）
- ConfigRegistry 配置中心集成
- SecurityStatsGenerator + SecurityReportGenerator 安全统计与报告
- 多项目支持（`--project` 参数）
- BadCaseManager 集成（含根因分析、状态流转）

### 其他模块

| 模块 | 类/函数 | 职责 |
|------|---------|------|
| `prompt_template.py` | `PromptTemplateLoader` | 从templates/加载.md模板，`{{variable}}`变量渲染，实例级缓存 |
| `under_test_prompt_assembler.py` | `UnderTestPromptAssembler` | 组装被测模型Prompt（单轮返回字符串，多轮返回messages列表） |
| `split_evaluator_template.py` | `split_template()` | 将完整评测模板按SECTION标记拆分为独立片段文件 |
| `utils.py` | 异常体系 + 辅助函数 | 7个异常类（TestingFrameworkError为基类）+ 11个辅助函数（含日志管理） |

**异常类体系**：
```
TestingFrameworkError (基础异常)
├── ConfigError (配置错误)
├── ExecutionError (执行错误)
├── EvaluationError (评测错误)
├── APIError (API调用错误)
├── ValidationError (数据验证错误)
└── ReportingError (报告生成错误)
```

---

## 关键设计决策

### 1. 评测独立性保障

**问题**：被测模型与评测模型相同时，评测结果不可信

**方案**：`EvaluatorPolicy` + `IndependencePolicy` 三级策略
- strict（默认）：被测模型与评测模型必须不同，否则抛异常
- warn：允许相同但发出警告
- relaxed：允许相同且不警告

### 2. EvaluationContext 场景传递

**问题**：用例生成脚本与评测脚本之间的场景参数传递断裂

**方案**：将场景信息嵌入测试用例元数据（`_evaluation_context` 字段），评测时自动恢复。包含场景指纹（fingerprint）用于校验用例生成与评测使用相同场景。

### 3. 评测Prompt动态组装

**问题**：将所有维度规则塞入同一个超长Prompt浪费Token

**方案**：模块化片段按需组装
1. 从 `evaluator-sections/` 按维度加载所需片段
2. 注入场景信息（从 `EvaluationContext` 恢复）
3. 填入待评测内容，请求评测

不同维度的组装顺序在 `test_generation.yaml` 的 `evaluation_settings` 中配置。

### 4. 多轮对话4子任务评测

**问题**：多轮对话评测复杂，单次判定容易遗漏

**方案**：固定4子任务分步校验
1. 逐轮单轮质量校验（4大维度）
2. 上下文一致性校验（矛盾/遗忘/幻觉）
3. 指令坚守性校验（是非判断：守了/没守）
4. 规则稳定性校验（趋势判断：稳/不稳）

### 5. Prompt注入攻击维度路由

**问题**：Prompt注入攻击的评测逻辑与标准维度完全不同

**方案**：独立路由，结果为"防御成功/绕过成功"而非"通过/不通过"，额外统计绕过成功率

### 6. 安全维度统一路由

**问题**：3个安全维度（Prompt注入、敏感话题、偏见公平性）各有不同的判定逻辑和输出格式

**方案**：统一安全路由机制，每个安全维度有独立的判定结果和统计方式
- `prompt_injection`：防御成功/绕过成功（指令层安全）
- `sensitive_topic`：拦截成功/拦截失败/误拦截（内容层安全）
- `bias_fairness`：无偏见/隐性偏见/显性偏见（内容层公平）

安全维度共享 `SECURITY_DIMENSIONS` 常量，统一由 `SecurityStatsGenerator` 统计 + `SecurityReportGenerator` 生成安全专项报告。

### 7. 项目级/共享层模板分离

**问题**：不同项目需要不同的角色定义和判定规则，但安全维度规则应统一维护

**方案**：双层模板架构
- **共享层**（`templates/evaluator-sections/`）：安全维度规则 + 通用片段，所有项目共享
- **项目层**（`projects/{name}/evaluator-sections/`）：角色定义、判定规则、Few-shot等，按项目定制

项目层片段优先加载，缺失时回退到共享层。安全维度规则（prompt-injection-rules、sensitive-topic-rules、bias-fairness-rules）由共享层统一提供，变量参数从 `project_config.yaml` 自动注入。

---

## 配置系统

### 配置文件说明

| 文件 | 职责 | 关键配置项 |
|------|------|-----------|
| `api_config.yaml` | API密钥（**不提交Git**，三模型独立配置） | case_generator(ak/sk+fallback), model_under_test(ak/sk), evaluator(api_key+fallback) |
| `api_config_example.yaml` | API密钥模板（占位符） | 同上，值为 YOUR_XXX_HERE |
| `business_rules.yaml` | 业务规则与场景定义 | active_scenario, scenarios, constraints, compliance_rules |
| `execution.yaml` | 执行参数配置 | concurrency(3种模式), parameters, quality_gate, performance_monitoring |
| `test_generation.yaml` | 用例生成配置 | dimensions(12个), dimension_groups, generation_settings, multi_turn_scenarios(10个), evaluation_settings |

### 安全配置机制

项目采用双重配置文件机制确保 API 密钥安全：

- **示例模板** (`api_config_example.yaml`)：包含占位符，可安全提交到 Git
- **实际配置** (`api_config.yaml`)：包含真实密钥，被 `.gitignore` 保护

### 配置加载优先级

1. 优先加载 `configs/api_config.yaml`（实际配置，包含真实密钥）
2. 如果不存在，加载 `configs/api_config_example.yaml`（示例模板，占位符）
3. 如果都不存在，使用硬编码默认值

### 业务场景切换

通过 `business_rules.yaml` 的 `active_scenario` 切换场景：default(通用客服) / bank(银行客服) / ecommerce(电商客服)

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
cp configs/api_config_example.yaml configs/api_config.yaml
# 编辑 configs/api_config.yaml 文件，填入你的 API 密钥

# 3. 安装依赖
pip install -r requirements.txt
```

### 如何配置 API Key

1. **复制配置模板**：`cp configs/api_config_example.yaml configs/api_config.yaml`
2. **编辑本地配置**：在 `configs/api_config.yaml` 文件中，将占位符替换为你的实际 API 密钥：
   - `case_generator.ak/sk`: 百度千帆 Access/Secret Key（用例生成模型）
   - `case_generator.fallback.providers[].api_key`: 阿里云 DashScope API Key（用例生成备用）
   - `model_under_test.ak/sk`: 百度千帆 Access/Secret Key（被测模型）
   - `evaluator.api_key`: 阿里云 DashScope API Key（评测模型）
   - `evaluator.fallback.providers[].api_key`: 魔搭社区/百度千帆 API Key（评测备用）

3. **获取 API Key**：
   - **百度千帆**：访问 [百度智能云控制台](https://console.bce.baidu.com/qianfan/)
   - **阿里云 DashScope**：访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
   - **魔搭社区**：访问 [魔搭社区控制台](https://modelscope.cn/)

**安全提示**：`configs/api_config.yaml` 文件已被 `.gitignore` 保护，不会被提交到版本控制系统。

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

# 指定项目执行（无需进入项目目录）
python3 scripts/run_tests.py --mode full --project 02-chat-companion

# 查看最新测试报告
cat results/batch-*/summary.md
```

### 创建新项目

```bash
# 使用项目脚手架创建新项目
python3 scripts/init_project.py --name 03-medical-assistant --display "医疗助手"

# 创建后编辑项目配置
# 1. 编辑 projects/03-medical-assistant/project_config.yaml
# 2. 编辑 projects/03-medical-assistant/evaluator-sections/ 下的评测规则
# 3. 运行测试: python3 scripts/run_tests.py --mode full --project 03-medical-assistant
```

---

## 命令行参考

### run_tests.py — 测试执行

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--mode` | 执行模式 | `full` | `single` `selected` `incremental` `full` |
| `--cases` | 指定用例ID（多选用逗号分隔） | `None` | 如: `TC-ACC-001,TC-COM-002` |
| `--report` | 报告输出模式 | `new` | `new` `append` `update` |
| `--batch-id` | 批次ID（用于增量/追加/更新/仅生成报告） | `None` | 如: `batch-003` |
| `--report-only` | 仅重新生成报告（不执行测试） | `False` | 独立标志，直接添加即可 |
| `--concurrent` | 并发数（0=单线程） | `0` | 建议不超过 `2` |
| `--project` | 项目名称 | `None`（默认01-ai-customer-service） | 如: `01-ai-customer-service`, `02-chat-companion` |

**执行模式**：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `single` | 执行第1条用例 | 健康检查、快速验证API连通性 |
| `selected` | 执行指定ID的用例 | 重新测试特定用例、调试 |
| `incremental` | 只执行未执行的用例 | 持续测试、避免重复执行 |
| `full` | 执行所有用例 | 完整测试、回归测试 |

**报告输出模式**：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `new` | 创建新批次目录 | 首次测试、新版本测试 |
| `append` | 追加结果到现有批次 | 增量测试、补充测试 |
| `update` | 重新生成批次报告 | 报告损坏、需要重新汇总 |
| `--report-only` | 仅重新生成报告（不执行测试） | 报告损坏、格式调整 |

**使用示例**：

```bash
# 健康检查
python3 ../../scripts/run_tests.py --mode single

# 指定用例执行
python3 ../../scripts/run_tests.py --mode selected --cases TC-ACC-001,TC-COM-002

# 增量执行
python3 ../../scripts/run_tests.py --mode incremental --batch-id batch-003

# 全量执行
python3 ../../scripts/run_tests.py --mode full

# 新建测试批次
python3 ../../scripts/run_tests.py --mode full --report new

# 追加测试结果到现有批次
python3 ../../scripts/run_tests.py --mode incremental --report append --batch-id batch-003

# 更新现有批次报告
python3 ../../scripts/run_tests.py --mode full --report update --batch-id batch-003

# 仅重新生成报告（不执行测试）
python3 ../../scripts/run_tests.py --report-only --batch-id batch-004

# 并发执行（注意API QPS限制）
python3 ../../scripts/run_tests.py --mode full --concurrent 2

# 指定项目执行
python3 ../../scripts/run_tests.py --mode full --project 02-chat-companion
```

### generate_test_cases.py — 用例生成

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--dimensions` | 指定要生成的维度（逗号分隔） | `None`（所有维度） | 如: `boundary,conflict,induction` |
| `--append` | 追加模式（有则追加，无则新建） | `False`（覆盖模式） | 独立标志，直接添加即可 |
| `--scenario` | 行业场景 | `None`（使用配置默认） | `default` `bank` `ecommerce` 等 |

**使用示例**：

```bash
# 生成所有维度用例（默认）
python3 scripts/generate_test_cases.py

# 生成指定维度用例
python3 scripts/generate_test_cases.py --dimensions boundary,conflict,induction

# 追加模式（自动判断：有则追加，无则新建）
python3 scripts/generate_test_cases.py --append

# 指定行业场景生成
python3 scripts/generate_test_cases.py --scenario bank

# 生成多轮对话用例并追加
python3 scripts/generate_test_cases.py --dimensions multi_turn --append
```

**维度列表**：

| 维度 | 代码 | 说明 | 类型 |
|------|------|------|------|
| `accuracy` | ACC | 准确性 | 基础 |
| `completeness` | CMP | 完整性 | 基础 |
| `compliance` | CPM | 合规性 | 基础 |
| `attitude` | ATT | 态度 | 基础 |
| `multi` | MUL | 多维度组合 | 基础 |
| `boundary` | BOU | 边界场景（模糊问题、越界请求） | 高级 |
| `conflict` | CFL | 多维度冲突（准确性vs态度、完整性vs合规性） | 高级 |
| `induction` | IND | 诱导场景（诱导说谎、诱导提供专业建议） | 高级 |
| `multi_turn` | MTD | 多轮对话（10种场景，3-6轮对话） | 高级 |
| `prompt_injection` | PIN | Prompt注入攻击（5种攻击手法） | 安全 |
| `sensitive_topic` | STP | 敏感话题安全防御（6类话题+4种绕过手法） | 安全 |
| `bias_fairness` | BFN | 偏见公平性（6类偏见：性别/地域/职业/年龄/外貌/学历） | 安全 |

**多轮对话10种场景**：

| 场景 | 说明 | 对话轮数 |
|------|------|----------|
| 渐进式需求澄清 | 用户需求模糊，AI逐步引导澄清 | 3-4轮 |
| 上下文追问链 | 用户对同一主题层层追问 | 3-4轮 |
| 信息提交与修改 | 用户提供信息后中途修改 | 4-5轮 |
| 纠错澄清 | AI误解用户意图，用户澄清 | 3-4轮 |
| 跨主题切换 | 用户跳跃式提问不同主题 | 4-6轮 |
| 条件筛选 | 用户逐步添加筛选条件 | 4-6轮 |
| 方案比较 | 用户对比多个方案，逐步深入 | 4-5轮 |
| 问题诊断 | AI通过逐步询问诊断问题原因 | 4-5轮 |
| 流程指导 | 用户逐步学习某个操作流程 | 3-5轮 |
| 记忆验证 | 用户测试AI是否记住前文信息 | 3-4轮 |

**Prompt注入5种攻击手法**：指令忽略型、指令覆盖型、角色劫持型、系统Prompt泄露型、间接诱导型

**敏感话题6类话题**：违法违规类、色情低俗类、偏见歧视类、暴力血腥类、敏感政治类、隐私泄露类

**敏感话题4种绕过手法**：谐音绕过、暗语绕过、委婉诱导绕过、上下文嵌套绕过

**偏见公平性6类偏见**：性别偏见、地域偏见、职业偏见、年龄偏见、外貌偏见、学历偏见

### init_project.py — 项目脚手架

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `--name` | 项目目录名称（必填） | 无 | 如: `03-medical-assistant` |
| `--display` | 项目显示名称 | 同name | 如: `医疗助手` |

**使用示例**：

```bash
# 创建新项目
python3 scripts/init_project.py --name 03-medical-assistant --display "医疗助手"

# 创建后目录结构
# projects/03-medical-assistant/
# ├── project_config.yaml          # 项目配置（模板参数+业务场景）
# ├── evaluator-sections/          # 项目级评测片段
# │   ├── role.md
# │   ├── rules.md
# │   ├── example.md
# │   ├── fewshot.md
# │   ├── portability.md
# │   ├── prompt-injection-rules.md
# │   ├── sensitive-topic-rules.md
# │   └── bias-fairness-rules.md
# ├── cases/                       # 测试用例目录
# │   └── bad_cases/
# └── results/                     # 测试结果目录
```

---

## 模板库设计

### 模板架构

评测器模板采用**双层模块化片段**架构，通过 `<!-- SECTION:xxx -->` 标记将完整模板拆分为独立片段：

```
templates/evaluator-sections/ (共享层，10个片段)
    ├── 安全维度规则（所有项目共享，变量从project_config.yaml注入）
    │   ├── prompt-injection-rules.md  → Prompt注入攻击规则
    │   ├── sensitive-topic-rules.md   → 敏感话题安全防御规则
    │   └── bias-fairness-rules.md     → 偏见公平性规则
    └── 通用片段
        ├── constraints.md   → 强制约束
        ├── output.md        → 输出格式定义
        ├── multi_turn.md    → 多轮4子任务拆解
        └── ...

projects/{name}/evaluator-sections/ (项目层，按项目定制)
    ├── role.md             → 角色定义（项目特定）
    ├── rules.md            → 判定规则（项目特定）
    ├── example.md          → 评测示例（项目特定）
    ├── fewshot.md          → Few-shot示例（项目特定）
    └── prompt-injection-rules.md → 项目级覆盖（可选）
```

**加载优先级**：项目层片段 → 共享层片段（项目层缺失时回退）

**按需组装**：`EvaluatorPromptAssembler` 根据评测维度，从片段中选取所需部分动态组装，避免浪费Token。安全维度规则从共享层加载，变量参数（如 `{{agent_name}}`、`{{service_identity}}`）从 `project_config.yaml` 自动注入。

### 模板设计原则

1. **规则刚性化**：可量化、无歧义、非黑即白
2. **Few-shot 单测点**：每个示例只覆盖一个规则点
3. **格式统一**：示例格式 = 输出格式，支持脚本解析
4. **CoT 强制校验**：多规则场景必须分步校验

### 5种输出格式

| 类型 | 格式 | 适用维度 |
|------|------|---------|
| 单轮 | `【用例ID】-【测试结果:通过/不通过】` + 4维度推理 | accuracy/completeness/compliance/attitude/multi/boundary/conflict/induction |
| 多轮 | 4子任务分步校验（逐轮→一致性→坚守性→稳定性） | multi_turn |
| Prompt注入 | `【用例ID】-【测试结果:防御成功/绕过成功】` + 绕过类型 | prompt_injection |
| 敏感话题 | `【用例ID】-【测试结果:拦截成功/拦截失败/误拦截】` + 话题类型+绕过手法 | sensitive_topic |
| 偏见公平性 | `【用例ID】-【测试结果:无偏见/隐性偏见/显性偏见】` + 偏见类型+刻板印象检测 | bias_fairness |

---

## 批次结果文件

按批次存储，目录名格式：`batch-{序号}_{日期}`

| 文件 | 说明 |
|------|------|
| `test_config.json` | 测试配置基线（环境、参数、质量门禁） |
| `test_execution.log` | 执行日志（用例级记录） |
| `records.json` | 执行记录（AI实际回答） |
| `results.json` | 评测结果（判定详情，含security_detail字段） |
| `summary.md` | 测试报告（人类可读） |
| `bug_list.md/json` | Bug清单（不通过用例） |
| `audit_report.md` | 审计报告（完整性检查） |
| `evaluation_detail.csv` | 评测明细CSV |
| `evaluation_summary.csv` | 统计汇总CSV |
| `bypass_stats_report.md` | 绕过成功率统计 |
| `security_report.md` | 安全专项测试报告（3维度统一评估+风险评级） |

---

## API 提供商

| 提供商 | 用途 | 模型 | API协议 |
|--------|------|------|---------|
| 百度千帆 | 用例生成模型 + 被测模型（主要）+ 评测兜底 | ernie-4.5-turbo-128k | OpenAI兼容 |
| 阿里云DashScope | 评测模型（主力）+ 用例生成备用 | qwen-turbo | OpenAI兼容 |
| 魔搭社区 | 评测模型（后备） | Qwen3.5-35B-A3B | OpenAI兼容 |

**三模型独立配置**：
- `case_generator`：用例生成模型（千帆 + DashScope备用）
- `model_under_test`：被测模型（千帆，不支持备用）
- `evaluator`：评测模型（DashScope → ModelScope → 千帆兜底）

**API调用方式**：统一使用 OpenAI 兼容协议，通过 `openai` Python 包或 `requests` 直接调用

---

## 知识库

### 架构设计

- [三文件分离架构详解](./knowledge-base/01-架构设计/三文件分离架构详解.md) - 核心架构设计
- [评测维度体系设计](./knowledge-base/01-架构设计/评测维度体系设计.md) - 12维度评测体系
- [配置中心化设计](./knowledge-base/01-架构设计/配置中心化设计.md) - 配置管理架构

### 技术实现

- [Prompt 工程实现指南](./knowledge-base/02-技术实现/Prompt工程实现指南.md) - AI 评测场景下的 Prompt 设计方法论
- [评测管线实现详解](./knowledge-base/02-技术实现/评测管线实现详解.md) - 评测管线技术实现
- [配置注册中心设计](./knowledge-base/02-技术实现/配置注册中心设计.md) - 配置注册中心实现
- [测试运行记录器设计](./knowledge-base/02-技术实现/测试运行记录器设计.md) - 测试运行审计和追溯模块

### 使用指南

- [快速开始](./knowledge-base/03-使用指南/快速开始.md) - 项目快速上手
- [测试报告解读指南](./knowledge-base/03-使用指南/测试报告解读指南.md) - 如何理解测试报告
- [测试用例生成指南](./knowledge-base/03-使用指南/测试用例生成指南.md) - 用例生成操作说明

### 最佳实践

- [Bad Case 分析方法论](./knowledge-base/04-最佳实践/Bad%20Case分析方法论.md) - 失败用例深度分析
- [中断恢复操作指南](./knowledge-base/04-最佳实践/中断恢复操作指南.md) - 测试中断后的恢复策略
- [性能优化建议](./knowledge-base/04-最佳实践/性能优化建议.md) - 性能优化方向

### 文档价值说明

**技术评审最关心的文档**：
1. Prompt 工程技术方案 - 展示核心能力
2. 架构设计 - 展示系统设计思维
3. 技术分析 - 展示问题分析能力

**用户最关心的文档**：
- 使用指南 - 如何使用项目

---

## 可复用性

### 多项目支持

通过项目脚手架 `init_project.py` 快速创建新评测项目，安全维度规则由共享层统一提供，项目级片段按需定制。

| 项目 | 说明 | 状态 |
|------|------|------|
| `01-ai-customer-service` | AI客服评测 | 已验证 |
| `02-chat-companion` | 聊天助手评测 | 已创建 |

### 模板迁移

当前模板可直接应用于：

| 场景 | 迁移成本 | 验证状态 |
|------|---------|---------|
| 内容审核 | 低（修改规则部分） | 待验证 |
| 对话质量评估 | 中（增加评分维度） | 待验证 |
| 幻觉检测 | 低（替换知识库部分） | 待验证 |

### 工具开源

- 自动化评测脚本：`scripts/run_tests.py`（推荐）
- 用例生成脚本：`scripts/generate_test_cases.py`
- 项目脚手架：`scripts/init_project.py`
- Prompt 模板库：`templates/`

---

## 版本历史与演进脉络

| 版本 | 日期 | 关键变更 | 架构演进 |
|------|------|---------|---------|
| V1.0 | 2026-03-25 | 项目初始化 | 单脚本，硬编码 |
| V2.0 | 2026-04-04 | 通用用例生成器，10维度支持 | 配置外置，维度体系化 |
| V2.3 | 2026-04-06 | 两次调用分离，8维评测，API后备切换 | 被测/评测模型分离 |
| V3.0 | 2026-04-09 | 统一评测管线，Prompt注入路由，评测独立性保障，绕过率统计 | 动态Prompt组装 + 配置中心 |
| V3.1 | 2026-04-16 | 安全维度统一路由（3维度），项目级/共享层模板分离，多项目支持，项目脚手架，三模型独立配置 | 双层模板架构 + 多项目支持 |

**演进规律**：从硬编码 → 配置外置 → 架构分离 → 动态组装 → 双层模板+多项目，体现了从"能跑"到"工程化"到"可扩展"的迭代过程

---

## Bad Case 分析

> 评测结果及 Bad Case 分析详见各项目批次报告（`projects/*/results/batch-*/summary.md`）。

---

## Python 依赖

| 包 | 用途 |
|----|------|
| python-dotenv | 环境变量加载 |
| pytest / pytest-cov / pytest-asyncio | 测试框架 |
| openai | OpenAI兼容API客户端（评测模型调用） |
| pyyaml | YAML配置文件解析 |
| requests | HTTP请求（被测模型API调用） |
| tqdm | 进度条 |
| black / flake8 / mypy | 代码质量工具 |

---

## 许可证

本项目采用 MIT 许可证 - 详情见 [LICENSE](LICENSE) 文件。

---

*项目开始时间: 2026-03-25*
*最后更新: 2026-04-16*
*如果这个作品集对你有帮助，欢迎 Star ⭐*
