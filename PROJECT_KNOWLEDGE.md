# LLM Testing Portfolio - 项目认知知识库

> **本文件是项目的完整认知图谱，供 AI 模型和面试官快速理解项目全貌。**
> **阅读顺序：本文件 → README.md → 具体代码文件**

---

## 一、项目定位

**名称**：LLM Testing Portfolio（大模型质量保障作品集）

**核心定位**：一个面向 AI 对话系统的自动化评测框架，解决"AI 输出是概率性的，无法像传统测试那样对比预期结果"的核心难题。通过**三文件分离架构**将非结构化对话转化为可量化、可追溯的工程化资产。

**解决的核心问题**：

```
传统测试: 输入 → 确定性输出 → 对比预期结果 → 通过/失败
AI 测试:  输入 → 概率性输出 → 评测判定     → 判定结果（有灰度）
```

**技术方向**：Prompt 工程、API 测试、模型评估、数据处理

**项目起始**：2026-03-25

**面试官关注点速览**：

| 关注点 | 本项目体现 | 代码位置 |
|--------|-----------|---------|
| Prompt工程能力 | 3层模板架构 + 10维度评测Prompt + 动态组装 | `templates/`, `evaluation.py` |
| 架构设计能力 | 三文件分离 + ConfigRegistry + EvaluationContext | `config.py`, `execution.py` |
| 工程化能力 | 全流程自动化 + 批次管理 + 审计报告 + Bad Case管理 | `run_tests.py`, `reporting.py` |
| 安全测试能力 | Prompt注入攻击5类手法 + 绕过率统计 | `prompt-injection-rules.md`, `BypassStatsGenerator` |
| 可扩展性 | 多场景切换(通用/银行/电商) + YAML配置外置 | `business_rules.yaml`, `ConfigRegistry` |

---

## 二、项目架构总览

```
llm-testing-portfolio/
├── configs/                          # 配置中心（4个YAML）
├── scripts/                          # 自动化脚本（2个入口 + 7个工具模块）
│   ├── generate_test_cases.py        # 入口1：用例生成
│   ├── run_tests.py                  # 入口2：测试执行
│   └── tools/                        # 工具模块
│       ├── config.py                 # 配置管理（核心枢纽）
│       ├── evaluation.py             # 评测逻辑
│       ├── execution.py              # 执行记录
│       ├── prompt_template.py        # 模板加载
│       ├── reporting.py              # 报告生成
│       ├── under_test_prompt_assembler.py  # 被测Prompt组装
│       └── utils.py                  # 通用工具
├── templates/                        # Prompt模板库（3层架构）
│   ├── customer-service-evaluator.md # 评测器主模板
│   ├── evaluator-prompts/            # 评测Prompt模板
│   ├── evaluator-sections/           # 维度专用规则片段
│   ├── generation/                   # 用例生成模板
│   └── under-test/                   # 被测模型Prompt模板
├── projects/                         # 项目案例
│   └── 01-ai-customer-service/       # AI客服评测项目
│       ├── cases/                    # 测试用例库
│       │   ├── universal.json/md/csv # 通用评测用例
│       │   └── bad_cases/            # Bad Case沉淀库
│       └── results/                  # 测试结果（按批次存储）
├── knowledge-base/                   # 项目知识库文档
├── docs/                             # 内部文档（不提交Git）
├── tests/                            # 测试工具
├── .trae/                            # Trae IDE技能配置（不提交Git）
├── CLAUDE.md                         # AI编码规范（不提交Git）
├── requirements.txt                  # Python依赖
├── LICENSE                           # MIT许可证
└── README.md                         # 项目说明
```

---

## 三、核心数据流

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
│ (测试执行入口)    │   │ (测试执行器V3.0)    │   │ batch-XXX/       │
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

---

## 四、模块详解

### 4.1 配置中心 (`configs/`)

| 文件 | 职责 | 关键配置项 |
|------|------|-----------|
| `api_config.yaml` | API密钥（**不提交Git**） | qianfan.ak/sk, dashscope.api_key, modelscope.api_key |
| `api_config_example.yaml` | API密钥模板（占位符） | 同上，值为 YOUR_XXX_HERE |
| `business_rules.yaml` | 业务规则与场景定义 | active_scenario, scenarios(3个), constraints, compliance_rules, security_rules |
| `execution.yaml` | 执行参数配置 | concurrency(3种模式), parameters, quality_gate, performance_monitoring |
| `test_generation.yaml` | 用例生成配置 | dimensions(10个), generation_settings, multi_turn_scenarios(10个), csv_export_config |

**配置加载优先级**：`api_config.yaml` → `api_config_example.yaml` → 硬编码默认值

**业务场景**：default(通用客服) / bank(银行客服) / ecommerce(电商客服)，通过 `active_scenario` 切换

### 4.2 配置管理模块 (`scripts/tools/config.py`)

**核心类**：

| 类 | 职责 | 设计模式 |
|----|------|---------|
| `ConfigLoader` | YAML配置文件加载器，带缓存和fallback | 缓存+策略模式 |
| `ConfigRegistry` | 配置注册中心，不可变单例 | 依赖注入+单例模式 |
| `EvaluationContext` | 评测上下文，场景信息持久化与传递 | 嵌入式元数据模式 |
| `ConfigManager` | 统一配置管理器，整合Loader和Registry | 门面模式 |

**关键常量**：
- `MODEL_UNDER_TEST = "ernie-4.5-turbo-128k"` （被测模型）
- `EVALUATOR_MODEL = "qwen-turbo"` （评测模型）
- `QUALITY_GATE_THRESHOLD = 0.9` （质量门禁阈值）

**便捷函数**（统一访问接口）：
- `get_api_config()` / `get_api_key(service)` / `get_business_rules()`
- `get_test_generation_config()` / `get_evaluation_dimensions()` / `get_dimension_names()`
- `get_evaluator_providers()` / `get_model_under_test()` / `get_execution_config()`
- `get_test_cases_path()` / `get_evaluator_template_path()` / `get_results_dir()`

**评测Provider列表**（优先级排序）：
1. dashscope (qwen-turbo) - 优先级1
2. modelscope (Qwen3.5-35B-A3B) - 优先级2
3. qianfan (ernie-4.5-turbo-128k) - 优先级3（兜底）

### 4.3 用例生成模块 (`scripts/generate_test_cases.py`)

**类**：`TestCaseGenerator`

**10个评测维度**：

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

**多轮对话10种场景**：渐进式需求澄清、上下文追问链、信息提交与修改、纠错澄清、跨主题切换、条件筛选、方案比较、问题诊断、流程指导、记忆验证

**Prompt注入5种攻击手法**：指令忽略型、指令覆盖型、角色劫持型、系统Prompt泄露型、间接诱导型

**用例ID格式**：`TC-{维度代码}-{序号}`，如 `TC-ACC-001`

**用例字段**：id, dimension, dimension_cn, input, test_purpose, quality_criteria, _evaluation_context(元数据)

**输出格式**：universal.json（带metadata和changelog）+ universal.md + universal.csv

**版本管理**：自动版本号递增 + changelog记录 + Git版本控制

### 4.4 测试执行模块 (`scripts/run_tests.py`)

**类**：`TestRunner`（V3.0）

**核心特性**：
- 统一评测管线：EvaluatorPromptAssembler 动态组装评测Prompt
- EvaluationParser 多策略解析评测响应
- EvaluatorPolicy 评测独立性保障（strict/warn/relaxed）
- prompt_injection 维度路由（防御成功/绕过成功）
- ConfigRegistry 配置中心集成
- 绕过成功率统计

**执行模式**：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| single | 执行第1条用例 | 健康检查 |
| selected | 执行指定ID用例 | 调试 |
| incremental | 只执行未执行用例 | 持续测试 |
| full | 执行所有用例 | 回归测试 |

**报告输出模式**：new(新建批次) / append(追加) / update(更新) / report-only(仅重新生成)

**并发执行**：`--concurrent N`，建议不超过2

### 4.5 评测模块 (`scripts/tools/evaluation.py`)

**三个核心类**：

| 类 | 职责 |
|----|------|
| `EvaluatorPolicy` | 评测独立性策略检查（strict=必须不同模型, warn=警告, relaxed=允许相同） |
| `EvaluationParser` | 统一评测响应解析器（3层解析：结构化→关键词→正则兜底） |
| `EvaluatorPromptAssembler` | 评测Prompt动态组装器（3层模板架构） |

**3层模板架构**：
1. 基础层：`templates/customer-service-evaluator.md`（通用评测规则）
2. 维度扩展层：`templates/evaluator-sections/{dimension}-rules.md`（维度专用规则）
3. 场景注入层：从 `EvaluationContext` 动态注入场景信息

**EvaluationParser 解析策略**：
- 结构化格式：`【用例ID】-【测试结果:通过/不通过】`
- 关键词匹配：通过/不通过/防御成功/绕过成功
- 正则兜底：提取各维度判定结果

### 4.6 执行记录模块 (`scripts/tools/execution.py`)

| 类 | 职责 |
|----|------|
| `TestRunRecorder` | 测试运行记录器（配置基线、执行日志、完整性验证、异常检测） |
| `TestCaseExecutor` | 测试用例执行器（API调用抽象层） |

**TestRunRecorder 核心功能**：
- 配置基线管理：create_test_config / load_test_config / update_test_config
- 执行日志管理：start_logging / log_case_start / log_case_complete / end_logging
- 完整性验证：validate_coverage / validate_consistency / validate_config_integrity
- 异常检测：check_version_compatibility / detect_interruption
- 审计报告：generate_audit_report / save_audit_report

### 4.7 报告模块 (`scripts/tools/reporting.py`)

| 类 | 职责 |
|----|------|
| `BadCaseManager` | Bad Case管理器（提取/去重/累积/状态流转/多格式输出） |
| `BugListGenerator` | Bug清单生成器（Markdown+JSON，含复现步骤和环境信息） |
| `BypassStatsGenerator` | 绕过成功率统计工具（按攻击手法和绕过类型统计） |
| `EvaluationCSVExporter` | 评测结果CSV导出工具（明细CSV+统计汇总CSV） |

**Bad Case 严重程度**：P0（合规性不通过/绕过成功）、P1（其他不通过）

**Bad Case 状态流转**：open → fixed → verified → closed

### 4.8 模板加载模块 (`scripts/tools/prompt_template.py`)

**类**：`PromptTemplateLoader`

**功能**：从 `templates/` 目录加载 `.md` 模板文件，使用 `{{variable}}` 占位符渲染变量

**特性**：实例级缓存（非类变量）、支持 `\{{` 转义

### 4.9 被测Prompt组装模块 (`scripts/tools/under_test_prompt_assembler.py`)

**类**：`UnderTestPromptAssembler`

**模板架构**：
- 单轮模板：`templates/under-test/single-turn.md`
- 多轮 system 模板：`templates/under-test/multi-turn-system.md`
- 场景配置：`configs/business_rules.yaml`

**输出**：单轮返回 prompt 字符串，多轮返回 messages 列表

### 4.10 通用工具模块 (`scripts/tools/utils.py`)

**统一异常类体系**：
```
TestingFrameworkError (基础异常)
├── ConfigError (配置错误)
├── ExecutionError (执行错误)
├── EvaluationError (评测错误)
├── APIError (API调用错误)
├── ValidationError (数据验证错误)
└── ReportingError (报告生成错误)
```

**辅助函数**：ensure_dir, load_json, save_json, load_text, save_text, get_project_root, get_config_dir, get_templates_dir, get_projects_dir

---

## 五、模板库架构 (`templates/`)

### 5.1 评测器主模板

**文件**：`templates/customer-service-evaluator.md`

**角色**：AI 对话评测工程师

**评测维度**：10个（4核心+4高级+1多轮+1安全）

**输出格式**：
- 单轮：`【用例ID】-【测试结果:通过/不通过】` + 4维度推理过程
- 多轮：4子任务分步校验（逐轮校验→上下文一致性→指令坚守性→规则稳定性）
- Prompt注入：`【用例ID】-【测试结果:防御成功/绕过成功】` + 绕过类型

### 5.2 模板目录结构

```
templates/
├── customer-service-evaluator.md     # 评测器主模板（基础层）
├── evaluator-prompts/                # 评测Prompt模板
│   ├── standard.md                   # 标准单轮评测
│   └── multi-turn.md                 # 多轮评测
├── evaluator-sections/               # 维度专用规则片段（扩展层）
│   ├── multi-dimension-focus.md      # 多维度焦点
│   ├── multi-turn-focus.md           # 多轮对话焦点
│   └── prompt-injection-rules.md     # Prompt注入规则
├── generation/                       # 用例生成模板
│   ├── standard.md                   # 标准维度生成
│   ├── multi-turn.md                 # 多轮对话生成
│   └── prompt-injection.md           # Prompt注入生成
└── under-test/                       # 被测模型Prompt模板
    ├── single-turn.md                # 单轮对话
    └── multi-turn-system.md          # 多轮对话system message
```

---

## 六、三文件分离架构（核心创新）

**核心洞察**：AI 输出是概率性的，测试用例**不包含预期结果**（与传统测试的根本差异）

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
- ✅ **可追溯**：任何判定都能回溯到原始证据
- ✅ **可复现**：相同用例 + 相同模型 = 可复现的结果
- ✅ **可对比**：不同批次间可横向对比模型表现变化

**设计理念**：用例模板可复用，执行记录可追溯，评测结果可审计

---

## 七、项目案例 (`projects/01-ai-customer-service/`)

### 7.1 用例库 (`cases/`)

- `universal.json`：通用评测用例（带metadata和changelog的结构化JSON）
- `universal.md`：用例说明文档（Markdown格式，人类可读）
- `universal.csv`：用例CSV格式（Excel友好）
- `bad_cases/`：Bad Case 沉淀库
  - `bad_cases.json`：Bad Case 数据（含severity、状态流转、跨批次累积）
  - `bad_cases.md`：Bad Case 报告
  - `bad_cases.csv`：Bad Case CSV
  - `changelog.md`：Bad Case 变更日志

### 7.2 测试结果 (`results/`)

按批次存储，目录名格式：`batch-{序号}_{日期}`

**批次内文件**：

| 文件 | 说明 |
|------|------|
| `test_config.json` | 测试配置基线（环境、参数、质量门禁） |
| `test_execution.log` | 执行日志（用例级记录） |
| `records.json` | 执行记录（AI实际回答） |
| `results.json` | 评测结果（判定详情） |
| `summary.md` | 测试报告（人类可读） |
| `bug_list.md/json` | Bug清单（不通过用例） |
| `audit_report.md` | 审计报告（完整性检查） |
| `evaluation_detail.csv` | 评测明细CSV |
| `evaluation_summary.csv` | 统计汇总CSV |
| `bypass_stats_report.md` | 绕过成功率统计 |

---

## 八、Git 提交策略

### 8.1 提交到 Git 的文件

- `configs/`：除 `api_config.yaml` 外的所有配置
- `scripts/`：所有 Python 脚本
- `templates/`：所有 Prompt 模板
- `projects/01-ai-customer-service/cases/`：测试用例（universal.json/md, bad_cases.json/md）
- `projects/01-ai-customer-service/results/`：仅保留 batch-016 作为示例
- `knowledge-base/`：知识库文档（docs/下的中文文档）
- `tests/`：测试工具
- `requirements.txt`, `README.md`, `LICENSE`

### 8.2 不提交到 Git 的文件（.gitignore）

| 类别 | 规则 | 原因 |
|------|------|------|
| API密钥 | `configs/api_config.yaml` | 安全 |
| Python缓存 | `__pycache__/`, `*.pyc` | 构建产物 |
| 虚拟环境 | `venv/`, `.venv` | 环境相关 |
| IDE配置 | `.vscode/`, `.idea/` | 个人配置 |
| 测试结果 | `projects/*/results/*`（保留batch-016） | 数据量大 |
| 日志 | `*.log`, `logs/` | 运行时产物 |
| Trae技能 | `.trae/` | IDE工具配置 |
| AI编码规范 | `CLAUDE.md` | 个人工作流 |
| 内部文档 | `docs/` | 内部规划文档 |
| 环境变量 | `.env`, `.env.local` | 安全 |

---

## 九、Python 依赖

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

## 十、关键设计决策

### 10.1 评测独立性保障

**问题**：被测模型与评测模型相同时，评测结果不可信

**方案**：`EvaluatorPolicy` 三级策略
- strict（默认）：被测模型与评测模型必须不同，否则抛异常
- warn：允许相同但发出警告
- relaxed：允许相同且不警告

### 10.2 EvaluationContext 场景传递

**问题**：用例生成脚本与评测脚本之间的场景参数传递断裂

**方案**：将场景信息嵌入测试用例元数据（`_evaluation_context` 字段），评测时自动恢复。包含场景指纹（fingerprint）用于校验用例生成与评测使用相同场景。

### 10.3 评测Prompt动态组装

**问题**：将所有维度规则塞入同一个超长Prompt浪费Token

**方案**：3层模板架构按需组装
1. 基础层（通用规则）→ 2. 维度扩展层（按维度注入）→ 3. 场景注入层（动态场景信息）

### 10.4 多轮对话4子任务评测

**问题**：多轮对话评测复杂，单次判定容易遗漏

**方案**：固定4子任务分步校验
1. 逐轮单轮质量校验（4大维度）
2. 上下文一致性校验（矛盾/遗忘/幻觉）
3. 指令坚守性校验（是非判断：守了/没守）
4. 规则稳定性校验（趋势判断：稳/不稳）

### 10.5 Prompt注入攻击维度路由

**问题**：Prompt注入攻击的评测逻辑与标准维度完全不同

**方案**：独立路由，结果为"防御成功/绕过成功"而非"通过/不通过"，额外统计绕过成功率

---

## 十一、API 提供商

| 提供商 | 用途 | 模型 | API协议 |
|--------|------|------|---------|
| 百度千帆 | 被测模型（主要） | ernie-4.5-turbo-128k | OpenAI兼容 |
| 阿里云DashScope | 评测模型（主力） | qwen-turbo | OpenAI兼容 |
| 魔搭社区 | 评测模型（后备） | Qwen3.5-35B-A3B | OpenAI兼容 |

**API调用方式**：统一使用 OpenAI 兼容协议，通过 `openai` Python 包或 `requests` 直接调用

**后备切换策略**：DashScope → ModelScope → 千帆兜底

---

## 十二、测试工具 (`tests/`)

| 文件 | 用途 |
|------|------|
| `capture_prompt_baseline.py` | Prompt输出对比基线脚本（重构前后字节级对比） |
| `baseline_prompts/customer_prompts.json` | 被测模型Prompt基线 |
| `baseline_prompts/evaluator_prompts.json` | 评测模型Prompt基线 |

---

## 十三、内部文档 (`docs/`，不提交Git)

| 目录 | 内容 |
|------|------|
| `archive/` | 历史归档文档（技术方案、架构设计、重构计划） |
| `archive/deprecated/` | 废弃代码存档（旧版模块） |
| `archive/case_report_chaifen/` | 案例报告拆分分析 |
| `archive/history/` | 项目历史文档 |
| `archive/superpowers/` | 内部规划文档 |
| `superpowers/` | 当前规划文档 |
| `MY_JOURNEY.md` | 项目开发历程 |

---

## 十四、运行命令速查

```bash
# 用例生成
python3 scripts/generate_test_cases.py                              # 全量生成
python3 scripts/generate_test_cases.py --dimensions boundary,conflict  # 指定维度
python3 scripts/generate_test_cases.py --append                     # 追加模式
python3 scripts/generate_test_cases.py --csv                        # 导出CSV

# 测试执行（需在 projects/01-ai-customer-service/ 目录下）
python3 ../../scripts/run_tests.py --mode single                    # 健康检查
python3 ../../scripts/run_tests.py --mode full                      # 全量执行
python3 ../../scripts/run_tests.py --mode selected --cases TC-ACC-001  # 指定用例
python3 ../../scripts/run_tests.py --mode incremental --batch-id batch-003  # 增量
python3 ../../scripts/run_tests.py --report-only --batch-id batch-003  # 仅重新生成报告
python3 ../../scripts/run_tests.py --mode full --concurrent 2       # 并发执行

# Prompt基线对比
python3 tests/capture_prompt_baseline.py                            # 捕获基线
python3 tests/capture_prompt_baseline.py --compare                  # 对比基线
```

---

## 十五、版本历史

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| V1.0 | 2026-03-25 | 项目初始化 |
| V2.0 | 2026-04-04 | 通用用例生成器，10维度支持 |
| V2.3 | 2026-04-06 | 两次调用分离，8维评测，API后备切换 |
| V3.0 | 2026-04-09 | 统一评测管线，Prompt注入路由，评测独立性保障，绕过率统计 |

---

*知识库版本: 1.0*
*生成时间: 2026-04-13*
*覆盖范围: 全部Git追踪文件 + 非追踪目录/文件*
