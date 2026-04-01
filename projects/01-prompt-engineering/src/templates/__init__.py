"""Prompt templates for LLM applications."""

from .summarization import SummarizationTemplate
from .question_answering import QATemplate
from .code_generation import CodeGenerationTemplate
from .data_extraction import DataExtractionTemplate
from .sentiment_analysis import SentimentAnalysisTemplate

__all__ = [
    "SummarizationTemplate",
    "QATemplate",
    "CodeGenerationTemplate",
    "DataExtractionTemplate",
    "SentimentAnalysisTemplate",
]
