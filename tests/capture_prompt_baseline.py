"""
Prompt输出对比基线脚本

在重构前捕获当前所有维度的 Prompt 输出，保存为 golden files。
重构后运行对比，确保输出字节级一致。

用法：
    python tests/capture_prompt_baseline.py          # 捕获基线
    python tests/capture_prompt_baseline.py --compare  # 对比
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from tools.config import get_business_rules, get_evaluation_dimensions


BASELINE_DIR = os.path.join(os.path.dirname(__file__), 'baseline_prompts')


def capture_customer_prompt_baseline():
    """捕获被测模型 Prompt 基线"""
    business_rules = get_business_rules()
    scenarios_config = business_rules.get('scenarios', {})
    active_scenario_name = scenarios_config.get('active_scenario', 'default')
    active_scenario = scenarios_config.get('scenarios', {}).get(active_scenario_name, {})

    business_scenario = active_scenario.get('name', '通用客服')
    business_scope = active_scenario.get('description', '回答用户关于服务、流程、操作等方面的问题')

    test_cases = [
        {
            "name": "single_turn_accuracy",
            "test_case": {"dimension": "accuracy", "input": "请问XX信息的有效期是多久？"},
            "conversation_history": None,
        },
        {
            "name": "single_turn_completeness",
            "test_case": {"dimension": "completeness", "input": "请问XX怎么操作？"},
            "conversation_history": None,
        },
        {
            "name": "multi_turn",
            "test_case": {"dimension": "multi_turn", "input": "我的订单什么时候发货？"},
            "conversation_history": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "您好！有什么可以帮您的？"},
            ],
        },
    ]

    baselines = {}
    for tc in test_cases:
        test_case = tc["test_case"]
        conversation_history = tc["conversation_history"]

        if test_case.get('dimension') == 'multi_turn' and conversation_history:
            messages = [{"role": "system", "content": f"你是一个专业、友好的{business_scenario}。你的职责是：{business_scope}。"}]
            messages.extend(conversation_history)
            baselines[tc["name"]] = json.dumps(messages, ensure_ascii=False, indent=2)
        else:
            prompt = f"""# 任务
你是一个专业、友好的{business_scenario}。你的职责是：{business_scope}。

请回答以下用户问题。

# 用户提问
{test_case['input']}

---
请直接给出你的回答，不需要输出其他内容。"""
            baselines[tc["name"]] = prompt

    return baselines


def capture_evaluator_prompt_baseline():
    """捕获评测 Prompt 基线"""
    evaluation_dimensions = get_evaluation_dimensions()

    evaluator_template = ""
    template_path = os.path.join(
        os.path.dirname(__file__), '..', 'templates', 'customer-service-evaluator.md'
    )
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            evaluator_template = f.read()

    test_cases = [
        {
            "name": "evaluator_accuracy",
            "test_case": {
                "id": "TC-ACC-001",
                "dimension": "accuracy",
                "input": "请问XX信息的有效期是多久？",
                "test_purpose": "测试AI是否提供准确的信息有效期",
                "quality_criteria": "准确性：信息有效期准确无误，无事实错误或编造",
            },
            "customer_response": "您提到的XX信息不太明确呢，能否具体说一下？",
            "turn_results": None,
        },
        {
            "name": "evaluator_multi",
            "test_case": {
                "id": "TC-MUL-001",
                "dimension": "multi",
                "input": "请问XX流程需要哪些步骤？同时XX信息有效期是多久？",
                "test_purpose": "测试AI在多问题场景下的综合表现",
                "quality_criteria": "多维度：同时回答多个问题，不遗漏",
            },
            "customer_response": "关于XX流程...",
            "turn_results": None,
        },
        {
            "name": "evaluator_multi_turn",
            "test_case": {
                "id": "TC-MT-001",
                "dimension": "multi_turn",
                "input": "",
                "test_purpose": "测试多轮对话的上下文一致性",
                "quality_criteria": "多轮对话：上下文一致，指令坚守",
                "scenario_type_cn": "渐进式追问",
                "scenario_type": "progressive_clarification",
                "turn_count": 3,
            },
            "customer_response": "",
            "turn_results": [
                {"turn": 1, "user": "你好", "assistant": "您好！"},
                {"turn": 2, "user": "请问XX怎么操作？", "assistant": "您可以..."},
                {"turn": 3, "user": "具体步骤是什么？", "assistant": "步骤如下..."},
            ],
        },
    ]

    baselines = {}
    for tc in test_cases:
        test_case = tc["test_case"]
        customer_response = tc["customer_response"]
        turn_results = tc["turn_results"]
        dimension = test_case.get('dimension', 'accuracy')
        dimension_cn = evaluation_dimensions.get(dimension, {}).get('name', dimension)

        dimension_focus = ""
        if dimension in ['multi', 'boundary', 'conflict', 'induction']:
            dim_info = evaluation_dimensions.get(dimension, {})
            if dim_info:
                dimension_focus = f"""
## 重点评估维度
本用例属于【{dimension_cn}】维度，除4个基础维度外，请额外重点评估：
- **{dimension_cn}**：{dim_info.get('description', '')}
"""
        elif dimension == 'multi_turn':
            dimension_focus = """
## 重点评估维度
本用例属于【多轮对话】维度，请按4个子任务分步校验：
- 子任务1：逐轮单轮质量校验（准确性/完整性/合规性/态度）
- 子任务2：上下文一致性校验（前后矛盾/遗忘/幻觉）
- 子任务3：指令坚守性校验（是非判断：守了/没守）
- 子任务4：规则稳定性校验（趋势判断：稳/不稳）
"""

        if dimension == 'multi_turn' and turn_results:
            conversation_text = ""
            for tr in turn_results:
                conversation_text += f"第{tr['turn']}轮 用户: {tr['user']}\n"
                conversation_text += f"第{tr['turn']}轮 AI: {tr['assistant']}\n\n"

            prompt = f"""# 角色
{evaluator_template}

---

# 测试用例
用例ID: {test_case['id']}
评测维度: {dimension}（{dimension_cn}）
场景类型: {test_case.get('scenario_type_cn', '')} ({test_case.get('scenario_type', '')})
对话轮数: {test_case.get('turn_count', 0)}轮
测试目的: {test_case['test_purpose']}
质量标准: {test_case['quality_criteria']}
{dimension_focus}
# 多轮对话记录
{conversation_text}
---

请严格按照上述角色和评测维度，对AI客服的多轮对话进行评测，按多轮对话输出格式输出结果。"""
        else:
            prompt = f"""# 角色
{evaluator_template}

---

# 测试用例
用例ID: {test_case['id']}
评测维度: {dimension}（{dimension_cn}）
测试目的: {test_case['test_purpose']}
质量标准: {test_case['quality_criteria']}
{dimension_focus}
# 用户提问
{test_case['input']}

# AI客服回答
{customer_response}

---

请严格按照上述角色和评测维度，对AI客服的回答进行评测，按指定格式输出结果。"""

        baselines[tc["name"]] = prompt

    return baselines


def save_baselines(baselines, filename):
    """保存基线到文件"""
    os.makedirs(BASELINE_DIR, exist_ok=True)
    filepath = os.path.join(BASELINE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(baselines, f, ensure_ascii=False, indent=2)
    print(f"基线已保存到: {filepath}")


def load_baselines(filename):
    """从文件加载基线"""
    filepath = os.path.join(BASELINE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_baselines(current, saved, label):
    """对比当前输出与保存的基线"""
    all_match = True
    for key in saved:
        if key not in current:
            print(f"  ❌ [{label}] 缺少: {key}")
            all_match = False
            continue
        if current[key] != saved[key]:
            print(f"  ❌ [{label}] 不一致: {key}")
            all_match = False
        else:
            print(f"  ✅ [{label}] 一致: {key}")
    for key in current:
        if key not in saved:
            print(f"  ⚠️  [{label}] 新增: {key}")
    return all_match


if __name__ == '__main__':
    if '--compare' in sys.argv:
        print("=== 对比 Prompt 输出 ===\n")

        customer_current = capture_customer_prompt_baseline()
        customer_saved = load_baselines('customer_prompts.json')
        c_ok = compare_baselines(customer_current, customer_saved, "Customer")

        print()
        evaluator_current = capture_evaluator_prompt_baseline()
        evaluator_saved = load_baselines('evaluator_prompts.json')
        e_ok = compare_baselines(evaluator_current, evaluator_saved, "Evaluator")

        if c_ok and e_ok:
            print("\n✅ 所有 Prompt 输出与基线一致")
        else:
            print("\n❌ 存在不一致的 Prompt 输出，请检查")
    else:
        print("=== 捕获 Prompt 输出基线 ===\n")

        customer_baselines = capture_customer_prompt_baseline()
        save_baselines(customer_baselines, 'customer_prompts.json')

        evaluator_baselines = capture_evaluator_prompt_baseline()
        save_baselines(evaluator_baselines, 'evaluator_prompts.json')

        print("\n基线捕获完成！")
