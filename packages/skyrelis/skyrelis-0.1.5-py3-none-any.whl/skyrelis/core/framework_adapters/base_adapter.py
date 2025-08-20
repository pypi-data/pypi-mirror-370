"""
Base adapter interface for agent framework support.

This module defines the abstract base class that all framework adapters
must implement to provide observability support for their respective
AI agent frameworks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime


class BaseFrameworkAdapter(ABC):
    """
    Abstract base class for framework adapters.
    
    Each framework adapter provides framework-specific logic for:
    - Detecting if an object belongs to the framework
    - Extracting metadata from agent objects
    - Creating framework-specific monitored wrappers
    - Handling framework-specific execution patterns
    """
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Return the name of the framework this adapter supports."""
        pass
    
    @property
    @abstractmethod
    def framework_version_requirement(self) -> Optional[str]:
        """Return the minimum version requirement for the framework."""
        pass
    
    @abstractmethod
    def is_framework_agent(self, obj: Any) -> bool:
        """
        Check if an object is an agent from this framework.
        
        Args:
            obj: Object to check
            
        Returns:
            bool: True if the object is an agent from this framework
        """
        pass
    
    @abstractmethod
    def extract_agent_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract metadata from a framework agent object.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing standardized agent metadata
        """
        pass
    
    @abstractmethod
    def get_agent_methods(self, obj: Any) -> List[str]:
        """
        Get the list of execution methods available on this agent.
        
        Args:
            obj: The agent object
            
        Returns:
            List of method names that can be used to execute the agent
        """
        pass
    
    @abstractmethod
    def create_monitored_wrapper(self, agent: Any, observer: Any, config: Any) -> Any:
        """
        Create a framework-specific monitored wrapper for the agent.
        
        Args:
            agent: The original agent object
            observer: The AgentObserver instance
            config: Configuration object
            
        Returns:
            A monitored wrapper that maintains the agent's interface
        """
        pass
    
    def is_framework_available(self) -> bool:
        """
        Check if the framework is available for import.
        
        Returns:
            bool: True if the framework can be imported
        """
        try:
            self._import_framework_modules()
            return True
        except ImportError:
            return False
    
    @abstractmethod
    def _import_framework_modules(self) -> None:
        """
        Import framework-specific modules.
        
        This method should attempt to import the framework's main modules
        and raise ImportError if the framework is not available.
        """
        pass
    
    def extract_system_prompts(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract system prompts from a framework agent.
        
        Default implementation returns empty list. Subclasses should override
        to provide framework-specific prompt extraction.
        
        Args:
            obj: The agent object
            
        Returns:
            List of system prompts with their sources
        """
        return []
    
    def extract_tools_info(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract tools/functions information from a framework agent.
        
        Default implementation returns empty list. Subclasses should override
        to provide framework-specific tool extraction.
        
        Args:
            obj: The agent object
            
        Returns:
            List of tools with their metadata
        """
        return []
    
    def extract_llm_info(self, obj: Any) -> Dict[str, Any]:
        """
        Extract LLM configuration from a framework agent.
        
        Default implementation returns empty dict. Subclasses should override
        to provide framework-specific LLM info extraction.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing LLM configuration
        """
        return {}
    
    def get_agent_type_info(self, obj: Any) -> Dict[str, str]:
        """
        Get basic type information about the agent.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict with type information
        """
        return {
            "framework": self.framework_name,
            "agent_type": type(obj).__name__,
            "agent_class": f"{type(obj).__module__}.{type(obj).__qualname__}",
            "extraction_time": datetime.utcnow().isoformat()
        } 