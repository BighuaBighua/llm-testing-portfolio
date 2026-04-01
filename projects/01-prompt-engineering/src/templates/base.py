"""Base template class for all prompt templates."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTemplate(ABC):
    """Abstract base class for prompt templates."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def render(self, **kwargs) -> str:
        """Render the prompt template with given parameters."""
        pass
    
    @abstractmethod
    def get_example(self) -> Dict[str, Any]:
        """Get an example usage of this template."""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
