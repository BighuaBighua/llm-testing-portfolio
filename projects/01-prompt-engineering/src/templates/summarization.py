"""Text summarization prompt template."""

from typing import Dict, Any
from .base import BaseTemplate


class SummarizationTemplate(BaseTemplate):
    """Template for text summarization tasks."""
    
    def __init__(self):
        super().__init__(
            name="Text Summarization",
            description="Summarize long text into concise, key points"
        )
    
    def render(
        self,
        text: str,
        style: str = "bullet_points",
        max_length: int = 200,
        language: str = "Chinese"
    ) -> str:
        """
        Render a summarization prompt.
        
        Args:
            text: The text to summarize
            style: Summary style - "bullet_points", "paragraph", "key_facts"
            max_length: Maximum length of summary in words
            language: Output language - "Chinese" or "English"
        
        Returns:
            Formatted prompt string
        """
        style_instructions = {
            "bullet_points": "使用项目符号列出关键要点",
            "paragraph": "写成一段连贯的文字",
            "key_facts": "提取最重要的3-5个事实"
        }
        
        instruction = style_instructions.get(style, style_instructions["bullet_points"])
        
        if language == "English":
            prompt = f"""Please summarize the following text.

Style: {style}
Maximum length: {max_length} words
Format: {instruction}

Text to summarize:
{text}

Summary:"""
        else:
            prompt = f"""请对以下文本进行总结。

格式要求：{instruction}
字数限制：{max_length}字以内

文本内容：
{text}

总结："""
        
        return prompt
    
    def get_example(self) -> Dict[str, Any]:
        """Get example usage of this template."""
        return {
            "text": "人工智能（AI）正在改变各行各业。从医疗诊断到自动驾驶，从金融风控到智能家居，AI技术的应用越来越广泛。然而，随着AI的发展，也带来了一些挑战，如数据隐私、算法偏见、就业影响等问题需要我们认真对待。",
            "style": "bullet_points",
            "max_length": 100,
            "language": "Chinese",
            "expected_output": "• AI正在改变多个行业\n• 应用领域包括医疗、交通、金融等\n• 发展中面临隐私、偏见等挑战"
        }
