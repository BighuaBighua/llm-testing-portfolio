"""Question answering prompt template."""

from typing import Dict, Any
from .base import BaseTemplate


class QATemplate(BaseTemplate):
    """Template for question answering tasks."""
    
    def __init__(self):
        super().__init__(
            name="Question Answering",
            description="Answer questions based on given context"
        )
    
    def render(
        self,
        question: str,
        context: str = "",
        answer_style: str = "detailed",
        language: str = "Chinese"
    ) -> str:
        """
        Render a question answering prompt.
        
        Args:
            question: The question to answer
            context: Context information (optional)
            answer_style: "detailed", "concise", or "step_by_step"
            language: Output language
        
        Returns:
            Formatted prompt string
        """
        style_instructions = {
            "detailed": "提供详细、完整的答案" if language == "Chinese" else "Provide a detailed and complete answer",
            "concise": "提供简洁、直接的答案" if language == "Chinese" else "Provide a concise and direct answer",
            "step_by_step": "逐步分析并回答问题" if language == "Chinese" else "Analyze and answer step by step"
        }
        
        instruction = style_instructions.get(answer_style, style_instructions["detailed"])
        
        if context:
            if language == "English":
                prompt = f"""Answer the following question based on the given context.

Context:
{context}

Question: {question}

Instruction: {instruction}

Answer:"""
            else:
                prompt = f"""请根据给定的上下文回答问题。

上下文：
{context}

问题：{question}

要求：{instruction}

答案："""
        else:
            if language == "English":
                prompt = f"""Answer the following question.

Question: {question}

Instruction: {instruction}

Answer:"""
            else:
                prompt = f"""请回答以下问题。

问题：{question}

要求：{instruction}

答案："""
        
        return prompt
    
    def get_example(self) -> Dict[str, Any]:
        """Get example usage of this template."""
        return {
            "question": "什么是机器学习？",
            "context": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并改进性能，而无需明确编程。",
            "answer_style": "detailed",
            "language": "Chinese",
            "expected_output": "机器学习是人工智能的一个重要分支领域。它让计算机系统能够自动从数据中学习和改进，而不需要人为编写具体的规则代码。通过算法和统计模型，机器学习可以识别数据中的模式，做出预测或决策，并随着经验积累不断优化其性能。"
        }
