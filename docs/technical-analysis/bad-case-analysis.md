# Bad Case 分析文档

> **文档版本**: 1.0
> **创建日期**: 2026-04-06
> **适用场景**: 系统分析测试失败的用例

---

## 📖 什么是 Bad Case

**Bad Case** 是指测试不通过的用例，代表模型表现不佳的场景。

**重要性**：
- 反映模型的薄弱环节
- 提供优化方向的依据
- 验证修复效果的标准

---

## 📊 Bad Case 收集方法

### 方法1：从测试报告中提取

```bash
# 提取所有不通过的用例
grep -A 30 "测试状态: 不通过" \
  projects/01-ai-customer-service/results/batch-004/summary.md
```

**输出示例**：

```
### TC-ACC-005 - accuracy

**测试状态**: 不通过

**用户提问**:
XX信息变更需要满足什么条件？

**客服回答**:
您可以在任何情况下变更XX信息...

**违规说明**: 准确性-事实错误-变更条件描述不准确
```

---

### 方法2：从 results.json 提取

```python
import json

# 读取结果文件
with open('results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 提取 Bad Case
bad_cases = [
    r for r in results 
    if r['evaluation_result']['status'] == '不通过'
]

# 输出统计
print(f"总数: {len(results)}")
print(f"Bad Case 数: {len(bad_cases)}")
print(f"通过率: {(1 - len(bad_cases)/len(results)) * 100:.1f}%")

# 输出 Bad Case 详情
for case in bad_cases:
    print(f"\nID: {case['id']}")
    print(f"维度: {case['dimension']}")
    print(f"问题: {case['evaluation_result']['issues']}")
```

---

### 方法3：使用脚本自动收集

**创建脚本**: `scripts/collect_bad_cases.py`

```python
#!/usr/bin/env python3
"""
收集 Bad Case 并生成分析报告

用法:
    python3 scripts/collect_bad_cases.py --batch-id batch-004
"""

import json
import argparse
from collections import Counter
from datetime import datetime

def collect_bad_cases(results_file):
    """收集 Bad Case"""
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    bad_cases = [
        r for r in results 
        if r['evaluation_result']['status'] == '不通过'
    ]
    
    return bad_cases, len(results)

def analyze_bad_cases(bad_cases):
    """分析 Bad Case"""
    # 按维度统计
    dimension_count = Counter([c['dimension'] for c in bad_cases])
    
    # 按问题类型统计
    issue_types = []
    for case in bad_cases:
        issues = case['evaluation_result'].get('issues', [])
        issue_types.extend(issues)
    issue_count = Counter(issue_types)
    
    return dimension_count, issue_count

def generate_report(bad_cases, dimension_count, issue_count, output_file):
    """生成分析报告"""
    report = f"""# Bad Case 分析报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **Bad Case 数**: {len(bad_cases)}

---

## 📊 维度分布

| 维度 | 数量 | 占比 |
|------|------|------|
"""
    
    total = sum(dimension_count.values())
    for dim, count in dimension_count.most_common():
        pct = count / total * 100
        report += f"| {dim} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 📈 问题类型分布

| 问题类型 | 数量 | 占比 |
|---------|------|------|
"""
    
    for issue, count in issue_count.most_common():
        pct = count / total * 100
        report += f"| {issue} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 📝 Bad Case 详情

"""
    
    for i, case in enumerate(bad_cases, 1):
        report += f"""### {i}. {case['id']} - {case['dimension']}

**用户提问**:
```
{case['input']}
```

**客服回答**:
```
{case['actual_response'][:200]}...
```

**问题**: {', '.join(case['evaluation_result']['issues'])}

---

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已生成: {output_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-id', required=True)
    args = parser.parse_args()
    
    results_file = f"projects/01-ai-customer-service/results/{args.batch_id}/results.json"
    output_file = f"projects/01-ai-customer-service/results/{args.batch_id}/bad_case_analysis.md"
    
    bad_cases, total = collect_bad_cases(results_file)
    dimension_count, issue_count = analyze_bad_cases(bad_cases)
    generate_report(bad_cases, dimension_count, issue_count, output_file)
    
    print(f"📊 Bad Case 统计:")
    print(f"  - 总用例数: {total}")
    print(f"  - Bad Case 数: {len(bad_cases)}")
    print(f"  - 通过率: {(1 - len(bad_cases)/total) * 100:.1f}%")

if __name__ == "__main__":
    main()
```

**使用方法**:

```bash
python3 scripts/collect_bad_cases.py --batch-id batch-004
```

---

## 🔍 Bad Case 分析框架

### 维度分析

按维度统计 Bad Case 分布：

```python
from collections import Counter

# 统计各维度的 Bad Case 数量
dimension_count = Counter([c['dimension'] for c in bad_cases])

# 输出
for dim, count in dimension_count.most_common():
    print(f"{dim}: {count} 个")
```

**示例输出**：

```
completeness: 3 个
accuracy: 2 个
```

**分析要点**：
- Bad Case 最多的维度是薄弱环节
- 需要重点优化

---

### 问题类型分析

按问题类型分类：

```python
# 提取所有问题类型
issue_types = []
for case in bad_cases:
    issues = case['evaluation_result'].get('issues', [])
    # 解析问题类型：维度-问题类型-具体问题
    for issue in issues:
        parts = issue.split('-')
        if len(parts) >= 2:
            issue_type = f"{parts[0]}-{parts[1]}"
            issue_types.append(issue_type)

# 统计
issue_count = Counter(issue_types)

# 输出
for issue, count in issue_count.most_common():
    print(f"{issue}: {count} 次")
```

**示例输出**：

```
accuracy-事实错误: 3 次
completeness-信息遗漏: 2 次
```

**问题类型映射表**：

| 维度 | 问题类型 | 典型表现 | 可能原因 |
|------|----------|----------|----------|
| accuracy | 事实错误 | 信息与事实不符 | 知识库错误、模型幻觉 |
| accuracy | 编造信息 | 虚构不存在的内容 | 模型幻觉、提示不足 |
| completeness | 信息遗漏 | 缺少关键步骤或信息 | Prompt 未强调完整性 |
| completeness | 操作指引缺失 | 未提供具体操作方法 | Prompt 未要求操作指引 |
| compliance | 超出服务范围 | 提供专业建议 | 角色定位不清晰 |
| compliance | 敏感话题 | 涉及不当内容 | 安全过滤器不足 |
| attitude | 冷漠推诿 | 拒绝提供帮助 | Prompt 角色设定问题 |
| attitude | 态度恶劣 | 使用不当语言 | Prompt 未强调态度要求 |

---

### 根因分析

分析问题根本原因：

#### 原因1：Prompt 设计问题

**表现**：
- 多个用例在同一维度失败
- 问题类型相似

**验证方法**：
```bash
# 查看 Prompt 模板
cat templates/customer-service-evaluator.md
```

**改进方案**：
1. 添加 Few-shot 示例
2. 明确输出格式要求
3. 强化关键规则

---

#### 原因2：模型能力问题

**表现**：
- 知识库缺失导致的错误
- 推理能力不足

**验证方法**：
```bash
# 测试其他模型
# 修改 config.py 中的 MODEL_UNDER_TEST
```

**改进方案**：
1. 补充知识库
2. 调整温度参数
3. 切换更强模型

---

#### 原因3：用例设计问题

**表现**：
- 用例过于复杂
- 输入不明确

**验证方法**：
```bash
# 查看用例详情
cat projects/01-ai-customer-service/cases/universal.json | jq '.cases.accuracy[]'
```

**改进方案**：
1. 简化用例输入
2. 明确预期输出
3. 调整评测标准

---

## 📈 改进建议

### 针对 Prompt 优化

#### 问题：准确性维度问题较多

**改进方案**：

```markdown
# Prompt 优化示例

## 优化前
你是一个专业的AI客服。

## 优化后
你是一个专业的AI客服。请注意：
1. 只提供你确定正确的信息
2. 如果不确定，请明确告知用户"我需要确认一下"
3. 不要编造或猜测任何信息
4. 对于专业问题（法律、医疗、金融），建议用户咨询专业人士

## 示例（Few-shot）
用户：XX信息变更需要什么条件？
客服：XX信息变更需要满足以下条件：
1. 已完成XX注册
2. 提供有效的身份证明
3. 填写变更申请表
如果您需要更详细的信息，我可以为您查询相关资料。
```

---

### 针对模型优化

#### 问题：完整性维度问题较多

**改进方案**：

1. **补充知识库**

```bash
# 添加知识库文件
echo "XX操作完整流程：步骤1-XX，步骤2-XX，步骤3-XX" >> knowledge_base.txt
```

2. **调整温度参数**

```python
# 修改 config.py
API_TEMPERATURE = 0.5  # 降低随机性（原值 0.7）
```

3. **切换更强模型**

```python
# 修改 config.py
MODEL_UNDER_TEST = "ernie-4.8-turbo-256k"  # 更强的模型
```

---

### 针对用例优化

#### 问题：用例设计不合理

**改进方案**：

```json
{
  "id": "TC-ACC-005",
  "dimension": "accuracy",
  "input": "XX信息变更需要满足什么条件？请详细说明",
  "test_purpose": "测试AI是否提供准确的XX信息变更条件",
  "quality_criteria": "准确性：变更条件准确无误，包含注册要求、身份证明、申请表三要素，无事实错误或编造"
}
```

**改进要点**：
1. 明确输入要求（"请详细说明"）
2. 细化质量标准（"包含三要素"）

---

## 📊 效果验证

### 验证方法

1. **修复后重新测试**

```bash
# 使用相同的用例重新测试
python3 scripts/run_tests.py --mode full --report new
```

2. **对比结果**

```bash
# 对比修复前后的通过率
# 修复前: completeness 通过率 80%
# 修复后: completeness 通过率 95%
```

3. **统计改进效果**

```python
# 计算改进幅度
before = 0.80
after = 0.95
improvement = (after - before) / before * 100
print(f"改进幅度: {improvement:.1f}%")  # 输出: 改进幅度: 18.8%
```

---

## 💡 最佳实践

### 1. 定期收集 Bad Case

```bash
# 每次测试后自动收集
python3 scripts/run_tests.py --mode full --report new
python3 scripts/collect_bad_cases.py --batch-id batch-004
```

### 2. 建立 Bad Case 数据库

```bash
# 创建 Bad Case 数据库
mkdir -p docs/bad-cases
python3 scripts/collect_bad_cases.py --batch-id batch-004 \
  --output docs/bad-cases/batch-004.md
```

### 3. 跟踪修复效果

```markdown
# Bad Case 修复记录

## 2026-04-06

### 问题
- completeness 维度通过率 80%

### 原因
- Prompt 未强调完整性要求

### 修复
- 添加完整性强调提示
- 添加 Few-shot 示例

### 效果
- completeness 通过率提升至 95%
- 改进幅度: 18.8%
```

---

## 📚 相关文档

- [测试报告解读指南](../user-guide/report-interpretation.md)
- [中断恢复用户指南](../user-guide/interruption-recovery.md)
- [Prompt 工程设计指南](../prompt-engineering-guide.md)

---

*最后更新: 2026-04-06*
