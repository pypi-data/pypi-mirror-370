"""
LangChain framework adapter for agent observability.

This module provides LangChain-specific implementation of the framework
adapter interface, including agent detection, metadata extraction, and
monitored wrapper creation.
"""

import inspect
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .base_adapter import BaseFrameworkAdapter


class LangChainAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for LangChain agents.
    
    Provides LangChain-specific implementations for:
    - Agent detection and validation
    - Metadata and system prompt extraction
    - Monitored wrapper creation
    - Tool and LLM information extraction
    """
    
    def __init__(self):
        """Initialize the LangChain adapter."""
        self.logger = logging.getLogger(__name__)
    
    @property
    def framework_name(self) -> str:
        """Return the framework name."""
        return "langchain"
    
    @property
    def framework_version_requirement(self) -> Optional[str]:
        """Return the minimum LangChain version requirement."""
        return ">=0.1.0"
    
    def _import_framework_modules(self) -> None:
        """Import LangChain modules to verify availability."""
        import langchain  # Will raise ImportError if not available
        from langchain.agents import AgentExecutor
        from langchain.schema import BaseMessage
        from langchain.callbacks.base import BaseCallbackHandler
    
    def is_framework_agent(self, obj) -> bool:
        """
        Check if an object is a LangChain agent or has LangChain agent-like attributes.
        
        Args:
            obj: Object to check
            
        Returns:
            bool: True if it appears to be a LangChain agent
        """
        # Check for common LangChain agent attributes
        langchain_indicators = [
            'run', 'invoke', 'arun', 'ainvoke',  # Common LangChain methods
            'llm', 'tools', 'agent', 'chain',    # Common LangChain attributes
            'callbacks', 'memory', 'verbose'      # LangChain configuration
        ]
        
        # Check if object has LangChain-like methods
        has_langchain_methods = any(hasattr(obj, method) for method in ['run', 'invoke'])
        
        # Check if object has LangChain-like attributes
        has_langchain_attrs = any(hasattr(obj, attr) for attr in langchain_indicators)
        
        # Check if it's a class that might be a LangChain agent
        if inspect.isclass(obj):
            # Check if it has LangChain-like methods in its methods
            methods = [name for name, _ in inspect.getmembers(obj, inspect.isfunction)]
            has_langchain_methods = any(method in methods for method in ['run', 'invoke'])
        
        return has_langchain_methods or has_langchain_attrs
    
    def get_agent_methods(self, obj: Any) -> List[str]:
        """
        Get the list of execution methods available on this LangChain agent.
        
        Args:
            obj: The agent object
            
        Returns:
            List of method names that can be used to execute the agent
        """
        methods = []
        for method_name in ['run', 'invoke', 'arun', 'ainvoke']:
            if hasattr(obj, method_name):
                methods.append(method_name)
        return methods
    
    def extract_agent_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract metadata from a LangChain agent object.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing agent metadata including system prompts
        """
        metadata = self.get_agent_type_info(obj)
        metadata.update({
            "attributes": {},
            "system_prompts": self.extract_system_prompts(obj),
            "tools": self.extract_tools_info(obj),
            "llm_info": self.extract_llm_info(obj),
            "agent_info": self._extract_agent_specific_info(obj)
        })
        
        # Extract common LangChain agent attributes
        common_attrs = [
            'llm', 'tools', 'agent', 'chain', 'memory', 'callbacks',
            'verbose', 'max_iterations', 'early_stopping_method'
        ]
        
        for attr in common_attrs:
            if hasattr(obj, attr):
                try:
                    value = getattr(obj, attr)
                    if value is not None:
                        # Convert to string representation for serialization
                        if hasattr(value, '__dict__'):
                            metadata["attributes"][attr] = str(value)
                        else:
                            metadata["attributes"][attr] = value
                except Exception:
                    # Skip attributes that can't be accessed
                    pass
        
        return metadata
    
    def extract_system_prompts(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract system prompts from various LangChain agent structures.
        
        Args:
            obj: The agent object
            
        Returns:
            List of system prompts with their sources
        """
        system_prompts = []
        
        # Method 1: Extract from agent.runnable (modern LangChain agents)
        if hasattr(obj, 'agent') and obj.agent is not None:
            runnable = getattr(obj.agent, 'runnable', None)
            if runnable is not None:
                prompts = self._extract_prompts_from_runnable(runnable)
                system_prompts.extend(prompts)
        
        # Method 2: Extract from direct prompt attribute
        if hasattr(obj, 'prompt'):
            prompt = getattr(obj, 'prompt')
            if prompt is not None:
                prompts = self._extract_prompts_from_template(prompt)
                system_prompts.extend(prompts)
        
        # Method 3: Extract from agent's prompt if available
        if hasattr(obj, 'agent') and obj.agent is not None and hasattr(obj.agent, 'prompt'):
            prompt = getattr(obj.agent, 'prompt')
            if prompt is not None:
                prompts = self._extract_prompts_from_template(prompt)
                system_prompts.extend(prompts)
        
        # Method 4: Extract from chain structures
        if hasattr(obj, 'chain') and obj.chain is not None:
            prompts = self._extract_prompts_from_runnable(obj.chain)
            system_prompts.extend(prompts)
        
        return system_prompts
    
    def extract_tools_info(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract tools information from a LangChain agent.
        
        Args:
            obj: The agent object
            
        Returns:
            List of tools with their metadata
        """
        tools_info = []
        
        if hasattr(obj, 'tools') and obj.tools is not None:
            for tool in obj.tools:
                tool_info = {
                    "name": getattr(tool, 'name', str(tool)),
                    "type": type(tool).__name__,
                    "description": getattr(tool, 'description', None)
                }
                tools_info.append(tool_info)
        
        return tools_info
    
    def extract_llm_info(self, obj: Any) -> Dict[str, Any]:
        """
        Extract LLM configuration from a LangChain agent.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing LLM configuration
        """
        llm_info = {}
        
        if hasattr(obj, 'llm') and obj.llm is not None:
            llm = obj.llm
            llm_info = {
                "type": type(llm).__name__,
                "model_name": getattr(llm, 'model_name', None),
                "temperature": getattr(llm, 'temperature', None),
                "max_tokens": getattr(llm, 'max_tokens', None),
            }
        
        return llm_info
    
    def create_monitored_wrapper(self, agent: Any, observer: Any, config: Any) -> Any:
        """
        Create a LangChain-specific monitored wrapper for the agent.
        
        Args:
            agent: The original LangChain agent object
            observer: The AgentObserver instance
            config: Configuration object
            
        Returns:
            A monitored wrapper that maintains the agent's interface
        """
        from ..monitored_agent import MonitoredAgent
        return MonitoredAgent(agent, observer, config)
    
    def _extract_agent_specific_info(self, obj: Any) -> Dict[str, Any]:
        """
        Extract agent-specific information from a LangChain agent.
        
        Args:
            obj: The agent object
            
        Returns:
            Dict containing agent-specific information
        """
        agent_info = {}
        
        if hasattr(obj, 'agent') and obj.agent is not None:
            agent = obj.agent
            agent_info = {
                "type": type(agent).__name__,
                "system_message": getattr(agent, 'system_message', None),
                "human_message": getattr(agent, 'human_message', None),
            }
        
        return agent_info
    
    def _extract_prompts_from_runnable(self, runnable) -> List[Dict[str, Any]]:
        """Extract prompts from a LangChain runnable object."""
        prompts = []
        
        try:
            # Check if runnable has steps (RunnableSequence)
            if hasattr(runnable, 'steps'):
                for step in runnable.steps:
                    prompts.extend(self._extract_prompts_from_runnable(step))
            
            # Check if it's a ChatPromptTemplate
            if hasattr(runnable, 'messages'):
                prompts.extend(self._extract_prompts_from_template(runnable))
            
            # Check if runnable has a mapper (RunnableAssign)
            if hasattr(runnable, 'mapper'):
                for key, value in runnable.mapper.items():
                    prompts.extend(self._extract_prompts_from_runnable(value))
            
            # Check if it's a bound runnable
            if hasattr(runnable, 'bound'):
                prompts.extend(self._extract_prompts_from_runnable(runnable.bound))
                
        except Exception as e:
            # Silently continue if extraction fails
            pass
        
        return prompts
    
    def _extract_prompts_from_template(self, template) -> List[Dict[str, Any]]:
        """Extract system prompts from a prompt template."""
        prompts = []
        
        try:
            # Handle ChatPromptTemplate
            if hasattr(template, 'messages'):
                for message in template.messages:
                    if hasattr(message, 'prompt') and hasattr(message.prompt, 'template'):
                        # Check if it's a SystemMessagePromptTemplate
                        if 'System' in type(message).__name__:
                            prompts.append({
                                "type": "system_prompt",
                                "source": "ChatPromptTemplate.SystemMessage",
                                "template": message.prompt.template,
                                "input_variables": getattr(message.prompt, 'input_variables', []),
                                "partial_variables": getattr(message.prompt, 'partial_variables', {})
                            })
            
            # Handle direct PromptTemplate
            elif hasattr(template, 'template'):
                # Check if it looks like a system prompt (heuristic)
                template_text = template.template.lower()
                if any(keyword in template_text for keyword in ['you are', 'system:', 'assistant', 'helpful']):
                    prompts.append({
                        "type": "system_prompt",
                        "source": "PromptTemplate",
                        "template": template.template,
                        "input_variables": getattr(template, 'input_variables', []),
                        "partial_variables": getattr(template, 'partial_variables', {})
                    })
            
            # Handle string templates
            elif isinstance(template, str):
                template_text = template.lower()
                if any(keyword in template_text for keyword in ['you are', 'system:', 'assistant', 'helpful']):
                    prompts.append({
                        "type": "system_prompt",
                        "source": "string_template",
                        "template": template,
                        "input_variables": [],
                        "partial_variables": {}
                    })
                    
        except Exception as e:
            # Silently continue if extraction fails
            pass
        
        return prompts 