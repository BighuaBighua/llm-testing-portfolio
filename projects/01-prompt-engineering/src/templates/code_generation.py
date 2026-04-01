"""Code generation prompt template."""

from typing import Dict, Any
from .base import BaseTemplate


class CodeGenerationTemplate(BaseTemplate):
    """Template for code generation tasks."""
    
    def __init__(self):
        super().__init__(
            name="Code Generation",
            description="Generate code based on requirements"
        )
    
    def render(
        self,
        requirement: str,
        language: str = "Python",
        style: str = "clean",
        include_comments: bool = True,
        include_tests: bool = False
    ) -> str:
        """
        Render a code generation prompt.
        
        Args:
            requirement: Description of what code should do
            language: Programming language
            style: "clean", "documented", or "optimized"
            include_comments: Whether to include comments
            include_tests: Whether to generate tests
        
        Returns:
            Formatted prompt string
        """
        style_instructions = {
            "clean": "Write clean, readable code following best practices",
            "documented": "Write well-documented code with docstrings",
            "optimized": "Write optimized code with performance considerations"
        }
        
        instruction = style_instructions.get(style, style_instructions["clean"])
        
        prompt = f"""Generate {language} code for the following requirement.

Requirement: {requirement}

Style: {instruction}
Include comments: {"Yes" if include_comments else "No"}
Include tests: {"Yes" if include_tests else "No"}

Please provide:
1. The code implementation
2. Brief explanation of the approach
3. {"Unit tests" if include_tests else "Example usage"}

Code:"""
        
        return prompt
    
    def get_example(self) -> Dict[str, Any]:
        """Get example usage of this template."""
        return {
            "requirement": "Create a function that calculates the factorial of a number",
            "language": "Python",
            "style": "clean",
            "include_comments": True,
            "include_tests": True,
            "expected_output": '''def factorial(n):
    """
    Calculate the factorial of a non-negative integer.
    
    Args:
        n: Non-negative integer
    
    Returns:
        Factorial of n
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

# Unit tests
import pytest

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    with pytest.raises(ValueError):
        factorial(-1)'''
        }
