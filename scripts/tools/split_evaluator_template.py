#!/usr/bin/env python3
"""
评测模板拆分脚本

将 customer-service-evaluator.md 按 SECTION 标记拆分为独立文件，
存放到 templates/evaluator-sections/ 目录下。
"""

import re
import sys
from pathlib import Path

SECTIONS_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "evaluator-sections"
SOURCE_FILE = Path(__file__).resolve().parent.parent.parent / "templates" / "customer-service-evaluator.md"

SECTION_PATTERN = re.compile(r"<!-- SECTION:(\w+) -->")


def split_template(source_path: Path = SOURCE_FILE, output_dir: Path = SECTIONS_DIR):
    """将完整版评测模板按 SECTION 标记拆分为独立文件

    解析 customer-service-evaluator.md 中的 <!-- SECTION:xxx --> 标记，
    将每个section的内容提取为独立的 .md 文件，供 EvaluatorPromptAssembler 按需加载。

    Args:
        source_path: 源模板文件路径（默认为 templates/customer-service-evaluator.md）
        output_dir: 输出目录路径（默认为 templates/evaluator-sections/）
    """
    content = source_path.read_text(encoding="utf-8")

    sections = {}
    current_name = None
    current_lines = []

    for line in content.split("\n"):
        match = SECTION_PATTERN.match(line.strip())
        if match:
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines).strip() + "\n"
            current_name = match.group(1)
            current_lines = []
        else:
            if current_name is not None:
                current_lines.append(line)

    if current_name is not None:
        sections[current_name] = "\n".join(current_lines).strip() + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)

    for name, body in sections.items():
        out_file = output_dir / f"{name}.md"
        out_file.write_text(body, encoding="utf-8")
        print(f"  ✅ {out_file.name} ({len(body)} chars)")

    print(f"\n拆分完成: {len(sections)} 个 section → {output_dir}")


if __name__ == "__main__":
    split_template()
