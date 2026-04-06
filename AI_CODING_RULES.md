# AI 编码规范与最佳实践

> **本文件定义项目编码规范和软件工程最佳实践，供 AI 助手和开发者遵循**

**重要**: AI 助手在开始编码前，请务必完整阅读并遵循本文件。

---

## 📋 前置条件与依赖

### 本文件可以独立使用

✅ **好消息**: 本文件可以独立使用，不依赖任何外部工具或技能。

**即使你的 CodeBuddy 没有安装 Superpowers 技能，AI 依然会**:
- ✅ 遵循 Superpowers 工作流方法论
- ✅ 执行测试驱动开发（TDD）
- ✅ 遵循 SOLID 原则
- ✅ 进行代码质量审查

**原理**: 本文件将 Superpowers 的方法论和实践原则以文本形式呈现，AI 可以直接理解并执行。

---

### 如果安装了 Superpowers 技能

🚀 **更好的体验**: 如果你的 CodeBuddy 安装了 Superpowers 技能，你会获得：
- ✅ 自动化的工作流触发
- ✅ 更高级的代码审查能力
- ✅ 自动化测试生成
- ✅ 子代理并行处理

**安装方式**:
```bash
# 方法 1: 通过 CodeBuddy 技能管理器
# 在 CodeBuddy 中搜索 "superpowers" 并安装

# 方法 2: 手动安装（如果支持）
# 参考: https://github.com/obra/superpowers
```

**即使没有安装，本文件依然有效！**

---

## 🎯 核心价值观

### 项目使命
> **让这个项目成为求职时的"绝技"和"利器"，在所有求职者中脱颖而出。**

这不是简单的学习项目，而是：
- ✅ 一把能展示工程能力的"利剑"
- ✅ 一个能证明你比其他求职者更专业的"证据"
- ✅ 一个能让面试官眼前一亮的"作品"

### 核心原则

**1. 工程化思维**: 不只是"能跑"，而是"可维护、可扩展、可测试"
**2. 专业级质量**: 代码质量达到生产级别，而非原型级别
**3. 最佳实践**: 遵循行业标准的软件工程方法论
**4. 面试导向**: 每一行代码都能在面试中讲述其设计思想

---

## 🚀 Superpowers 工作流方法论

> **基于 Superpowers 技能框架的 AI 编程工程化方法论**

### 核心理念

Superpowers 是一套为 AI 编程代理设计的完整软件开发工作流系统，通过 20+ 个可组合的技能，强制 AI 遵循最佳实践。

**关键价值**:
- ✅ 测试覆盖率提升至 90%
- ✅ 减少 50% 的返工时间
- ✅ 提升开发效率 3 倍
- ✅ 避免"能跑但不敢改"的尴尬局面

### 三阶段工作流

#### 阶段 1: 头脑风暴（Brainstorming）

**目的**: 在开始编码前，充分理解需求和设计

**执行步骤**:
1. **需求澄清**: 向用户提问，明确需求和边界
2. **设计探索**: 提出多个设计方案，讨论优劣
3. **技术选型**: 选择合适的技术栈和架构
4. **风险评估**: 识别潜在风险和挑战

**AI 必须做到**:
- ❌ 不要立即开始编码
- ✅ 先提问澄清需求
- ✅ 提出至少 2-3 个设计方案
- ✅ 讨论每个方案的优劣

**示例对话**:
```
用户: 帮我实现一个测试用例生成器

AI (错误做法):
[立即生成代码...]

AI (正确做法):
在开始编码前，我需要澄清几个问题：

1. **目标用户**: 这个生成器是给谁用的？
   - 测试工程师？开发者？AI 研究员？

2. **输入输出**: 
   - 输入是什么？（需求文档？测试场景？）
   - 输出格式是什么？（JSON？Excel？Markdown？）

3. **测试类型**: 
   - 功能测试？性能测试？安全测试？
   - 需要支持哪些测试维度？

4. **技术选型**: 
   - 使用本地模型还是调用 API？
   - 需要支持哪些 LLM 提供商？

请告诉我你的具体需求，我会提供 2-3 个设计方案供你选择。
```

---

#### 阶段 2: 测试驱动开发（TDD）

**目的**: 先写测试，再写实现，确保代码质量

**TDD 三步循环**:
```
🔴 Red    → 先写失败的测试
🟢 Green  → 写最简单的代码让测试通过
🔵 Refactor → 重构代码，提升质量
```

**AI 必须遵循的 TDD 流程**:

1. **明确需求** → 写测试用例
2. **运行测试** → 确认测试失败（🔴 Red）
3. **写实现代码** → 让测试通过（🟢 Green）
4. **重构优化** → 提升代码质量（🔵 Refactor）
5. **重复循环** → 直到所有功能完成

**示例**:
```python
# 第 1 步：先写测试（🔴 Red）
def test_generate_test_case():
    """测试用例生成器应该生成符合规范的测试用例"""
    generator = TestCaseGenerator()
    test_case = generator.generate("测试AI客服的准确性")
    
    assert test_case is not None
    assert "id" in test_case
    assert "input" in test_case
    assert "expected_output" in test_case

# 运行测试 → 失败（因为还没有实现）

# 第 2 步：写实现代码（🟢 Green）
class TestCaseGenerator:
    def generate(self, requirement: str) -> dict:
        """生成测试用例"""
        return {
            "id": "TC-001",
            "input": requirement,
            "expected_output": "..."
        }

# 运行测试 → 通过

# 第 3 步：重构优化（🔵 Refactor）
class TestCaseGenerator:
    """AI 测试用例生成器
    
    使用 LLM 自动生成符合规范的测试用例
    """
    
    def __init__(self, model: str = "ernie-4.5"):
        self.model = model
        self.client = LLMClient(model)
    
    def generate(self, requirement: str) -> TestCase:
        """生成测试用例
        
        Args:
            requirement: 测试需求描述
            
        Returns:
            TestCase: 生成的测试用例对象
        """
        prompt = self._build_prompt(requirement)
        response = self.client.chat(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, requirement: str) -> str:
        """构建生成提示词"""
        # 实现细节...
        pass
    
    def _parse_response(self, response: str) -> TestCase:
        """解析 LLM 响应"""
        # 实现细节...
        pass
```

**TDD 的价值**:
- ✅ 确保代码可测试
- ✅ 提前发现设计问题
- ✅ 提供活的文档（测试即文档）
- ✅ 重构时有安全网

---

#### 阶段 3: 子代理驱动开发（Subagent-Driven Development）

**目的**: 将复杂任务拆分为独立子任务，并行处理，提升效率

**适用场景**:
- 多个独立的功能模块
- 需要并行处理的任务
- 大型项目的迭代开发

**执行流程**:

1. **任务拆解**: 将大任务拆分为多个独立子任务
2. **并行执行**: 每个子任务由独立的 AI 子代理处理
3. **自动审查**: 子代理完成后自动审查代码质量
4. **合并结果**: 将所有子任务的结果合并

**示例**:
```
用户: 实现一个完整的 AI 测试框架

AI:
这个任务可以拆分为多个独立模块：

1. **测试用例生成器** → 子代理 A
   - 输入：测试需求
   - 输出：测试用例 JSON

2. **测试执行引擎** → 子代理 B
   - 输入：测试用例
   - 输出：执行记录

3. **评测引擎** → 子代理 C
   - 输入：执行记录
   - 输出：评测结果

4. **报告生成器** → 子代理 D
   - 输入：评测结果
   - 输出：测试报告

我将创建 4 个子代理并行处理这些模块，每个子代理都会：
- 遵循 TDD 流程
- 编写单元测试
- 进行代码审查

是否开始执行？
```

---

### 自动审查机制

**两阶段审查**:

#### 阶段 1: 规格合规性审查
- ✅ 是否符合需求规格？
- ✅ 是否处理了所有边界情况？
- ✅ 是否符合项目架构设计？

#### 阶段 2: 代码质量审查
- ✅ 是否遵循 SOLID 原则？
- ✅ 是否有充分的测试覆盖？
- ✅ 是否有清晰的文档注释？
- ✅ 是否符合命名规范？
- ✅ 是否有潜在的性能问题？

**AI 必须在每次提交代码前进行自我审查**。

---

## 📐 软件工程核心原则

### SOLID 原则

> **面向对象设计的五大原则，构建可维护、可扩展的软件系统**

#### S - 单一职责原则（Single Responsibility Principle）

**定义**: 一个类应该只有一个引起它变化的原因

**✅ 正确示例**:
```python
# 每个类只有一个职责
class TestCaseGenerator:
    """只负责生成测试用例"""
    def generate(self, requirement: str) -> TestCase:
        pass

class TestCaseExecutor:
    """只负责执行测试用例"""
    def execute(self, test_case: TestCase) -> ExecutionResult:
        pass

class TestResultEvaluator:
    """只负责评测结果"""
    def evaluate(self, result: ExecutionResult) -> EvaluationResult:
        pass
```

**❌ 错误示例**:
```python
# 一个类承担多个职责
class TestFramework:
    """负责生成、执行、评测所有事情"""
    def generate_test_case(self, requirement: str):
        pass
    
    def execute_test_case(self, test_case: TestCase):
        pass
    
    def evaluate_result(self, result: ExecutionResult):
        pass
```

**为什么重要**:
- ✅ 降低类的复杂度
- ✅ 提高代码可读性
- ✅ 便于单元测试
- ✅ 降低修改风险

---

#### O - 开放封闭原则（Open/Closed Principle）

**定义**: 软件实体应该对扩展开放，对修改关闭

**✅ 正确示例**:
```python
# 通过抽象基类实现扩展
from abc import ABC, abstractmethod

class Evaluator(ABC):
    """评测器基类"""
    
    @abstractmethod
    def evaluate(self, response: str, criteria: dict) -> EvaluationResult:
        """评测方法"""
        pass

class AccuracyEvaluator(Evaluator):
    """准确性评测器"""
    def evaluate(self, response: str, criteria: dict) -> EvaluationResult:
        # 实现准确性评测逻辑
        pass

class CompletenessEvaluator(Evaluator):
    """完整性评测器"""
    def evaluate(self, response: str, criteria: dict) -> EvaluationResult:
        # 实现完整性评测逻辑
        pass

# 添加新的评测器不需要修改现有代码
class SafetyEvaluator(Evaluator):
    """安全性评测器"""
    def evaluate(self, response: str, criteria: dict) -> EvaluationResult:
        # 实现安全性评测逻辑
        pass
```

**面试价值**:
> "我的测试框架遵循开放封闭原则，通过抽象基类定义评测器接口。当需要添加新的评测维度时，只需要创建新的评测器类，不需要修改现有代码。这样保证了系统的稳定性和可扩展性。"

---

#### L - 里氏替换原则（Liskov Substitution Principle）

**定义**: 子类对象必须能够替换父类对象，且不影响程序正确性

**✅ 正确示例**:
```python
class LLMClient(ABC):
    """LLM 客户端基类"""
    
    @abstractmethod
    def chat(self, prompt: str) -> str:
        """发送聊天请求"""
        pass

class ErnieClient(LLMClient):
    """文心一言客户端"""
    def chat(self, prompt: str) -> str:
        # 调用文心一言 API
        pass

class GPTClient(LLMClient):
    """GPT 客户端"""
    def chat(self, prompt: str) -> str:
        # 调用 GPT API
        pass

# 使用时可以无缝替换
def test_llm(client: LLMClient):
    response = client.chat("你好")
    assert response is not None

# 任意子类都可以替换父类
test_llm(ErnieClient())
test_llm(GPTClient())
```

---

#### I - 接口隔离原则（Interface Segregation Principle）

**定义**: 客户端不应该依赖它不需要的接口

**✅ 正确示例**:
```python
# 将大接口拆分为小接口
class TestCaseGenerator(ABC):
    """测试用例生成器接口"""
    @abstractmethod
    def generate(self, requirement: str) -> TestCase:
        pass

class TestCaseSerializer(ABC):
    """测试用例序列化接口"""
    @abstractmethod
    def to_json(self, test_case: TestCase) -> str:
        pass

class TestCaseValidator(ABC):
    """测试用例验证接口"""
    @abstractmethod
    def validate(self, test_case: TestCase) -> bool:
        pass

# 具体类只需要实现需要的接口
class SimpleGenerator(TestCaseGenerator):
    """简单生成器，只负责生成"""
    def generate(self, requirement: str) -> TestCase:
        pass

class AdvancedGenerator(
    TestCaseGenerator, 
    TestCaseSerializer, 
    TestCaseValidator
):
    """高级生成器，实现所有接口"""
    def generate(self, requirement: str) -> TestCase:
        pass
    
    def to_json(self, test_case: TestCase) -> str:
        pass
    
    def validate(self, test_case: TestCase) -> bool:
        pass
```

---

#### D - 依赖倒置原则（Dependency Inversion Principle）

**定义**: 高层模块不应该依赖低层模块，两者都应该依赖抽象

**✅ 正确示例**:
```python
# 高层模块依赖抽象，不依赖具体实现
class TestRunner:
    """测试运行器（高层模块）"""
    
    def __init__(
        self, 
        llm_client: LLMClient,  # 依赖抽象
        evaluator: Evaluator     # 依赖抽象
    ):
        self.llm_client = llm_client
        self.evaluator = evaluator
    
    def run_test(self, test_case: TestCase) -> TestResult:
        """运行测试"""
        # 1. 执行测试
        response = self.llm_client.chat(test_case.input)
        
        # 2. 评测结果
        evaluation = self.evaluator.evaluate(
            response, 
            test_case.criteria
        )
        
        return TestResult(
            test_case=test_case,
            response=response,
            evaluation=evaluation
        )

# 使用时注入具体实现
runner = TestRunner(
    llm_client=ErnieClient(),  # 可以随时替换
    evaluator=AccuracyEvaluator()
)
```

**为什么重要**:
- ✅ 降低耦合度
- ✅ 提高灵活性
- ✅ 便于单元测试（可以注入 Mock 对象）
- ✅ 符合依赖注入模式

---

### 其他核心原则

#### KISS 原则（Keep It Simple, Stupid）

**定义**: 保持简单，不要过度设计

**✅ 正确做法**:
- 用最简单的方案解决问题
- 不过度抽象
- 不过度优化

**❌ 错误做法**:
- 为了"灵活性"添加不需要的功能
- 为了"完美"过度设计
- 为了"炫技"使用复杂技术

---

#### DRY 原则（Don't Repeat Yourself）

**定义**: 不要重复自己，避免代码重复

**✅ 正确做法**:
```python
# 提取公共逻辑
def save_to_file(data: dict, file_path: str):
    """保存数据到文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 多处使用
save_to_file(test_cases, "test_cases.json")
save_to_file(results, "results.json")
save_to_file(report, "report.json")
```

---

#### YAGNI 原则（You Aren't Gonna Need It）

**定义**: 不要实现当前不需要的功能

**✅ 正确做法**:
- 只实现当前需求
- 不要预测未来需求
- 保持代码简洁

---

### 设计模式应用

#### 工厂模式（Factory Pattern）

**应用场景**: 创建复杂的对象

```python
class EvaluatorFactory:
    """评测器工厂"""
    
    @staticmethod
    def create_evaluator(dimension: str) -> Evaluator:
        """创建评测器"""
        evaluators = {
            "accuracy": AccuracyEvaluator,
            "completeness": CompletenessEvaluator,
            "compliance": ComplianceEvaluator,
            "attitude": AttitudeEvaluator
        }
        
        if dimension not in evaluators:
            raise ValueError(f"未知的评测维度: {dimension}")
        
        return evaluators[dimension]()

# 使用
evaluator = EvaluatorFactory.create_evaluator("accuracy")
result = evaluator.evaluate(response, criteria)
```

#### 策略模式（Strategy Pattern）

**应用场景**: 算法可以相互替换

```python
class TestGenerationStrategy(ABC):
    """测试生成策略"""
    
    @abstractmethod
    def generate(self, requirement: str) -> List[TestCase]:
        pass

class RandomStrategy(TestGenerationStrategy):
    """随机生成策略"""
    def generate(self, requirement: str) -> List[TestCase]:
        # 随机生成测试用例
        pass

class TemplateBasedStrategy(TestGenerationStrategy):
    """模板生成策略"""
    def generate(self, requirement: str) -> List[TestCase]:
        # 基于模板生成测试用例
        pass

class AIGeneratedStrategy(TestGenerationStrategy):
    """AI 生成策略"""
    def generate(self, requirement: str) -> List[TestCase]:
        # 使用 AI 生成测试用例
        pass

# 使用时可以随时切换策略
class TestCaseGenerator:
    def __init__(self, strategy: TestGenerationStrategy):
        self.strategy = strategy
    
    def generate(self, requirement: str) -> List[TestCase]:
        return self.strategy.generate(requirement)

# 切换策略
generator = TestCaseGenerator(AIGeneratedStrategy())
test_cases = generator.generate("测试AI客服的准确性")
```

---

## 🧪 测试策略

### 测试金字塔

```
        /\
       /  \      E2E 测试（端到端测试）
      /----\     - 10%
     /      \    - 模拟真实用户场景
    /--------\   
   /          \  集成测试（API 测试）
  /------------\ - 20%
 /              \- 测试模块间交互
/----------------\
 单元测试（函数/类测试）
- 70%
- 测试独立单元
```

### 单元测试规范

**必须测试的内容**:
- ✅ 核心业务逻辑
- ✅ 边界条件
- ✅ 异常处理
- ✅ 关键算法

**测试命名规范**:
```python
def test_<功能>_<场景>_<预期结果>():
    """
    测试说明
    
    场景：
    预期：
    """
    pass

# 示例
def test_generate_test_case_with_valid_requirement_returns_valid_case():
    """测试生成测试用例 - 有效需求 - 返回有效用例"""
    generator = TestCaseGenerator()
    test_case = generator.generate("测试AI客服的准确性")
    
    assert test_case is not None
    assert "id" in test_case
    assert "input" in test_case

def test_generate_test_case_with_empty_requirement_raises_error():
    """测试生成测试用例 - 空需求 - 抛出错误"""
    generator = TestCaseGenerator()
    
    with pytest.raises(ValueError):
        generator.generate("")
```

### 测试覆盖率目标

- **单元测试覆盖率**: ≥ 80%
- **核心模块覆盖率**: ≥ 90%
- **关键路径覆盖率**: 100%

---

## 📁 文件命名规范

### Python 文件

**规范**: 动词开头 + 下划线分隔 + 全小写

**✅ 正确示例**:
```
generate_test_cases.py      # 生成测试用例
run_evaluations.py          # 运行评测
compare_cot_methods.py      # 对比 CoT 方法
```

**❌ 错误示例**:
```
test_runner.py              # 名词开头
test-cases.py               # 连字符
GenTestCases.py             # 驼峰
gen_tc.py                   # 过度缩写
```

**常见动词**:
```
generate, run, compare, setup, build, test, create,
update, delete, get, set, add, remove, check, validate,
parse, format, convert, extract, load, save, read, write,
process, execute, init, start, stop, fix, resolve, handle,
manage, configure, install, deploy, publish, download, upload
```

---

### Markdown 文件

**规范**: 连字符分隔 + 全小写

**✅ 正确示例**:
```
how-to-install.md
getting-started.md
customer-service-evaluator.md
```

**❌ 错误示例**:
```
how_to_install.md           # 下划线（不符合 Markdown 规范）
GettingStarted.md           # 驼峰
```

**原因**: Markdown 文件通常用于文档网站，连字符在 URL 中更友好。

---

### JSON 文件

**规范**: 下划线分隔 + 全小写

**✅ 正确示例**:
```
test_cases.json
records.json
results.json
```

**❌ 错误示例**:
```
project-data.json           # 连字符
ProjectData.json            # 驼峰
```

---

## 💻 代码规范

### Python 代码

**变量命名**: 下划线分隔
```python
# ✅ 正确
test_cases = []
api_response = {}
execution_time = 0

# ❌ 错误
testCases = []              # 驼峰
testcases = []              # 单词拼接
```

**函数命名**: 动词开头 + 下划线分隔
```python
# ✅ 正确
def generate_test_cases():
    pass

def run_evaluation(test_case):
    pass

# ❌ 错误
def testCases():            # 名词
def runTest():              # 驼峰
```

**类命名**: 驼峰
```python
# ✅ 正确
class TestCaseGenerator:
    pass

class EvaluationEngine:
    pass

# ❌ 错误
class test_case_generator:  # 下划线
```

---

### 文档字符串规范

**使用 Google 风格的文档字符串**:
```python
class TestCaseGenerator:
    """AI 测试用例生成器
    
    使用 LLM 自动生成符合规范的测试用例。
    
    Attributes:
        model: 使用的 LLM 模型名称
        client: LLM 客户端实例
    
    Example:
        >>> generator = TestCaseGenerator(model="ernie-4.5")
        >>> test_case = generator.generate("测试AI客服的准确性")
        >>> print(test_case.id)
        'TC-001'
    """
    
    def __init__(self, model: str = "ernie-4.5"):
        """初始化生成器
        
        Args:
            model: LLM 模型名称，默认为 "ernie-4.5"
        
        Raises:
            ValueError: 如果 model 为空字符串
        """
        pass
    
    def generate(self, requirement: str) -> TestCase:
        """生成测试用例
        
        Args:
            requirement: 测试需求描述
        
        Returns:
            TestCase: 生成的测试用例对象
        
        Raises:
            ValueError: 如果 requirement 为空
            LLMError: 如果 LLM 调用失败
        
        Example:
            >>> test_case = generator.generate("测试AI客服的准确性")
        """
        pass
```

---

## 🏗️ 架构设计原则

### 分层架构

```
┌─────────────────────────────────────┐
│         Presentation Layer          │  展示层（CLI/Web）
│   - 用户交互                        │
│   - 输入验证                        │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│          Business Layer             │  业务层
│   - 业务逻辑                        │
│   - 工作流编排                      │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│         Service Layer               │  服务层
│   - 外部服务集成                    │
│   - LLM API 调用                    │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│          Data Layer                 │  数据层
│   - 数据存储                        │
│   - 文件读写                        │
└─────────────────────────────────────┘
```

### 模块划分

```
llm-testing-portfolio/
├── scripts/        # 核心业务脚本（业务层）
├── tools/          # 辅助工具（数据层/服务层）
├── templates/      # Prompt 模板（配置层）
├── docs/           # 技术文档
└── projects/       # 项目案例（展示层）
```

**职责划分**:
- `scripts/` → 核心业务逻辑（生成用例、运行测试、对比实验）
- `tools/` → 辅助工具（文档生成、Git Hook、规范检查）
- `templates/` → Prompt 模板文件
- `docs/` → 技术文档
- `projects/` → 具体项目案例

---

## 🎯 AI 编程最佳实践

### 规范驱动开发（SDD）

**核心理念**: 通过形式化规范引导 AI 生成生产级代码

**流程**:
1. **编写规范**: 定义接口、数据结构、业务规则
2. **AI 生成**: AI 根据规范生成代码
3. **验证对齐**: 检查代码是否符合规范
4. **迭代优化**: 修正偏差，完善规范

**示例规范**:
```python
# test_case.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class TestCase:
    """测试用例数据结构
    
    规范：
    - id: 必填，格式为 "TC-{维度}-{序号}"
    - dimension: 必填，必须是预定义的维度之一
    - input: 必填，用户输入的问题
    - expected_output: 可选，期望的输出
    - quality_criteria: 必填，质量标准
    """
    id: str
    dimension: str
    input: str
    expected_output: Optional[str] = None
    quality_criteria: str
    
    def __post_init__(self):
        """验证数据规范"""
        # 验证 ID 格式
        if not self.id.startswith("TC-"):
            raise ValueError(f"ID 必须以 'TC-' 开头: {self.id}")
        
        # 验证维度
        valid_dimensions = ["accuracy", "completeness", "compliance", "attitude", "multi"]
        if self.dimension not in valid_dimensions:
            raise ValueError(f"无效的维度: {self.dimension}")
```

---

### 代码质量保证

#### 1. 静态代码分析

**使用工具**:
- `pylint`: 代码质量检查
- `black`: 代码格式化
- `mypy`: 类型检查

**配置**:
```bash
# 安装工具
pip install pylint black mypy

# 运行检查
pylint scripts/
black scripts/
mypy scripts/
```

#### 2. 代码审查清单

**AI 必须在每次提交代码前检查**:

- [ ] **功能正确性**: 代码是否实现了需求？
- [ ] **测试覆盖**: 是否有充分的单元测试？
- [ ] **命名规范**: 变量、函数、类名是否清晰？
- [ ] **文档注释**: 是否有清晰的文档字符串？
- [ ] **错误处理**: 是否处理了异常情况？
- [ ] **性能考虑**: 是否有明显的性能问题？
- [ ] **安全考虑**: 是否有安全隐患？
- [ ] **SOLID 原则**: 是否符合设计原则？
- [ ] **代码复用**: 是否避免了重复代码？
- [ ] **可维护性**: 代码是否易于修改？

---

### 性能优化原则

#### 1. 避免过早优化

**✅ 正确做法**:
1. 先让代码工作
2. 编写测试
3. 测量性能瓶颈
4. 针对性优化

**❌ 错误做法**:
- 在没有性能问题时过度优化
- 为了"性能"牺牲可读性

#### 2. 优化策略

**I/O 密集型任务**:
```python
# 使用异步编程
import asyncio

async def fetch_llm_response(prompt: str) -> str:
    """异步调用 LLM API"""
    # 实现异步调用
    pass

# 批量处理
async def batch_generate(test_cases: List[TestCase]) -> List[TestCase]:
    """批量生成测试用例"""
    tasks = [generate_test_case(tc) for tc in test_cases]
    return await asyncio.gather(*tasks)
```

**CPU 密集型任务**:
```python
# 使用多进程
from multiprocessing import Pool

def process_test_case(test_case: TestCase) -> EvaluationResult:
    """处理单个测试用例"""
    pass

# 批量处理
with Pool(processes=4) as pool:
    results = pool.map(process_test_case, test_cases)
```

---

## 🎯 面试价值

### 可以这样说

**关于工程化思维**:
> "我的项目遵循软件工程的最佳实践，采用 Superpowers 工作流方法论，强制执行测试驱动开发（TDD）和代码审查机制。测试覆盖率达到 90%，减少了 50% 的返工时间。"

**关于架构设计**:
> "我使用 SOLID 原则指导架构设计，通过依赖倒置原则降低耦合度，通过开放封闭原则保证可扩展性。当需要添加新的评测维度时，只需要创建新的评测器类，不需要修改现有代码。"

**关于测试策略**:
> "我采用测试金字塔策略，70% 的单元测试、20% 的集成测试、10% 的 E2E 测试。所有核心模块的测试覆盖率都在 90% 以上，关键路径达到 100%。"

**关于代码质量**:
> "我使用 pylint、black、mypy 等工具保证代码质量，每次提交前都会进行自动化的代码审查。所有函数都有清晰的文档字符串，遵循 Google 风格的注释规范。"

---

## 📋 AI 编程检查清单

### 开始任务前

- [ ] 是否完整阅读了 AI_CODING_RULES.md？
- [ ] 是否理解了任务需求和边界？
- [ ] 是否澄清了不明确的地方？
- [ ] 是否提出了多个设计方案？
- [ ] 是否选择了合适的技术栈？

### 编码过程中

- [ ] 是否遵循 TDD 流程（先写测试）？
- [ ] 是否遵循 SOLID 原则？
- [ ] 是否遵循命名规范？
- [ ] 是否添加了清晰的文档注释？
- [ ] 是否处理了异常情况？

### 提交代码前

- [ ] 是否运行了所有测试？
- [ ] 是否进行了代码审查？
- [ ] 是否检查了代码覆盖率？
- [ ] 是否运行了静态分析工具？
- [ ] 是否更新了相关文档？

---

## 📚 参考资源

### 软件工程方法论
- [Superpowers - AI编程纪律框架](https://github.com/obra/superpowers)
- [规范驱动开发（SDD）](https://cloud.tencent.com/developer/article/2586438)
- [测试驱动开发（TDD）](https://en.wikipedia.org/wiki/Test-driven_development)

### 设计原则
- [SOLID 原则](https://en.wikipedia.org/wiki/SOLID)
- [设计模式](https://refactoring.guru/design-patterns)
- [Clean Code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

### 代码规范
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Markdown Style Guide](https://ocular-d.github.io/styleguide-markdown/)

### 测试策略
- [测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)
- [单元测试最佳实践](https://testdriven.io/blog/testing-best-practices/)
- [pytest 文档](https://docs.pytest.org/)

---

## 🔄 持续改进

**本文件是活的文档，随着项目演进不断优化。**

**更新记录**:
- 2026-04-05: 创建初始版本
- 未来: 根据项目实践持续优化

---

*"代码是写给人看的，顺便能在机器上运行。" — Donald Knuth*

*"简单的代码比聪明的代码更有价值。" — unknown*

*"测试是最好的文档。如果代码有测试，说明它是被设计来工作的。" — unknown*

---

**最后更新**: 2026-04-05  
**版本**: v2.0  
**维护者**: AI Assistant with Superpowers
