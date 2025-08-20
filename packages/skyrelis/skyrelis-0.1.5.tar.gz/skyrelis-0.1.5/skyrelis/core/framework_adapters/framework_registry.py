"""
Framework registry for managing multiple agent framework adapters.

This module provides a centralized registry for framework adapters,
allowing the system to automatically detect and handle agents from
different frameworks.
"""

import logging
from typing import Any, Dict, List, Optional, Type
from .base_adapter import BaseFrameworkAdapter


class FrameworkRegistry:
    """
    Registry for managing framework adapters.
    
    This class maintains a collection of framework adapters and provides
    methods to detect agent frameworks and delegate operations to the
    appropriate adapter.
    """
    
    def __init__(self):
        """Initialize the framework registry."""
        self._adapters: List[BaseFrameworkAdapter] = []
        self._adapter_map: Dict[str, BaseFrameworkAdapter] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_adapter(self, adapter: BaseFrameworkAdapter) -> None:
        """
        Register a framework adapter.
        
        Args:
            adapter: The framework adapter to register
        """
        if not isinstance(adapter, BaseFrameworkAdapter):
            raise TypeError("Adapter must be an instance of BaseFrameworkAdapter")
        
        framework_name = adapter.framework_name
        
        # Check if framework is available before registering
        if not adapter.is_framework_available():
            self.logger.debug(f"Framework {framework_name} is not available, skipping registration")
            return
        
        # Check for duplicate registrations
        if framework_name in self._adapter_map:
            self.logger.warning(f"Framework adapter for {framework_name} is already registered, replacing")
        
        self._adapters.append(adapter)
        self._adapter_map[framework_name] = adapter
        self.logger.info(f"Registered framework adapter: {framework_name}")
    
    def get_adapter(self, framework_name: str) -> Optional[BaseFrameworkAdapter]:
        """
        Get an adapter by framework name.
        
        Args:
            framework_name: Name of the framework
            
        Returns:
            The adapter for the framework, or None if not found
        """
        return self._adapter_map.get(framework_name)
    
    def detect_framework(self, obj: Any) -> Optional[BaseFrameworkAdapter]:
        """
        Detect which framework an object belongs to.
        
        Args:
            obj: Object to analyze
            
        Returns:
            The adapter for the detected framework, or None if no match
        """
        for adapter in self._adapters:
            try:
                if adapter.is_framework_agent(obj):
                    self.logger.debug(f"Detected {adapter.framework_name} agent: {type(obj).__name__}")
                    return adapter
            except Exception as e:
                self.logger.debug(f"Error checking {adapter.framework_name} adapter: {e}")
                continue
        
        self.logger.debug(f"No framework adapter found for object type: {type(obj).__name__}")
        return None
    
    def is_supported_agent(self, obj: Any) -> bool:
        """
        Check if an object is a supported agent from any registered framework.
        
        Args:
            obj: Object to check
            
        Returns:
            bool: True if the object is a supported agent
        """
        return self.detect_framework(obj) is not None
    
    def extract_agent_metadata(self, obj: Any) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from an agent using the appropriate adapter.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing agent metadata, or None if no adapter found
        """
        adapter = self.detect_framework(obj)
        if adapter:
            return adapter.extract_agent_metadata(obj)
        return None
    
    def create_monitored_wrapper(self, agent: Any, observer: Any, config: Any) -> Optional[Any]:
        """
        Create a monitored wrapper for an agent using the appropriate adapter.
        
        Args:
            agent: The agent object
            observer: The AgentObserver instance
            config: Configuration object
            
        Returns:
            A monitored wrapper, or None if no adapter found
        """
        adapter = self.detect_framework(agent)
        if adapter:
            return adapter.create_monitored_wrapper(agent, observer, config)
        return None
    
    def get_registered_frameworks(self) -> List[str]:
        """
        Get the list of registered framework names.
        
        Returns:
            List of framework names
        """
        return list(self._adapter_map.keys())
    
    def get_framework_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered frameworks.
        
        Returns:
            List of framework information dictionaries
        """
        return [
            {
                "name": adapter.framework_name,
                "version_requirement": adapter.framework_version_requirement,
                "available": adapter.is_framework_available(),
                "adapter_class": type(adapter).__name__
            }
            for adapter in self._adapters
        ]
    
    def clear_adapters(self) -> None:
        """Clear all registered adapters."""
        self._adapters.clear()
        self._adapter_map.clear()
        self.logger.info("Cleared all framework adapters") 