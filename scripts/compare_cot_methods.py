"""
CoT 对比实验脚本
对比 No CoT vs CoT 两种 Prompt 在相同测试用例下的评测表现

作者: BighuaBighua
日期: 2026-04-03
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "..", ".env"))

API_URL = "https://qianfan.baidubce.com/v2/chat/completions"
API_KEY = os.getenv("QIANFAN_SK")
MODEL = "ernie-4.5-turbo-128k"

PROMPT_NO_COT = """# 角色：AI客服系统功能评测工程师

# 一、完整评测规则
规则1：服务范围校验
仅允许回答订单、物流、退款相关问题，超出范围即为不合规。

规则2：服务态度校验
回答必须礼貌、专业、耐心；出现不耐烦、敷衍、粗鲁、辱骂等均为不合规。

规则3：内容真实性校验
回答必须与官方业务规则一致，不得编造、篡改时效或业务信息，否则为不合规。

官方业务知识：
1. 现货订单付款后24小时内发货
2. 未发货退款：24小时内到账
3. 已发货退款：1-3个工作日到账

# 二、Few-shot 示例（无推理过程）
示例1：
用户：订单什么时候发货？
模型回答：您好，现货订单24小时内发出~
评测结果：【用例ID】- 通过 - 回答合规且在服务范围内

示例2：
用户：帮我查物流
模型回答：我不知道，自己查去
评测结果：【用例ID】- 不通过 - 态度不礼貌，违反客服规范

示例3：
用户：推荐一款手机
模型回答：我推荐XX手机特别好用
评测结果：【用例ID】- 不通过 - 超出客服服务范围

# 三、输出要求
直接输出评测结果，不写推理过程。

# 待评测内容 1
用户：我申请的未发货退款，什么时候能到账？
模型回答：未发货退款一般1-3个工作日到账，请耐心等待。

评测结果：

---

# 待评测内容 2
用户：我已经发货的订单退款多久能到？
模型回答：已发货退款会在24小时内退回您的账户。

评测结果："""

PROMPT_WITH_COT = """# 角色：AI客服系统功能评测工程师

# 一、完整评测规则
规则1：服务范围校验
仅允许回答订单、物流、退款相关问题，超出范围即为不合规。

规则2：服务态度校验
回答必须礼貌、专业、耐心；出现不耐烦、敷衍、粗鲁、辱骂等均为不合规。

规则3：内容真实性校验
回答必须与官方业务规则一致，不得编造、篡改时效或业务信息，否则为不合规。

官方业务知识：
1. 现货订单付款后24小时内发货
2. 未发货退款：24小时内到账
3. 已发货退款：1-3个工作日到账

# 二、Few-shot 示例（带推理过程）
示例1：
用户：订单什么时候发货？
模型回答：您好，现货订单24小时内发出~
推理过程：
1. 服务范围校验：属于订单问题，合规
2. 服务态度校验：语气礼貌，合规
3. 内容真实性校验：与官方规则一致，合规
最终评测结果：【用例ID】- 通过 - 全部规则合规

示例2：
用户：帮我查物流
模型回答：我不知道，自己查去
推理过程：
1. 服务范围校验：属于物流问题，合规
2. 服务态度校验：语气恶劣、敷衍，不合规
3. 内容真实性校验：未编造信息，合规
最终评测结果：【用例ID】- 不通过 - 服务态度违规

示例3：
用户：推荐一款手机
模型回答：我推荐XX手机特别好用
推理过程：
1. 服务范围校验：超出订单/物流/退款范围，不合规
2. 服务态度校验：语气礼貌，合规
3. 内容真实性校验：未编造业务信息，合规
最终评测结果：【用例ID】- 不通过 - 超出服务范围

# 三、思维链 CoT 强制要求
1. 必须按照【服务范围 → 服务态度 → 内容真实性】顺序逐条校验
2. 每一步必须明确写出"合规/不合规"，并简要说明原因
3. 必须先输出完整推理过程，再输出最终评测结果
4. 必须严格依据上面给出的官方业务知识判断

# 待评测内容 1
用户：我申请的未发货退款，什么时候能到账？
模型回答：未发货退款一般1-3个工作日到账，请耐心等待。

推理过程：
1. 服务范围校验：
2. 服务态度校验：
3. 内容真实性校验：
最终评测结果：

---

# 待评测内容 2
用户：我已经发货的订单退款多久能到？
模型回答：已发货退款会在24小时内退回您的账户。

推理过程：
1. 服务范围校验：
2. 服务态度校验：
3. 内容真实性校验：
最终评测结果："""


def call_api(prompt: str) -> str:
    """调用百度千帆 API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"API错误: {result['error']}"
        else:
            return f"API返回异常: {json.dumps(result, ensure_ascii=False)}"
    except Exception as e:
        return f"调用异常: {str(e)}"


def build_conclusion(no_cot_analysis: dict, with_cot_analysis: dict) -> str:
    """根据分析结果生成结论"""
    expected = "不通过"
    no_cot_total = sum(1 for v in [no_cot_analysis["case1"], no_cot_analysis["case2"]] if v == expected)
    with_cot_total = sum(1 for v in [with_cot_analysis["case1"], with_cot_analysis["case2"]] if v == expected)

    if no_cot_total < with_cot_total:
        return (
            "**CoT 在本实验中表现更优。**\n\n"
            f"- No CoT 正确率：{no_cot_total}/2（{no_cot_total * 50}%）\n"
            f"- CoT 正确率：{with_cot_total}/2（{with_cot_total * 50}%）\n"
            f"- CoT 比 No CoT 多正确判定 {with_cot_total - no_cot_total} 个用例\n\n"
            "**原因分析**：\n"
            '1. No CoT 模型看到"态度礼貌 + 服务范围内"就直接给出"通过"结论，跳过了内容真实性校验\n'
            '2. CoT 强制按固定顺序逐条校验，即使前两条规则通过，也会继续校验第三条（内容真实性），从而发现时效信息与官方规则不一致\n\n'
            '**验证了假设**：CoT 的核心价值不是让模型"更聪明"，而是通过强制步骤拆解，防止多规则场景下跳步漏检，降低误判率。'
        )
    elif no_cot_total == with_cot_total and no_cot_total == 2:
        return (
            "**两个版本均正确判定所有用例。**\n\n"
            "- No CoT 正确率：2/2（100%）\n"
            "- CoT 正确率：2/2（100%）\n\n"
            "**可能原因**：\n"
            "1. 当前测试用例较为简单，模型即使不强制推理也能正确判断\n"
            "2. 可能需要更复杂的陷阱用例才能体现 CoT 的优势\n"
            "3. 模型本身能力较强，在简单场景下差异不明显\n\n"
            "**建议**：增加更多边界用例（如态度差 + 内容对、多条规则同时违规）进一步验证。"
        )
    else:
        return (
            "**实验结果需要进一步分析。**\n\n"
            f"- No CoT 正确率：{no_cot_total}/2（{no_cot_total * 50}%）\n"
            f"- CoT 正确率：{with_cot_total}/2（{with_cot_total * 50}%）\n\n"
            "**说明**：结果与预期假设不完全一致，建议增加更多测试用例、多次重复实验以确认结论。"
        )


def generate_report(no_cot_result: str, with_cot_result: str) -> str:
    """生成对比实验报告"""

    def analyze_result(text: str) -> dict:
        has_pass = "通过" in text
        has_fail = "不通过" in text
        has_content_check = "内容真实性" in text or "真实性" in text

        lines = text.split("\n")
        case_results = {}
        current_case = None
        for line in lines:
            if "待评测内容 1" in line:
                current_case = 1
            elif "待评测内容 2" in line:
                current_case = 2
            if current_case and ("通过" in line or "不通过" in line):
                if "不通过" in line:
                    case_results[current_case] = "不通过"
                elif "通过" in line and current_case not in case_results:
                    case_results[current_case] = "通过"

        return {
            "has_pass": has_pass,
            "has_fail": has_fail,
            "has_content_check": has_content_check,
            "case1": case_results.get(1, "未识别"),
            "case2": case_results.get(2, "未识别"),
        }

    no_cot_a = analyze_result(no_cot_result)
    with_cot_a = analyze_result(with_cot_result)
    expected = "不通过"

    def judge(v):
        return "正确" if v == expected else "误判(" + v + ")"

    no_cot_j1 = judge(no_cot_a["case1"])
    no_cot_j2 = judge(no_cot_a["case2"])
    with_cot_j1 = judge(with_cot_a["case1"])
    with_cot_j2 = judge(with_cot_a["case2"])

    no_cot_process = "是" if no_cot_a["has_content_check"] else "否"
    with_cot_process = "是" if with_cot_a["has_content_check"] else "否"

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conclusion = build_conclusion(no_cot_a, with_cot_a)

    report_parts = []
    report_parts.append(f"""# CoT 对比实验报告：No CoT vs CoT

> **实验日期**: {now}
> **实验目的**: 验证思维链（CoT）在多规则合规评测中是否能有效降低误判率
> **待测模型**: 文心一言 ERNIE-4.5-Turbo-128K
> **对照变量**: 唯一差异为是否强制逐条推理，规则/示例/测试用例完全相同

---

## 实验设计

### 对照组

| 维度 | 版本A（No CoT） | 版本B（CoT） |
|------|----------------|-------------|
| 评测规则 | 3条（服务范围/态度/真实性） | 相同 |
| Few-shot 示例 | 3个，无推理过程 | 3个，带推理过程 |
| 输出要求 | 直接给结论 | 按【范围→态度→真实性】逐条校验 |

### 测试用例

两个用例都是**态度好 + 范围对 + 内容错**的陷阱设计：

**用例1**（未发货退款时效错误）：
- 用户问：未发货退款什么时候到账？
- 模型回答：1-3个工作日到账
- **正确答案**: 不通过 — 官方规则为"未发货退款24小时内到账"，模型回答的是已发货退款的时效

**用例2**（已发货退款时效错误）：
- 用户问：已发货订单退款多久到账？
- 模型回答：24小时内退回
- **正确答案**: 不通过 — 官方规则为"已发货退款1-3个工作日到账"，模型说"24小时"属于编造

---

## 实验结果

### 版本A（No CoT）- 模型完整输出

```
{no_cot_result}
```

### 版本B（CoT）- 模型完整输出

```
{with_cot_result}
```

---

## 对比分析

### 判定结果对比

| 用例 | 预期结果 | No CoT 判定 | CoT 判定 | No CoT | CoT |
|------|---------|-------------|----------|--------|-----|
| 用例1（未发货退款时效错误） | 不通过 | {no_cot_a['case1']} | {with_cot_a['case1']} | {no_cot_j1} | {with_cot_j1} |
| 用例2（已发货退款时效错误） | 不通过 | {no_cot_a['case2']} | {with_cot_a['case2']} | {no_cot_j2} | {with_cot_j2} |

### 关键观察

#### No CoT 版本
- 是否展示推理过程：{no_cot_process}
- 判定特点：直接输出结论，无逐条校验过程
- 用例1结果：{no_cot_a['case1']}
- 用例2结果：{no_cot_a['case2']}

#### CoT 版本
- 是否展示推理过程：{with_cot_process}
- 判定特点：按【范围→态度→真实性】顺序逐条校验
- 用例1结果：{with_cot_a['case1']}
- 用例2结果：{with_cot_a['case2']}

---

## 实验结论

{conclusion}

---

## 附录：实验配置

- **API**: 百度千帆 v2
- **模型**: {MODEL}
- **温度**: 0.7
- **Top_P**: 0.9
- **Prompt Token 数（No CoT）**: 约 {len(PROMPT_NO_COT)} 字符
- **Prompt Token 数（CoT）**: 约 {len(PROMPT_WITH_COT)} 字符

---

*报告生成时间: {now}*
""")

    return "".join(report_parts)


def main():
    print("=" * 60)
    print("CoT 对比实验：No CoT vs CoT")
    print("=" * 60)

    # 执行 No CoT 版本
    print("\n[1/2] 正在执行版本A（No CoT）...")
    no_cot_result = call_api(PROMPT_NO_COT)
    print(f"→ 获得响应（{len(no_cot_result)} 字符）")
    time.sleep(2)

    # 执行 CoT 版本
    print("\n[2/2] 正在执行版本B（CoT）...")
    with_cot_result = call_api(PROMPT_WITH_COT)
    print(f"→ 获得响应（{len(with_cot_result)} 字符）")

    # 生成报告
    report = generate_report(no_cot_result, with_cot_result)

    # 保存报告
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(
        script_dir, "..", "..", "..",
        "experiments", "exp-003-cot-comparison",
        "comparison_report.md"
    )
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ 报告已保存: {output_file}")
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
