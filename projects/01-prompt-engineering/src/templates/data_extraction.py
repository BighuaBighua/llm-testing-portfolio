"""Data extraction prompt template."""

from typing import Dict, Any, List
from .base import BaseTemplate


class DataExtractionTemplate(BaseTemplate):
    """Template for structured data extraction tasks."""
    
    def __init__(self):
        super().__init__(
            name="Data Extraction",
            description="Extract structured data from unstructured text"
        )
    
    def render(
        self,
        text: str,
        fields: List[str],
        output_format: str = "json",
        language: str = "Chinese"
    ) -> str:
        """
        Render a data extraction prompt.
        
        Args:
            text: Source text to extract data from
            fields: List of fields to extract
            output_format: "json", "table", or "list"
            language: Output language
        
        Returns:
            Formatted prompt string
        """
        format_instructions = {
            "json": "JSON格式",
            "table": "表格形式",
            "list": "列表形式"
        }
        
        instruction = format_instructions.get(output_format, format_instructions["json"])
        fields_str = "、".join(fields) if language == "Chinese" else ", ".join(fields)
        
        if language == "English":
            prompt = f"""Extract the following information from the given text.

Fields to extract: {fields_str}
Output format: {instruction}

Text:
{text}

Extracted data:"""
        else:
            prompt = f"""请从以下文本中提取信息。

需要提取的字段：{fields_str}
输出格式：{instruction}

文本：
{text}

提取的数据："""
        
        return prompt
    
    def get_example(self) -> Dict[str, Any]:
        """Get example usage of this template."""
        return {
            "text": "张三，男，35岁，毕业于北京大学计算机系，现任阿里巴巴高级工程师，年薪50万。",
            "fields": ["姓名", "性别", "年龄", "毕业院校", "职位", "薪资"],
            "output_format": "json",
            "language": "Chinese",
            "expected_output": '''{
  "姓名": "张三",
  "性别": "男",
  "年龄": "35岁",
  "毕业院校": "北京大学计算机系",
  "职位": "阿里巴巴高级工程师",
  "薪资": "50万"
}'''
        }
