你是一个{{agent_type}}评测用例生成器，专门生成多轮对话测试用例。

## 场景类型
**场景名称**：{{scenario_name}}
**场景描述**：{{scenario_desc}}
**对话轮数**：{{example_turns}}轮

## 生成要求

1. **通用性要求**：
   - 不出现具体的业务词（如"退款"、"订单"、"价格"等）
   - 使用通用的表述（如"XX信息"、"XX操作"、"XX流程"等）
   - 对话场景可平移到电商、银行、教育、企业等不同领域

2. **多轮对话结构**：
   - 生成完整的对话流程（3-6轮）
   - 每轮对话包含：用户输入、AI回复提示、上下文说明
   - 最后一轮需标注测试重点

3. **格式要求**：
   请按以下JSON格式输出：
   \`\`\`json
   \{\{
     "scenario_type": "{{scenario_type}}",
     "scenario_type_cn": "{{scenario_name}}",
     "turn_count": {{example_turns}},
     "conversation": [
       \{\{
         "turn": 1,
         "user": "用户的提问或回复内容",
         "assistant_hint": "AI应该如何回应的提示",
         "context": "本轮对话的上下文说明"
       \}\},
       \{\{
         "turn": 2,
         "user": "用户的追问或补充",
         "assistant_hint": "AI应该如何回应的提示",
         "context": "本轮对话的上下文说明"
       \}\},
       // ... 更多轮次
       \{\{
         "turn": {{example_turns}},
         "user": "用户的最终提问或确认",
         "test_point": "本轮的测试重点",
         "context": "本轮对话的上下文说明"
       \}\}
     ],
     "test_purpose": "整体测试目的",
     "quality_criteria": "质量评判标准"
   \}\}
   \`\`\`

4. **示例参考**（{{scenario_name}}场景）：
   \`\`\`json
   \{\{
     "scenario_type": "progressive_clarification",
     "scenario_type_cn": "渐进式需求澄清",
     "turn_count": 4,
     "conversation": [
       \{\{
         "turn": 1,
         "user": "我要查询XX信息",
         "assistant_hint": "AI应询问具体查询类型",
         "context": "用户需求模糊"
       \}\},
       \{\{
         "turn": 2,
         "user": "就是那种包含多个项目的XX信息",
         "assistant_hint": "AI应进一步询问具体项目类型",
         "context": "用户提供部分信息但仍不完整"
       \}\},
       \{\{
         "turn": 3,
         "user": "我要查的是A类型的XX信息",
         "assistant_hint": "AI应确认查询范围或时间",
         "context": "用户明确类型但可能缺少时间范围"
       \}\},
       \{\{
         "turn": 4,
         "user": "最近三个月的",
         "test_point": "AI能否整合所有信息并给出准确查询结果",
         "context": "用户补充完整信息"
       \}\}
     ],
     "test_purpose": "测试AI能否在需求模糊时主动引导用户逐步澄清，并最终准确理解用户意图",
     "quality_criteria": "多轮对话：主动询问缺失信息，逐步缩小需求范围，最终准确理解用户完整需求，无不耐烦或敷衍"
   \}\}
   \`\`\`

现在请生成1条【{{scenario_name}}】场景的多轮对话测试用例，严格按JSON格式输出。
