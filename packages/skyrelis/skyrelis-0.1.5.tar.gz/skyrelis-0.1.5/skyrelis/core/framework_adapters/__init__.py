"""
Framework adapters for multi-framework agent observability support.

This module provides a plugin architecture for supporting different
AI agent frameworks like LangChain, CrewAI, etc.
"""

from .base_adapter import BaseFrameworkAdapter
from .framework_registry import FrameworkRegistry
from .langchain_adapter import LangChainAdapter

# Initialize the framework registry
registry = FrameworkRegistry()

# Register built-in adapters
registry.register_adapter(LangChainAdapter())

# Try to register CrewAI adapter if available
try:
    from .crewai_adapter import CrewAIAdapter
    registry.register_adapter(CrewAIAdapter())
except ImportError:
    # CrewAI not available, skip registration
    pass

__all__ = [
    'BaseFrameworkAdapter',
    'FrameworkRegistry',
    'LangChainAdapter',
    'registry'
] 