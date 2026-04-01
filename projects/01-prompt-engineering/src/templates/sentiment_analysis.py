"""Sentiment analysis prompt template."""

from typing import Dict, Any
from .base import BaseTemplate


class SentimentAnalysisTemplate(BaseTemplate):
    """Template for sentiment analysis tasks."""
    
    def __init__(self):
        super().__init__(
            name="Sentiment Analysis",
            description="Analyze sentiment of text"
        )
    
    def render(
        self,
        text: str,
        granularity: str = "binary",
        language: str = "Chinese",
        include_confidence: bool = True
    ) -> str:
        """
        Render a sentiment analysis prompt.
        
        Args:
            text: Text to analyze
            granularity: "binary" (positive/negative), 
                        "ternary" (positive/neutral/negative),
                        or "detailed" (with emotions)
            language: Output language
            include_confidence: Whether to include confidence score
        
        Returns:
            Formatted prompt string
        """
        granularity_instructions = {
            "binary": "将情感分为：正面 或 负面",
            "ternary": "将情感分为：正面、中性 或 负面",
            "detailed": "详细分析情感，包括主要情绪（如喜悦、愤怒、悲伤等）"
        }
        
        instruction = granularity_instructions.get(granularity, granularity_instructions["binary"])
        
        if language == "English":
            prompt = f"""Analyze the sentiment of the following text.

Text: {text}

Instructions:
1. {instruction.replace('将情感分为：', 'Classify sentiment as: ').replace('或', 'or').replace('、', ', ')}
2. {"Provide confidence score (0-1)" if include_confidence else ""}
3. Briefly explain your reasoning

Analysis:"""
        else:
            prompt = f"""请分析以下文本的情感。

文本：{text}

要求：
1. {instruction}
2. {"提供置信度评分（0-1）" if include_confidence else ""}
3. 简要说明分析理由

分析结果："""
        
        return prompt
    
    def get_example(self) -> Dict[str, Any]:
        """Get example usage of this template."""
        return {
            "text": "今天天气真好，阳光明媚，心情特别愉快！",
            "granularity": "ternary",
            "language": "Chinese",
            "include_confidence": True,
            "expected_output": """情感：正面
置信度：0.95

分析理由：
- 使用了正面词汇："真好"、"阳光明媚"、"特别愉快"
- 表达了积极的情绪和愉悦的心境
- 整体语调轻快、积极"""
        }
