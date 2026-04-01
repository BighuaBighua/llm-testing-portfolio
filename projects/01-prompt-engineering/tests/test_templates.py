"""Tests for prompt templates."""

import pytest
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


class TestSummarizationTemplate:
    """Tests for SummarizationTemplate."""
    
    def test_render_with_chinese(self):
        """Test rendering with Chinese language."""
        template = SummarizationTemplate()
        prompt = template.render(
            text="这是一段测试文本。",
            style="bullet_points",
            language="Chinese"
        )
        
        assert "请对以下文本进行总结" in prompt
        assert "这是一段测试文本" in prompt
    
    def test_render_with_english(self):
        """Test rendering with English language."""
        template = SummarizationTemplate()
        prompt = template.render(
            text="This is a test text.",
            style="paragraph",
            language="English"
        )
        
        assert "Please summarize" in prompt
        assert "This is a test text" in prompt
    
    def test_get_example(self):
        """Test example method."""
        template = SummarizationTemplate()
        example = template.get_example()
        
        assert "text" in example
        assert "style" in example
        assert "expected_output" in example


class TestQATemplate:
    """Tests for QATemplate."""
    
    def test_render_with_context(self):
        """Test rendering with context."""
        template = QATemplate()
        prompt = template.render(
            question="什么是AI?",
            context="AI是人工智能的缩写。",
            language="Chinese"
        )
        
        assert "什么是AI" in prompt
        assert "AI是人工智能的缩写" in prompt
        assert "上下文" in prompt
    
    def test_render_without_context(self):
        """Test rendering without context."""
        template = QATemplate()
        prompt = template.render(
            question="What is AI?",
            language="English"
        )
        
        assert "What is AI" in prompt
        assert "Context" not in prompt


class TestDataExtractionTemplate:
    """Tests for DataExtractionTemplate."""
    
    def test_render_json_format(self):
        """Test rendering with JSON format."""
        template = DataExtractionTemplate()
        prompt = template.render(
            text="张三，男，25岁",
            fields=["姓名", "性别", "年龄"],
            output_format="json",
            language="Chinese"
        )
        
        assert "提取信息" in prompt
        assert "JSON格式" in prompt
        assert "张三" in prompt


class TestSentimentAnalysisTemplate:
    """Tests for SentimentAnalysisTemplate."""
    
    def test_render_binary(self):
        """Test rendering with binary granularity."""
        template = SentimentAnalysisTemplate()
        prompt = template.render(
            text="今天很开心",
            granularity="binary",
            language="Chinese"
        )
        
        assert "分析以下文本的情感" in prompt
        assert "正面 或 负面" in prompt
    
    def test_render_ternary(self):
        """Test rendering with ternary granularity."""
        template = SentimentAnalysisTemplate()
        prompt = template.render(
            text="I feel neutral",
            granularity="ternary",
            language="English"
        )
        
        assert "positive, neutral, or negative" in prompt.lower()


class TestQualityEvaluator:
    """Tests for QualityEvaluator."""
    
    def test_evaluate_good_response(self):
        """Test evaluating a good quality response."""
        evaluator = QualityEvaluator()
        result = evaluator.evaluate(
            prompt="解释什么是机器学习",
            response="机器学习是人工智能的一个分支，通过算法从数据中学习模式，不断改进性能。",
            expected_keywords=["机器学习", "人工智能", "数据"]
        )
        
        assert result['overall_score'] > 0.5
        assert 'metrics' in result
        assert 'analysis' in result
    
    def test_evaluate_empty_response(self):
        """Test evaluating an empty response."""
        evaluator = QualityEvaluator()
        result = evaluator.evaluate(
            prompt="测试问题",
            response=""
        )
        
        assert result['overall_score'] < 0.5


class TestRelevanceEvaluator:
    """Tests for RelevanceEvaluator."""
    
    def test_evaluate_relevant_response(self):
        """Test evaluating a relevant response."""
        evaluator = RelevanceEvaluator()
        result = evaluator.evaluate(
            prompt="什么是Python?",
            response="Python是一种编程语言，广泛用于数据科学和Web开发。",
            key_topics=["Python", "编程语言"]
        )
        
        assert result['relevance_score'] > 0.3
        assert 'level' in result
        assert 'covered_topics' in result
    
    def test_evaluate_irrelevant_response(self):
        """Test evaluating an irrelevant response."""
        evaluator = RelevanceEvaluator()
        result = evaluator.evaluate(
            prompt="什么是Python?",
            response="今天天气真好，阳光明媚。",
            key_topics=["Python", "编程"]
        )
        
        assert result['relevance_score'] < 0.5
        assert result['level'] == "不相关" or result['level'] == "低度相关"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
