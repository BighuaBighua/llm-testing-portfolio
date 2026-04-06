#!/usr/bin/env python3
"""
文档生成器 - 自动生成项目文档

功能：
1. 从 project_data.json 读取数据
2. 自动更新 README.md 的脚本列表部分
3. 自动生成 scripts/README.md

使用方法：
python tools/generate_docs.py [--auto-update]
"""

import json
import re
from pathlib import Path
from datetime import datetime
import sys


def load_project_data():
    """加载项目数据"""
    data_file = Path(__file__).parent.parent / ".codebuddy" / "project_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_scripts_table(scripts):
    """生成脚本列表表格（用于 README.md）"""
    table = "| 脚本 | 功能 | 状态 |\n|------|------|------|\n"
    for script in scripts:
        status = script['status']
        if status == '推荐':
            status_str = f"{status}"
        else:
            status_str = f"{status} 已验证"
        
        if script.get('api_integrated'):
            status_str += ' | ✅ 文心一言 API 已集成'
        table += f"| {script['name']} | {script['description']} | {status_str} |\n"
    return table


def generate_scripts_tree(scripts):
    """生成脚本目录树（用于 README.md）"""
    tree = "scripts/\n"
    
    for i, script in enumerate(scripts):
        prefix = "└──" if i == len(scripts) - 1 else "├──"
        tree += f"{prefix} {script['name']:30} # {script['description']}\n"
    
    return tree


def generate_scripts_readme_content(data):
    """生成 scripts/README.md 的完整内容"""
    scripts = data['scripts']
    
    content = """# 自动化脚本目录

> 所有自动化测试和工具脚本

---

## 📋 脚本列表:

"""
    
    for script in scripts:
        status = script['status'] if script['status'] not in ['✅', '推荐'] else f"{script['status']} 已验证"
        content += f"### {script['name']} {status}\n\n"
        content += f"**功能**:\n"
        for feature in script['features']:
            content += f"- {feature}\n"
        content += f"\n**使用方法**:\n```bash\npython3 {script['name']}\n```\n\n"
        
        # 如果有详细指南，展开说明
        if script.get('detailed_guide'):
            guide = script['detailed_guide']
            
            # 核心特点
            if guide.get('core_features'):
                content += "#### 核心特点\n\n"
                for feature in guide['core_features']:
                    content += f"**{feature['title']}**: {feature['description']}\n"
                    for detail in feature['details']:
                        content += f"- {detail}\n"
                    content += "\n"
            
            # 使用步骤
            if guide.get('usage_steps'):
                content += "#### 使用步骤\n\n"
                for step in guide['usage_steps']:
                    content += f"**步骤{step['step']}: {step['title']}**\n\n{step['content']}\n\n"
            
            # 配置说明
            if guide.get('config'):
                config = guide['config']
                content += f"#### {config['title']}\n\n{config['description']}\n\n{config['table']}\n\n"
                if config.get('custom_note'):
                    content += f"💡 {config['custom_note']}\n\n"
            
            # 示例
            if guide.get('examples'):
                content += "#### 用例示例\n\n"
                for example in guide['examples']:
                    content += f"**{example['type']}**:\n```json\n{example['code']}\n```\n\n"
            
            # 注意事项
            if guide.get('notes'):
                content += "#### 注意事项\n\n"
                for note in guide['notes']:
                    content += f"- {note}\n"
                content += "\n"
            
            # 后续步骤
            if guide.get('next_steps'):
                content += "#### 后续步骤\n\n"
                for i, step in enumerate(guide['next_steps'], 1):
                    content += f"{i}. ✅ {step}\n"
                content += "\n"
        
        content += "---\n\n"
    
    content += """## 🎯 脚本设计原则

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

"""
    
    # 添加历史版本说明（如果有）
    if data.get('deprecated_scripts'):
        content += "## 📜 历史版本\n\n"
        for script in data['deprecated_scripts']:
            content += f"> **{script['name']}** 已移至 `{script['archive_path']}`\n"
            content += f">\n"
            content += f"> 废弃原因：{script['reason']}\n"
            content += f">\n"
            content += f"> 建议使用 `{script['replacement']}`\n\n"
        content += "---\n\n"
    
    # 添加文档生成器使用指南
    content += """## 🔧 文档生成器使用指南

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

"""
    
    content += f"*最后更新: {data['project']['last_updated']}*\n"
    
    return content


def update_readme_automatically(data, auto_update=False):
    """自动更新 README.md 的脚本列表部分"""
    readme_path = Path(__file__).parent.parent / "README.md"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的脚本表格
    new_table = generate_scripts_table(data['scripts'])
    
    # 使用正则表达式找到脚本列表部分并替换
    pattern = r'### 自动化评测脚本\n\n\| 脚本 \| 功能 \| 状态 \|\n\|------\|------\|------\|\n.*?\n\n\*\*路径\*\*: `scripts/`'
    
    replacement = f'### 自动化评测脚本\n\n{new_table}\n**路径**: `scripts/`'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if auto_update:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 已自动更新: {readme_path}")
    else:
        print("=== README.md 脚本列表表格 ===")
        print(new_table)
        print()


def generate_templates_tree(templates):
    """生成模板目录树（用于 README.md）"""
    tree = "templates/\n"
    
    for i, template in enumerate(templates):
        prefix = "└──" if i == len(templates) - 1 else "├──"
        tree += f"{prefix} {template['name']:30} # {template['description']} ✅ 已验证\n"
    
    return tree


def generate_scripts_readme(data):
    """生成 scripts/README.md"""
    scripts_readme_path = Path(__file__).parent.parent / "scripts" / "README.md"
    
    content = generate_scripts_readme_content(data)
    
    with open(scripts_readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已生成: {scripts_readme_path}")


def check_naming_conventions():
    """检查项目文件命名规范"""
    from pathlib import Path
    
    violations = []
    project_root = Path(__file__).parent.parent
    
    # Python 文件常见动词
    common_verbs = [
        'generate', 'run', 'compare', 'setup', 'build', 'test', 'create', 
        'update', 'delete', 'get', 'set', 'add', 'remove', 'check', 'validate',
        'parse', 'format', 'convert', 'extract', 'load', 'save', 'read', 'write',
        'process', 'execute', 'init', 'start', 'stop', 'fix', 'resolve', 'handle',
        'manage', 'configure', 'install', 'deploy', 'publish', 'download', 'upload'
    ]
    
    # 检查 scripts/ 目录
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        for file in scripts_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            # 检查是否以下划线分隔
            if "-" in file.name:
                violations.append(f"❌ scripts/{file.name} - Python 文件应用下划线,不是连字符")
            
            # 检查是否以常见动词开头
            name_without_ext = file.stem
            first_word = name_without_ext.split('_')[0] if '_' in name_without_ext else name_without_ext
            if first_word not in common_verbs:
                violations.append(f"⚠️  scripts/{file.name} - 建议以动词开头 (当前: {first_word})")
    
    # 检查 tools/ 目录
    tools_dir = project_root / "tools"
    if tools_dir.exists():
        for file in tools_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            # 检查是否以下划线分隔
            if "-" in file.name:
                violations.append(f"❌ tools/{file.name} - Python 文件应用下划线,不是连字符")
            
            # 检查是否以常见动词开头
            name_without_ext = file.stem
            first_word = name_without_ext.split('_')[0] if '_' in name_without_ext else name_without_ext
            if first_word not in common_verbs:
                violations.append(f"⚠️  tools/{file.name} - 建议以动词开头 (当前: {first_word})")
    
    # Markdown 文件规范: 连字符分隔
    templates_dir = project_root / "templates"
    if templates_dir.exists():
        for file in templates_dir.glob("*.md"):
            if file.name == "README.md":
                continue
            
            # 检查是否用下划线(应该用连字符)
            if "_" in file.stem:
                violations.append(f"⚠️  templates/{file.name} - Markdown 文件建议用连字符 (如: {file.stem.replace('_', '-')}.md)")
    
    return violations


def main():
    """主函数"""
    # 检查是否有 --auto-update 参数
    auto_update = '--auto-update' in sys.argv
    
    print("=" * 60)
    print("文档生成器")
    if auto_update:
        print("模式: 自动更新")
    print("=" * 60)
    print()
    
    # 加载项目数据
    print("📂 加载项目数据...")
    data = load_project_data()
    print(f"✅ 已加载: {len(data['scripts'])} 个脚本")
    print()
    
    # 生成各部分内容
    print("📝 生成文档内容...\n")
    
    # 1. 更新 README.md
    update_readme_automatically(data, auto_update)
    
    # 2. 生成 scripts/README.md
    generate_scripts_readme(data)
    
    print()
    print("=" * 60)
    print("✅ 文档生成完成！")
    print("=" * 60)
    print()
    
    # 检查命名规范
    print("🔍 检查命名规范...")
    violations = check_naming_conventions()
    
    if violations:
        print()
        print("⚠️  发现命名规范问题:")
        print("-" * 60)
        for violation in violations:
            print(violation)
        print()
        print("💡 参考规范: AI_CODING_RULES.md")
        print("-" * 60)
    else:
        print("✅ 所有文件命名符合规范")
    
    print()
    
    if not auto_update:
        print("💡 使用提示：")
        print("1. README.md 的脚本列表需要手动替换")
        print("2. scripts/README.md 已自动生成")
        print("3. 使用 --auto-update 参数可以自动更新所有文档")
        print()
        print("示例：")
        print("  python tools/generate_docs.py              # 生成内容，手动替换")
        print("  python tools/generate_docs.py --auto-update # 自动更新所有文档")


if __name__ == "__main__":
    main()
