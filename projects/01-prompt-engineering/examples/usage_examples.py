"""
Example usage of prompt templates and evaluators.
演示如何使用 Prompt 模板和评估器。

This file demonstrates:
1. How to use different prompt templates
2. How to evaluate prompt responses
3. Best practices for prompt engineering
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.templates import (
    SummarizationTemplate,
    QATemplate,
    CodeGenerationTemplate,
    DataExtractionTemplate,
    SentimentAnalysisTemplate
)
from src.evaluators import QualityEvaluator, RelevanceEvaluator


def example_summarization():
    """Example: Text summarization template."""
    print("=" * 60)
    print("示例 1: 文本摘要")
    print("=" * 60)
    
    template = SummarizationTemplate()
    
    # Example text
    text = """
    人工智能（AI）正在改变各行各业。从医疗诊断到自动驾驶，从金融风控到智能家居，
    AI技术的应用越来越广泛。然而，随着AI的发展，也带来了一些挑战，如数据隐私、
    算法偏见、就业影响等问题需要我们认真对待。同时，AI的发展也需要大量的计算资源
    和专业人才，这对企业和政府都提出了新的要求。
    """
    
    # Generate prompt
    prompt = template.render(
        text=text,
        style="bullet_points",
        max_length=100,
        language="Chinese"
    )
    
    print("\n生成的 Prompt:")
    print(prompt)
    print("\n" + "=" * 60)


def example_qa():
    """Example: Question answering template."""
    print("\n示例 2: 问答系统")
    print("=" * 60)
    
    template = QATemplate()
    
    context = "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并改进性能，而无需明确编程。"
    question = "什么是机器学习？"
    
    prompt = template.render(
        question=question,
        context=context,
        answer_style="detailed",
        language="Chinese"
    )
    
    print("\n生成的 Prompt:")
    print(prompt)
    print("\n" + "=" * 60)


def example_code_generation():
    """Example: Code generation template."""
    print("\n示例 3: 代码生成")
    print("=" * 60)
    
    template = CodeGenerationTemplate()
    
    prompt = template.render(
        requirement="Create a function that checks if a string is a palindrome",
        language="Python",
        style="clean",
        include_comments=True,
        include_tests=True
    )
    
    print("\n生成的 Prompt:")
    print(prompt)
    print("\n" + "=" * 60)


def example_data_extraction():
    """Example: Data extraction template."""
    print("\n示例 4: 数据提取")
    print("=" * 60)
    
    template = DataExtractionTemplate()
    
    text = "张三，男，35岁，毕业于北京大学计算机系，现任阿里巴巴高级工程师，年薪50万。"
    fields = ["姓名", "性别", "年龄", "毕业院校", "职位", "薪资"]
    
    prompt = template.render(
        text=text,
        fields=fields,
        output_format="json",
        language="Chinese"
    )
    
    print("\n生成的 Prompt:")
    print(prompt)
    print("\n" + "=" * 60)


def example_sentiment_analysis():
    """Example: Sentiment analysis template."""
    print("\n示例 5: 情感分析")
    print("=" * 60)
    
    template = SentimentAnalysisTemplate()
    
    text = "今天天气真好，阳光明媚，心情特别愉快！"
    
    prompt = template.render(
        text=text,
        granularity="ternary",
        language="Chinese",
        include_confidence=True
    )
    
    print("\n生成的 Prompt:")
    print(prompt)
    print("\n" + "=" * 60)


def example_evaluation():
    """Example: Evaluate a response using the evaluators."""
    print("\n示例 6: 响应评估")
    print("=" * 60)
    
    # Example prompt and response
    prompt = "请解释什么是机器学习？"
    response = """
    机器学习是人工智能的一个重要分支。它让计算机系统能够自动从数据中学习和改进，
    而不需要人为编写具体的规则代码。通过算法和统计模型，机器学习可以识别数据
    中的模式，做出预测或决策，并随着经验积累不断优化其性能。
    """
    
    # Evaluate quality
    quality_eval = QualityEvaluator()
    quality_result = quality_eval.evaluate(
        prompt=prompt,
        response=response,
        expected_keywords=["人工智能", "数据", "学习", "算法"]
    )
    
    print("\n质量评估结果:")
    print(f"总体得分: {quality_result['overall_score']}")
    print(f"各项指标: {quality_result['metrics']}")
    print(f"分析: {quality_result['analysis']}")
    
    # Evaluate relevance
    relevance_eval = RelevanceEvaluator()
    relevance_result = relevance_eval.evaluate(
        prompt=prompt,
        response=response,
        key_topics=["机器学习", "人工智能", "数据"]
    )
    
    print("\n相关性评估结果:")
    print(f"相关性得分: {relevance_result['relevance_score']}")
    print(f"相关性等级: {relevance_result['level']}")
    print(f"覆盖的主题: {relevance_result['covered_topics']}")
    print(f"分析: {relevance_result['analysis']}")
    
    print("\n" + "=" * 60)


def main():
    """Run all examples."""
    print("\n🚀 Prompt Engineering 模板和评估器使用示例")
    print("=" * 60)
    
    # Run template examples
    example_summarization()
    example_qa()
    example_code_generation()
    example_data_extraction()
    example_sentiment_analysis()
    
    # Run evaluation example
    example_evaluation()
    
    print("\n✅ 所有示例运行完成！")
    print("\n💡 提示：这些是生成的 Prompt，实际使用时需要调用 LLM API 获取响应。")
    print("   然后可以使用评估器对响应进行评估。\n")


if __name__ == "__main__":
    main()
