"""
被测模型输入Prompt动态组装器

职责：
1. 加载被测模型输入模板（单轮/多轮）
2. 根据场景动态切换角色和业务范围
3. 组装测试用例输入
4. 多轮对话的 system message 也从模板加载（非硬编码）
"""

import logging
from typing import Dict, List, Optional, Union

from tools.prompt_template import PromptTemplateLoader

logger = logging.getLogger(__name__)


class UnderTestPromptAssembler:
    """被测模型输入Prompt动态组装器

    根据测试用例的维度（单轮/多轮）和业务场景配置，
    动态组装发送给被测模型的Prompt。
    单轮用例输出纯文本Prompt，多轮用例输出OpenAI格式的messages列表。
    """

    def __init__(self, loader: PromptTemplateLoader = None, registry: 'ConfigRegistry' = None):
        """初始化组装器

        Args:
            loader: Prompt模板加载器（可选，默认自动创建）
            registry: 配置注册中心（可选，用于获取业务场景信息）
        """
        self._loader = loader or PromptTemplateLoader()
        self._registry = registry

    def assemble(
        self,
        test_case: Dict,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Union[str, List[Dict]]:
        """组装被测模型的输入Prompt

        根据测试用例维度自动选择组装方式：
        - multi_turn + 有对话历史：组装为OpenAI messages格式（system + 历史轮次）
        - 其他维度：组装为单轮纯文本Prompt

        Args:
            test_case: 测试用例字典
            conversation_history: 多轮对话历史（仅multi_turn维度使用）

        Returns:
            单轮返回str，多轮返回List[Dict]（OpenAI messages格式）
        """
        if self._registry:
            business_scenario = self._registry.business_scenario_name
            business_scope = self._registry.business_scenario_description
        else:
            business_scenario = "通用客服"
            business_scope = "回答用户关于服务、流程、操作等方面的问题"

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
        """组装单轮对话Prompt，从模板加载并渲染，失败时使用fallback"""
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
        """组装多轮对话Prompt，生成system message + 对话历史的messages列表"""
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
        """单轮Prompt的fallback模板（模板文件缺失时使用）"""
        return f"""# 任务
你是一个专业、友好的{variables.get('business_scenario', '通用客服')}。你的职责是：{variables.get('business_scope', '回答用户关于服务、流程、操作等方面的问题')}。

请回答以下用户问题。

# 用户提问
{variables.get('user_input', '')}

---
请直接给出你的回答，不需要输出其他内容。"""

    def _fallback_multi_turn_system(self, variables: Dict[str, str]) -> str:
        """多轮对话system message的fallback模板（模板文件缺失时使用）"""
        return f"你是一个专业、友好的{variables.get('business_scenario', '通用客服')}。你的职责是：{variables.get('business_scope', '回答用户关于服务、流程、操作等方面的问题')}。"
