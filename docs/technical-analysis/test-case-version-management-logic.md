# 测试用例版本管理逻辑分析

> 为什么选择"单文件+版本号+Git"模式？

---

## 文档信息

- **创建日期**: 2026-04-06
- **更新日期**: 2026-04-06
- **技术领域**: 测试用例管理、版本控制

---

## 一、背景问题

### 1.1 原始方案的问题

在项目初期，测试用例管理采用了以下方案：

```
cases/
├── v1.0/
│   └── universal.json    # v1.0 版本的测试用例
├── v1.1/
│   └── universal.json    # v1.1 版本的测试用例
└── history/
    ├── backup_20260405.json
    ├── backup_20260406.json
    └── ...
```

**问题**：
1. **冗余存储**: 每个版本都保存完整用例，占用空间
2. **版本混乱**: v1.0、v1.1、history 三种版本管理方式并存
3. **不一致性**: Git 已经提供版本控制，本地 history 目录功能重复
4. **维护成本**: 需要手动管理 history 目录，容易遗漏或误删

### 1.2 核心矛盾

**Git 已经是优秀的版本控制系统，为什么还要在本地再实现一套版本管理？**

---

## 二、方案对比

### 2.1 方案 A：多文件模式（原方案）

```
cases/
├── v1.0/universal.json
├── v1.1/universal.json
├── v1.2/universal.json
└── ...
```

**优点**：
- ✅ 版本物理隔离，清晰直观
- ✅ 可以同时访问多个版本

**缺点**：
- ❌ 冗余存储，每个版本保存完整用例
- ❌ 需要手动管理版本目录
- ❌ 与 Git 版本控制功能重复
- ❌ 容易导致版本混乱（忘记创建新版本目录）

---

### 2.2 方案 B：单文件 + 本地 history 目录

```
cases/
├── universal.json
└── history/
    ├── backup_20260405.json
    └── backup_20260406.json
```

**优点**：
- ✅ 单一文件，结构简单
- ✅ 本地备份，恢复方便

**缺点**：
- ❌ history 目录管理混乱（命名不规范、容易遗漏）
- ❌ 与 Git 版本控制功能重复
- ❌ 缺少版本号标记，难以快速定位
- ❌ 占用额外存储空间

---

### 2.3 方案 C：单文件 + 版本号 + Git（推荐）

```
cases/
└── universal.json    # 单一文件，内含版本号
```

**文件内部结构**：
```json
{
  "metadata": {
    "version": "1.1",
    "created_at": "2026-04-05",
    "updated_at": "2026-04-05",
    "changelog": [
      {
        "version": "1.0",
        "date": "2026-04-01",
        "changes": "初始版本"
      },
      {
        "version": "1.1",
        "date": "2026-04-05",
        "changes": "新增 20 条用例，修复 5 条用例"
      }
    ]
  },
  "cases": {
    "accuracy": [...],
    "completeness": [...],
    ...
  }
}
```

**优点**：
- ✅ 单一文件，结构最简单
- ✅ 版本号清晰标记
- ✅ changelog 记录变更历史
- ✅ Git 负责版本控制（专业工具做专业的事）
- ✅ 无冗余存储
- ✅ 强制规范化（每次更新必须更新版本号和 changelog）

**缺点**：
- ⚠️ 需要从 Git 查看历史版本（但这是正确的做法）
- ⚠️ 需要严格遵循版本号递增规则

---

## 三、最终方案：单文件 + 版本号 + Git

### 3.1 核心设计理念

**"专业工具做专业的事"**

- **Git**: 负责版本控制（历史版本、回滚、diff）
- **JSON**: 负责数据存储（用例内容、版本号、changelog）
- **脚本**: 负责版本管理逻辑（版本递增、changelog 更新）

### 3.2 为什么删除本地 history 目录？

**原因 1：功能重复**

Git 已经提供了完整的版本控制功能：
```bash
# 查看历史版本
git log --oneline cases/universal.json

# 查看某个版本的内容
git show a1b2c3d:cases/universal.json

# 回滚到某个版本
git checkout a1b2c3d -- cases/universal.json

# 对比两个版本
git diff v1.0 v1.1 -- cases/universal.json
```

本地 history 目录只是"重新发明轮子"，而且做得不如 Git 好。

**原因 2：容易导致不一致**

- history 目录的命名不规范（backup_20260405.json vs backup_20260406.json）
- 容易遗漏备份或误删备份
- 与 Git 版本对应关系不明确

**原因 3：占用额外存储空间**

每次修改用例，都需要保存完整副本，浪费存储空间。

### 3.3 为什么保留 changelog 字段？

虽然 Git 可以查看提交历史，但 changelog 字段仍然有其价值：

**原因 1：快速了解变更概要**

不需要执行 `git log` 命令，直接查看文件就能了解变更历史：

```json
{
  "changelog": [
    {
      "version": "1.1",
      "date": "2026-04-05",
      "changes": "新增 20 条用例，修复 5 条用例"
    }
  ]
}
```

**原因 2：变更说明更规范**

Git commit message 可能包含无关信息，changelog 字段强制要求简洁、规范的变更说明。

**原因 3：与测试报告关联**

测试报告可以引用 changelog，说明测试的是哪个版本、有什么变更。

---

## 四、版本管理逻辑

### 4.1 版本号规则

**格式**: `major.minor`（如 1.0、1.1、1.2）

- **major（主版本号）**: 用例结构发生重大变更（如新增维度、字段重构）
- **minor（次版本号）**: 用例内容变更（如新增用例、修改用例、删除用例）

**递增规则**:
```python
# 从当前文件读取版本号
current_version = "1.1"
major, minor = map(int, current_version.split("."))

# 默认递增 minor
new_version = f"{major}.{minor + 1}"  # 1.2

# 如果结构发生重大变更，递增 major
new_version = f"{major + 1}.0"  # 2.0
```

### 4.2 版本更新流程

```python
# scripts/generate_test_cases.py 核心逻辑

def generate_test_cases(args):
    # 读取现有用例（如果存在）
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取当前版本号
        current_version = data["metadata"]["version"]
        major, minor = map(int, current_version.split("."))
        
        # 递增版本号
        new_version = f"{major}.{minor + 1}"
        
        # 保留 changelog
        existing_changelog = data["metadata"].get("changelog", [])
    else:
        # 首次创建
        new_version = "1.0"
        existing_changelog = []
    
    # 生成新用例
    new_cases = generate_cases_with_llm(args)
    
    # 更新 changelog
    changelog_entry = {
        "version": new_version,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "changes": args.change_description or f"v{new_version}: 新版本"
    }
    updated_changelog = existing_changelog + [changelog_entry]
    
    # 写入文件
    data = {
        "metadata": {
            "version": new_version,
            "created_at": ...,
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
            "changelog": updated_changelog,
            ...
        },
        "cases": new_cases
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 用例已生成: v{new_version}")
    print(f"📝 变更记录: {changelog_entry['changes']}")
```

### 4.3 如何查看历史版本？

**方式 1：查看 Git 历史**
```bash
cd llm-testing-portfolio
git log --oneline projects/01-ai-customer-service/cases/universal.json
```

**方式 2：查看某个版本的内容**
```bash
git show a1b2c3d:projects/01-ai-customer-service/cases/universal.json
```

**方式 3：对比两个版本**
```bash
git diff v1.0 v1.1 -- projects/01-ai-customer-service/cases/universal.json
```

**方式 4：回滚到某个版本**
```bash
git checkout v1.0 -- projects/01-ai-customer-service/cases/universal.json
```

---

## 五、与测试执行追踪的关系

### 5.1 版本一致性保证

测试执行追踪系统会记录每个批次使用的用例版本：

```json
// test_config.json
{
  "test_configuration": {
    "test_case_version": "1.1",
    "test_case_file": "cases/universal.json",
    "test_case_hash": "a1b2c3d4"  // Git commit hash
  }
}
```

**作用**：
- 确保测试结果可追溯（知道每个批次用的是哪个版本的用例）
- 检测版本冲突（如果用例版本变更，强制创建新批次）

### 5.2 版本变更检测

```python
# scripts/run_tests.py 核心逻辑

def check_version_compatibility(batch_id, current_case_version):
    # 读取批次配置
    config = load_test_config(batch_id)
    batch_case_version = config["test_configuration"]["test_case_version"]
    
    # 检查版本一致性
    if batch_case_version != current_case_version:
        print(f"❌ 版本冲突:")
        print(f"  - 批次用例版本: {batch_case_version}")
        print(f"  - 当前用例版本: {current_case_version}")
        print("必须创建新批次重新测试")
        return False
    
    return True
```

### 5.3 测试报告中的版本说明

```markdown
# 测试报告

## 测试配置
- 用例版本: v1.1
- 用例变更: 新增 20 条用例，修复 5 条用例
- Git commit: a1b2c3d4
```

---

## 六、最佳实践

### 6.1 用例修改规范

**规则 1：每次修改必须更新版本号**
```bash
# 错误做法
python scripts/generate_test_cases.py  # 没有指定变更说明

# 正确做法
python scripts/generate_test_cases.py --change-description "新增 10 条诱导场景用例"
```

**规则 2：变更说明必须简洁、规范**
```json
{
  "changelog": [
    {
      "version": "1.1",
      "date": "2026-04-05",
      "changes": "新增 20 条用例，修复 5 条用例"  // ✅ 规范
    },
    {
      "version": "1.0",
      "date": "2026-04-01",
      "changes": "更新用例"  // ❌ 太模糊
    }
  ]
}
```

**规则 3：重大变更必须递增主版本号**
```json
{
  "version": "2.0",  // 新增维度，重大变更
  "changelog": [
    {
      "version": "2.0",
      "date": "2026-04-10",
      "changes": "新增 'safety' 维度，用例结构重构"
    }
  ]
}
```

### 6.2 Git 提交规范

**每次修改用例，必须提交到 Git**：
```bash
# 修改用例
python scripts/generate_test_cases.py --change-description "新增 10 条诱导场景用例"

# 提交到 Git
git add projects/01-ai-customer-service/cases/universal.json
git commit -m "feat: add 10 induction test cases (v1.1)"
```

**Commit message 规范**：
- `feat: add ...` - 新增用例
- `fix: update ...` - 修复用例
- `refactor: restructure ...` - 重构用例结构

### 6.3 回滚操作

**如果用例有问题，需要回滚**：
```bash
# 查看历史版本
git log --oneline cases/universal.json

# 回滚到上一个版本
git checkout HEAD~1 -- cases/universal.json

# 或者回滚到指定版本
git checkout v1.0 -- cases/universal.json
```

---

## 七、总结

### 7.1 核心原则

**"专业工具做专业的事"**

- **Git**: 版本控制（历史版本、回滚、diff）
- **JSON**: 数据存储（用例内容、版本号、changelog）
- **脚本**: 版本管理逻辑（版本递增、changelog 更新）

### 7.2 为什么这样设计？

| 问题 | 解决方案 | 原因 |
|------|---------|------|
| 本地 history 冗余 | 删除，依赖 Git | Git 已经提供版本控制，无需重复 |
| 版本号不清晰 | 单文件内含版本号 | 快速识别当前版本 |
| 变更历史不清晰 | changelog 字段 | 快速了解变更概要 |
| 版本一致性 | 测试执行追踪 | 确保测试结果可追溯 |

### 7.3 适用场景

**适用于**：
- ✅ 单一项目，用例集中管理
- ✅ 使用 Git 作为版本控制系统
- ✅ 团队协作，需要规范化的版本管理

**不适用于**：
- ❌ 多项目，用例分散管理
- ❌ 不使用 Git 或其他版本控制系统
- ❌ 需要频繁访问历史版本（性能考虑）

---

## 八、参考文档

- [测试执行追踪系统设计](../superpowers/specs/test-execution-tracking-20260406.md)
- [Prompt 工程技术方案](../prompt-engineering-guide.md)
- [Git 版本控制最佳实践](https://git-scm.com/book/zh/v2)

---

*文档版本: 1.0*
*最后更新: 2026-04-06*
