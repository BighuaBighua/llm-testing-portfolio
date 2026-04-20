"""
项目脚手架脚本 V1.0

功能：
1. 创建新项目的目录结构
2. 生成 project_config.yaml 模板
3. 创建 evaluator-sections 占位文件
4. 创建 cases 和 results 目录
5. 安全维度评估规则自动从共享层链接

使用方式：
  python scripts/init_project.py --name 03-medical-assistant --display "医疗助手"

日期: 2026-04-16
版本: 1.0
"""

import argparse
import os
import sys

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects")

EVALUATOR_SECTIONS = [
    "role.md",
    "rules.md",
    "example.md",
    "fewshot.md",
    "portability.md",
]

SECURITY_EVALUATOR_SECTIONS = [
    "prompt-injection-rules.md",
    "sensitive-topic-rules.md",
    "bias-fairness-rules.md",
]

SHARED_SECTIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates", "evaluator-sections"
)

PROJECT_CONFIG_TEMPLATE = """display_name: "{display_name}"

template_params:
  agent_name: "{display_name}"
  agent_type: "{display_name}"
  service_identity: "{display_name}身份"
  example_domains: "请填写示例领域"

business_scenario:
  name: "{display_name}"
  description: "请填写业务场景描述"
  service_boundaries:
    in_scope:
      - "请填写服务范围内项目1"
      - "请填写服务范围内项目2"
    out_of_scope:
      - "医疗建议"
      - "法律咨询"
      - "投资理财建议"
  constraints:
    - "不提供专业领域建议（医疗、法律、投资等）"
    - "不泄露用户隐私或敏感信息"
    - "不编造不存在的信息"
"""

ROLE_TEMPLATE = """# 角色定义

## 被测AI角色

**名称**: {agent_name}

**身份**: {agent_name}

**职责**: 请填写{agent_name}的主要职责

**服务范围**: 请填写服务范围

**禁止行为**:
1. 不提供专业领域建议（医疗、法律、投资等）
2. 不泄露用户隐私或敏感信息
3. 不编造不存在的信息
"""

RULES_TEMPLATE = """# 评测规则

## 基础评测规则

### 1. 准确性
评估AI回复是否准确、无误。

### 2. 完整性
评估AI回复是否完整、全面。

### 3. 合规性
评估AI回复是否符合规范和约束。

### 4. 态度
评估AI回复的态度是否恰当。

---

## 安全维度评测规则

安全维度（Prompt注入攻击、敏感话题安全防御、偏见公平性）的评测规则
由共享层模板统一提供，变量参数由 project_config.yaml 中的 template_params 注入。

共享层模板位置：templates/evaluator-sections/
- prompt-injection-rules.md
- sensitive-topic-rules.md
- bias-fairness-rules.md
"""

EXAMPLE_TEMPLATE = """# 评测示例

## 标准维度示例

### 示例1：准确性评测
**用户输入**: 请问你们的退货政策是什么？
**AI回复**: 我们的退货政策是7天无理由退货...
**评测**: 通过 - 准确描述了退货政策

## 安全维度示例

安全维度的评测示例由共享层模板提供。
"""

FEWSHOT_TEMPLATE = """# Few-Shot 示例

## 标准维度 Few-Shot

请根据项目实际情况添加 Few-Shot 示例。

## 安全维度 Few-Shot

安全维度的 Few-Shot 示例由共享层模板提供。
"""

PORTABILITY_TEMPLATE = """# 可移植性说明

本项目的评测规则和示例可在同类项目中复用。

## 项目特定配置
- agent_name: {agent_name}
- service_identity: {agent_name}身份

## 共享配置
安全维度评测规则由共享层模板统一管理，通过变量注入适配不同项目。
"""

SECURITY_RULES_NOTE = """# {dimension_cn}评测规则

> 本维度的评测规则由共享层模板统一提供。
> 模板位置: templates/evaluator-sections/{filename}
> 变量参数由 project_config.yaml 中的 template_params 自动注入。
>
> 如需项目级定制，可在此文件中添加覆盖规则。
"""


def create_project(name: str, display_name: str):
    if not name:
        print("❌ 项目名称不能为空")
        return False

    project_dir = os.path.join(PROJECTS_DIR, name)
    if os.path.exists(project_dir):
        print(f"❌ 项目已存在: {project_dir}")
        return False

    print(f"📁 创建项目目录: {project_dir}")
    os.makedirs(project_dir, exist_ok=True)

    os.makedirs(os.path.join(project_dir, "cases", "bad_cases"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "results"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "evaluator-sections"), exist_ok=True)
    print("  ✅ 目录结构已创建")

    config_content = PROJECT_CONFIG_TEMPLATE.format(display_name=display_name)
    config_path = os.path.join(project_dir, "project_config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✅ project_config.yaml 已生成")

    template_params = {"agent_name": display_name}

    section_templates = {
        "role.md": ROLE_TEMPLATE,
        "rules.md": RULES_TEMPLATE,
        "example.md": EXAMPLE_TEMPLATE,
        "fewshot.md": FEWSHOT_TEMPLATE,
        "portability.md": PORTABILITY_TEMPLATE,
    }

    for section_name, template in section_templates.items():
        section_path = os.path.join(project_dir, "evaluator-sections", section_name)
        content = template.format(**template_params)
        with open(section_path, "w", encoding="utf-8") as f:
            f.write(content)
    print("  ✅ 基础 evaluator-sections 已生成")

    security_dimensions = [
        ("prompt-injection-rules.md", "Prompt注入攻击"),
        ("sensitive-topic-rules.md", "敏感话题安全防御"),
        ("bias-fairness-rules.md", "偏见公平性"),
    ]

    for filename, dim_cn in security_dimensions:
        section_path = os.path.join(project_dir, "evaluator-sections", filename)
        content = SECURITY_RULES_NOTE.format(dimension_cn=dim_cn, filename=filename)
        with open(section_path, "w", encoding="utf-8") as f:
            f.write(content)

        shared_path = os.path.join(SHARED_SECTIONS_DIR, filename)
        if os.path.exists(shared_path):
            print(f"  ✅ {filename} (共享层模板已就绪: templates/evaluator-sections/{filename})")
        else:
            print(f"  ⚠️ {filename} (共享层模板未找到，请确认 templates/evaluator-sections/ 下存在此文件)")

    print()
    print(f"🎉 项目 '{name}' 创建成功！")
    print()
    print("📋 后续步骤:")
    print(f"  1. 编辑 {project_dir}/project_config.yaml 填写项目配置")
    print(f"  2. 编辑 {project_dir}/evaluator-sections/ 下的文件定制评测规则")
    print(f"  3. 运行测试: python scripts/run_tests.py --project {name}")
    print()
    print("📌 安全维度说明:")
    print("  - Prompt注入攻击、敏感话题安全防御、偏见公平性的评测规则")
    print("  - 由共享层模板 (templates/evaluator-sections/) 统一提供")
    print("  - 变量参数 (agent_name, service_identity 等) 自动从 project_config.yaml 注入")
    print("  - 如需项目级覆盖，编辑 evaluator-sections/ 下对应文件即可")

    return True


def main():
    parser = argparse.ArgumentParser(description="项目脚手架脚本 - 创建新项目目录结构")
    parser.add_argument("--name", type=str, required=True, help="项目目录名称，如 03-medical-assistant")
    parser.add_argument("--display", type=str, default="", help="项目显示名称，如 医疗助手")

    args = parser.parse_args()

    display_name = args.display or args.name
    create_project(args.name, display_name)


if __name__ == "__main__":
    main()
