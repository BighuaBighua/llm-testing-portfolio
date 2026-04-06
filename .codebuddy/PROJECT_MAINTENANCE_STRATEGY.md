# 项目维护策略 - 智者视角

**审视时间**: 2026-04-05 15:15
**核心问题**: 文件清理、脚本归档、自动更新机制

---

## 一、剥离噪声：核心问题是什么？

**你的困惑**：
1. 过时的文件是否需要清理到 archive？
2. 过时的脚本是否需要移动？
3. 能否建立自动更新机制？

**物理本质**：
> 这些问题的核心是"熵增定律"——项目会自然变乱，需要持续投入能量来维持秩序。

**三个层次**：
1. **物理层**：文件和脚本的实际位置
2. **信息层**：文档和代码的一致性
3. **机制层**：自动化维护流程

---

## 二、逐个问题诊断

### 问题1：过时的文件是否需要清理到 archive？

**当前状态**：
```
llm-testing-portfolio/
├── .env                                ❌ 根目录配置（已在 .gitignore）
├── archive/                            ✅ 归档目录已建立
│   └── historical-experiments/         ✅ 历史实验已归档
├── docs/                               ✅ 已清理冗余文档
├── projects/                           ✅ README.md 已更新
└── templates/                          ✅ 已更新路径
```

**诊断结果**：
- ✅ **主要问题已解决**：历史实验已归档
- ✅ **根目录 .env**：已在 .gitignore，不会提交 Git
- ✅ **文档已清理**：删除了 roadmap.md

**结论**：
> **不需要额外清理。当前状态已经很好。**

**心法**：
> "归档不是删除，是尊重历史。但不要过度归档，只归档有价值的历史实验。"

---

### 问题2：过时的脚本是否需要移动？

**当前状态**：
```
scripts/
├── automated_test.py                   ⚠️ 旧版脚本（还在使用）
├── cot_comparison.py                   ✅ 实验脚本
├── generate_test_cases.py              ✅ 新脚本
├── GUIDE.md                            ✅ 使用指南
├── README.md                           ✅ 脚本说明
└── run_tests.py                        ✅ 新脚本（推荐）
```

**诊断结果**：

**第一性原理提问**：
1. "automated_test.py 真的是'过时'吗？"
   - ❌ 不是！它仍然可以运行，只是有更好的替代方案
   - 它是"旧版"，不是"废弃版"

2. "如果移动到 archive，会发生什么？"
   - ❌ 会破坏向后兼容性
   - ❌ 如果有人用了旧脚本，会找不到
   - ❌ 文档中的"旧版"标注会失效

3. "保留在 scripts/ 的好处是什么？"
   - ✅ 向后兼容
   - ✅ 可以对比新旧脚本
   - ✅ 学习演进历史

**物理类比**：
```
scripts/ 就像一个"工具箱"

如果每次买了新工具，就把旧工具扔掉：
- 第一次买锤子 → 用旧了买新的 → 扔掉旧的
- 结果：遇到特殊情况需要旧锤子时，找不到了

正确的做法：
- 保留旧工具，但标注"推荐使用新工具"
- 这样既保持兼容，又引导用户使用更好的方案
```

**结论**：
> **不要移动 automated_test.py。保留在 scripts/，标注为"旧版"即可。**

**理由**：
1. **向后兼容**：已有的使用记录不会失效
2. **学习价值**：可以对比新旧脚本的设计差异
3. **文档一致**：所有文档都标注了"旧版"，移动会破坏一致性
4. **维护成本低**：只是一个文件，不影响项目整洁

**心法**：
> "旧版不是垃圾，是历史。保留它，标注它，但不要隐藏它。"

---

### 问题3：能否建立自动更新机制？

**你的痛点**：
> "每次文件变更，都要手动更新多个文档，容易遗漏。"

**物理本质**：
> 这是"信息同步"问题——当源头变化时，下游信息需要同步更新。

**三种方案对比**：

#### 方案A：手动更新（当前方案）

**流程**：
```
文件变更 → 手动更新 README.md
         → 手动更新 PROJECT_GUIDE.md
         → 手动更新 scripts/README.md
         → 手动更新 templates/README.md
```

**优点**：
- ✅ 简单，无需技术投入
- ✅ 灵活，可以控制每个细节

**缺点**：
- ❌ 容易遗漏（今天的问题）
- ❌ 维护成本高
- ❌ 依赖记忆

---

#### 方案B：半自动化脚本

**设计思路**：
```python
# scripts/update_docs.py

def update_docs():
    """自动更新项目文档"""
    
    # 1. 扫描 scripts/ 目录，生成脚本列表
    scripts = scan_scripts()
    
    # 2. 更新 README.md 的脚本列表
    update_readme_scripts(scripts)
    
    # 3. 更新 PROJECT_GUIDE.md 的脚本列表
    update_project_guide_scripts(scripts)
    
    # 4. 更新 scripts/README.md
    update_scripts_readme(scripts)
    
    print("文档更新完成！")

# 使用方法：
# python scripts/update_docs.py
```

**优点**：
- ✅ 一键更新，减少遗漏
- ✅ 技术成本不高（100行代码）
- ✅ 可定制

**缺点**：
- ⚠️ 需要维护脚本本身
- ⚠️ 只能处理结构化信息（脚本列表、文件数量等）
- ⚠️ 无法处理语义信息（路径变化、归档说明等）

---

#### 方案C：Git Hooks 自动化

**设计思路**：
```bash
# .git/hooks/pre-commit

#!/bin/bash

# 在每次 git commit 前自动运行
python scripts/update_docs.py

# 如果文档有变化，提示用户
if git diff --name-only | grep -q "README.md\|PROJECT_GUIDE.md"; then
    echo "文档已更新，请确认后再次提交"
    exit 1
fi
```

**优点**：
- ✅ 完全自动化
- ✅ 不会遗漏

**缺点**：
- ❌ Git Hooks 不会提交到 Git（每个开发者需要手动配置）
- ❌ 过度工程化（对个人项目来说太重）
- ❌ 可能影响提交速度

---

#### 方案D：文档生成器（最佳方案）

**设计思路**：
```
不要维护多个文档，而是维护一个"数据源"，其他文档引用它。

数据源：.codebuddy/project_data.json
{
  "scripts": [
    {
      "name": "run_tests.py",
      "status": "推荐",
      "description": "批量执行评测用例"
    },
    {
      "name": "automated_test.py",
      "status": "旧版",
      "description": "批量执行评测用例"
    }
  ],
  "test_cases_count": 50,
  "last_updated": "2026-04-05"
}

生成脚本：
python scripts/generate_docs.py

输出：
- README.md（自动生成脚本列表部分）
- PROJECT_GUIDE.md（自动生成脚本列表部分）
- scripts/README.md（自动生成完整内容）
```

**优点**：
- ✅ 单一数据源，不会不一致
- ✅ 一键生成，不会遗漏
- ✅ 可扩展（未来可以加更多数据）

**缺点**：
- ⚠️ 需要维护生成脚本
- ⚠️ 需要手动更新数据源

---

## 三、结构化指引

**心法**：
> "维护成本 = 自动化收益 - 技术投入。如果投入 > 收益，手动更好。"

**策略**：
- **短期（1个月内）**：手动更新 + 检查清单
- **中期（3个月内）**：半自动化脚本（方案B）
- **长期（可选）**：文档生成器（方案D）

**今日微行动**：

### 阶段一：建立检查清单（今天）

创建 `.codebuddy/DOC_UPDATE_CHECKLIST.md`：

```markdown
# 文档更新检查清单

当项目发生以下变更时，请手动更新对应文档：

## 新增脚本时
- [ ] README.md → 脚本列表
- [ ] PROJECT_GUIDE.md → scripts/ 目录结构
- [ ] scripts/README.md → 脚本列表
- [ ] scripts/GUIDE.md → 使用指南（如需要）

## 文件移动/归档时
- [ ] README.md → 项目结构
- [ ] PROJECT_GUIDE.md → 对应目录结构
- [ ] 相关文档的路径引用

## 测试用例变化时
- [ ] README.md → 数据说话部分
- [ ] PROJECT_GUIDE.md → 项目状态
- [ ] projects/README.md → 核心数据

## 项目状态变化时
- [ ] PROJECT_GUIDE.md → 里程碑
- [ ] MY_JOURNEY.md → 添加学习记录

## 更新流程
1. 完成代码变更
2. 打开本检查清单
3. 逐项检查并更新
4. 运行 git status 确认所有文档已更新
```

---

### 阶段二：编写半自动化脚本（本周）

创建 `scripts/update_docs.py`：

```python
#!/usr/bin/env python3
"""
文档自动更新脚本

功能：
1. 扫描 scripts/ 目录，生成脚本列表
2. 更新 README.md 和 PROJECT_GUIDE.md 的脚本列表部分
3. 生成 scripts/README.md

使用方法：
python scripts/update_docs.py
"""

import os
import json
from pathlib import Path

def scan_scripts():
    """扫描 scripts/ 目录，返回脚本列表"""
    scripts_dir = Path("scripts")
    scripts = []
    
    for file in scripts_dir.glob("*.py"):
        # 读取脚本文件的文档字符串
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单提取描述（实际可以更复杂）
            description = file.stem.replace('_', ' ').title()
        
        # 判断状态
        if file.name == "run_tests.py":
            status = "推荐"
        elif file.name == "automated_test.py":
            status = "旧版"
        else:
            status = "✅"
        
        scripts.append({
            "name": file.name,
            "status": status,
            "description": description
        })
    
    return scripts

def update_readme_scripts(scripts):
    """更新 README.md 的脚本列表"""
    # 生成表格
    table = "| 脚本 | 功能 | 状态 |\n|------|------|------|\n"
    for script in scripts:
        table += f"| {script['name']} | {script['description']} | {script['status']} |\n"
    
    # 读取 README.md
    with open("README.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换脚本列表部分（需要定义标记）
    # 这里省略具体实现
    
    print("README.md 已更新")

def update_project_guide_scripts(scripts):
    """更新 PROJECT_GUIDE.md 的脚本列表"""
    # 类似 update_readme_scripts
    pass

def main():
    """主函数"""
    print("开始扫描脚本...")
    scripts = scan_scripts()
    
    print(f"找到 {len(scripts)} 个脚本")
    
    print("更新文档...")
    update_readme_scripts(scripts)
    update_project_guide_scripts(scripts)
    
    print("文档更新完成！")

if __name__ == "__main__":
    main()
```

---

### 阶段三：定期优化（未来）

如果发现手动维护成本仍然很高，可以考虑：
1. 完善半自动化脚本，处理更多场景
2. 引入文档生成器（方案D）
3. 使用 Git Hooks 自动化

---

## 四、金句箴言

> **"熵增定律：项目会自然变乱，需要持续投入能量来维持秩序。"**

> **"旧版不是垃圾，是历史。保留它，标注它，但不要隐藏它。"**

> **"维护成本 = 自动化收益 - 技术投入。如果投入 > 收益，手动更好。"**

> **"先建立检查清单，再考虑自动化。不要在混乱中引入复杂度。"**

> **"向后兼容比完美整洁更重要。不要为了整洁破坏已有的使用记录。"**

---

## 五、决策总结

### ✅ 问题1：过时的文件清理

**决策**：**不需要额外清理**

**理由**：
- 历史实验已归档
- 根目录 .env 已在 .gitignore
- 文档已清理

---

### ✅ 问题2：过时的脚本移动

**决策**：**不要移动 automated_test.py**

**理由**：
- 保留向后兼容
- 标注为"旧版"即可
- 移动会破坏文档一致性

---

### ✅ 问题3：自动更新机制

**决策**：**分阶段实施**

**短期（今天）**：
- 创建检查清单 `.codebuddy/DOC_UPDATE_CHECKLIST.md`

**中期（本周）**：
- 编写半自动化脚本 `scripts/update_docs.py`

**长期（可选）**：
- 引入文档生成器（如果维护成本持续很高）

---

**决策人**: AI 智者
**决策日期**: 2026-04-05
