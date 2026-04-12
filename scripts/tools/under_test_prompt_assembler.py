"""
被测模型输入Prompt动态组装器

职责：
1. 加载被测模型输入模板（单轮/多轮）
2. 根据场景动态切换角色和业务范围
3. 组装测试用例输入
4. 多轮对话的 system message 也从模板加载（非硬编码）
"""

import os
import logging
from typing import Dict, List, Optional, Union

from tools.prompt_template import PromptTemplateLoader
from tools.config import get_business_rules

logger = logging.getLogger(__name__)


class UnderTestPromptAssembler:
    """被测模型输入Prompt动态组装器

    模板架构：
    1. 单轮模板：templates/under-test/single-turn.md
    2. 多轮 system 模板：templates/under-test/multi-turn-system.md
    3. 场景配置：configs/business/scenarios.yaml
    """

    def __init__(self, loader: PromptTemplateLoader = None):
        self._loader = loader or PromptTemplateLoader()

    def assemble(
        self,
        test_case: Dict,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Union[str, List[Dict]]:
        """组装被测模型输入Prompt

        Args:
            test_case: 测试用例
            conversation_history: 多轮对话历史

        Returns:
            单轮：返回 prompt 字符串
            多轮：返回 messages 列表
        """
        business_rules = get_business_rules()
        scenarios_config = business_rules.get('scenarios', {})
        active_scenario_name = scenarios_config.get('active_scenario', 'default')
        active_scenario = scenarios_config.get('scenarios', {}).get(active_scenario_name, {})

        business_scenario = active_scenario.get('name', '通用客服')
        business_scope = active_scenario.get('description', '回答用户关于服务、流程、操作等方面的问题')

        variables = {
            'business_scenario': business_scenario,
            'business_scope': business_scope,
            'user_input': test_case.get('input', ''),
        }

        dimension = test_case.get('dimension', 'accuracy')

        if dimension == 'multi_turn' and conversation_history:
            return self._assemble_multi_turn(variables, conversation_history)

        return self._assemble_single_turn(variables)

    def _assemble_single_turn(self, variables: Dict[str, str]) -> str:
        """组装单轮对话Prompt"""
        try:
            return self._loader.render('under-test/single-turn.md', variables).rstrip('\n')
        except FileNotFoundError:
            logger.warning("单轮模板未找到，使用 fallback")
            return self._fallback_single_turn(variables)

    def _assemble_multi_turn(
        self,
        variables: Dict[str, str],
        conversation_history: List[Dict],
    ) -> List[Dict]:
        """组装多轮对话Prompt（返回messages格式）

        关键：system message 从模板加载，而非硬编码
        """
        try:
            system_content = self._loader.render(
                'under-test/multi-turn-system.md', variables
            ).strip()
        except FileNotFoundError:
            logger.warning("多轮 system 模板未找到，使用 fallback")
            system_content = self._fallback_multi_turn_system(variables)

        messages = [{"role": "system", "content": system_content}]
        messages.extend(conversation_history)
        return messages

    def _fallback_single_turn(self, variables: Dict[str, str]) -> str:
        """单轮对话 fallback（模板文件不存在时）"""
        return f"""# 任务
你是一个专业、友好的{variables.get('business_scenario', '通用客服')}。你的职责是：{variables.get('business_scope', '回答用户关于服务、流程、操作等方面的问题')}。

请回答以下用户问题。

# 用户提问
{variables.get('user_input', '')}

---
请直接给出你的回答，不需要输出其他内容。"""

    def _fallback_multi_turn_system(self, variables: Dict[str, str]) -> str:
        """多轮对话 system message fallback"""
        return f"你是一个专业、友好的{variables.get('business_scenario', '通用客服')}。你的职责是：{variables.get('business_scope', '回答用户关于服务、流程、操作等方面的问题')}。"
