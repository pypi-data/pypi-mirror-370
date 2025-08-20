"""
CrewAI framework adapter for agent observability.

This module provides CrewAI-specific implementation of the framework
adapter interface, including agent detection, metadata extraction, and
monitored wrapper creation. It integrates with the existing OpenTelemetry
CrewAI instrumentation.
"""

import inspect
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .base_adapter import BaseFrameworkAdapter


class CrewAIAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for CrewAI agents and workflows.
    
    Provides CrewAI-specific implementations for:
    - Agent and crew detection and validation
    - Metadata extraction from agents, tasks, and crews
    - Monitored wrapper creation using existing OpenTelemetry instrumentation
    - Integration with CrewAI's workflow execution patterns
    """
    
    def __init__(self):
        """Initialize the CrewAI adapter."""
        self.logger = logging.getLogger(__name__)
    
    @property
    def framework_name(self) -> str:
        """Return the framework name."""
        return "crewai"
    
    @property
    def framework_version_requirement(self) -> Optional[str]:
        """Return the minimum CrewAI version requirement."""
        return ">=0.70.0"
    
    def _import_framework_modules(self) -> None:
        """Import CrewAI modules to verify availability."""
        import crewai  # Will raise ImportError if not available
        from crewai import Agent, Task, Crew
        from crewai.llm import LLM
    
    def is_framework_agent(self, obj) -> bool:
        """
        Check if an object is a CrewAI agent, task, or crew.
        
        Args:
            obj: Object to check
            
        Returns:
            bool: True if it appears to be a CrewAI component
        """
        try:
            # Check for CrewAI specific classes first
            if hasattr(obj, '__class__'):
                class_name = obj.__class__.__name__
                module_name = getattr(obj.__class__, '__module__', '')
                
                # Check if it's a CrewAI class by module
                if 'crewai' in module_name:
                    return True
                
                # Check for specific CrewAI class names
                crewai_classes = ['Agent', 'Task', 'Crew', 'LLM']
                if class_name in crewai_classes:
                    return True
            
            # Check for CrewAI-specific attributes
            crewai_indicators = [
                # Agent attributes
                'role', 'goal', 'backstory', 'tools', 'llm', 'verbose', 'allow_delegation',
                'max_iter', 'cache', 'system_template', 'prompt_template', 'response_template',
                # Task attributes
                'description', 'expected_output', 'agent', 'async_execution', 'context',
                'output_file', 'callback', 'human_input',
                # Crew attributes
                'agents', 'tasks', 'process', 'verbose', 'manager_llm', 'function_calling_llm',
                'config', 'max_rpm', 'language', 'memory', 'embedder', 'full_output',
                'step_callback', 'share_crew', 'manager_agent', 'manager_callbacks',
                'prompt_file', 'planning', 'planning_llm'
            ]
            
            # Check if object has CrewAI-like attributes
            has_crewai_attrs = any(hasattr(obj, attr) for attr in crewai_indicators)
            
            # Check for CrewAI-specific methods
            crewai_methods = [
                'kickoff',  # Crew method
                'execute_task',  # Agent method
                'execute_sync',  # Task method
                'execute_async'  # Task method
            ]
            has_crewai_methods = any(hasattr(obj, method) for method in crewai_methods)
            
            # Check if it's a class that might be a CrewAI component
            if inspect.isclass(obj):
                methods = [name for name, _ in inspect.getmembers(obj, inspect.isfunction)]
                has_crewai_methods = any(method in methods for method in crewai_methods)
            
            return has_crewai_attrs or has_crewai_methods
            
        except Exception as e:
            self.logger.debug(f"Error checking CrewAI agent: {e}")
            return False
    
    def get_agent_methods(self, obj: Any) -> List[str]:
        """
        Get the list of execution methods available on this CrewAI component.
        
        Args:
            obj: The CrewAI object
            
        Returns:
            List of method names that can be used to execute the component
        """
        methods = []
        
        # Check based on component type
        if hasattr(obj, '__class__'):
            class_name = obj.__class__.__name__
            
            if class_name == 'Crew':
                if hasattr(obj, 'kickoff'):
                    methods.append('kickoff')
            elif class_name == 'Agent':
                for method_name in ['execute_task']:
                    if hasattr(obj, method_name):
                        methods.append(method_name)
            elif class_name == 'Task':
                for method_name in ['execute_sync', 'execute_async']:
                    if hasattr(obj, method_name):
                        methods.append(method_name)
        
        return methods
    
    def extract_agent_metadata(self, obj: Any) -> Dict[str, Any]:
        """
        Extract metadata from a CrewAI component (Agent, Task, or Crew).
        
        Args:
            obj: The CrewAI object
            
        Returns:
            Dict containing component metadata
        """
        metadata = self.get_agent_type_info(obj)
        
        # Determine component type and extract specific metadata
        if hasattr(obj, '__class__'):
            class_name = obj.__class__.__name__
            
            if class_name == 'Agent':
                metadata.update(self._extract_agent_metadata(obj))
            elif class_name == 'Task':
                metadata.update(self._extract_task_metadata(obj))
            elif class_name == 'Crew':
                metadata.update(self._extract_crew_metadata(obj))
            elif class_name == 'LLM':
                metadata.update(self._extract_llm_metadata(obj))
        
        return metadata
    
    def extract_system_prompts(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract system prompts from CrewAI components.
        
        Args:
            obj: The CrewAI object
            
        Returns:
            List of system prompts with their sources
        """
        system_prompts = []
        
        try:
            if hasattr(obj, '__class__'):
                class_name = obj.__class__.__name__
                
                if class_name == 'Agent':
                    # Extract agent's system prompts
                    if hasattr(obj, 'system_template') and obj.system_template:
                        system_prompts.append({
                            "type": "system_template",
                            "source": "CrewAI.Agent.system_template",
                            "template": obj.system_template,
                            "input_variables": [],
                            "partial_variables": {}
                        })
                    
                    if hasattr(obj, 'prompt_template') and obj.prompt_template:
                        system_prompts.append({
                            "type": "prompt_template",
                            "source": "CrewAI.Agent.prompt_template",
                            "template": obj.prompt_template,
                            "input_variables": [],
                            "partial_variables": {}
                        })
                    
                    # Extract role and backstory as implicit prompts
                    if hasattr(obj, 'role') and obj.role:
                        system_prompts.append({
                            "type": "role_prompt",
                            "source": "CrewAI.Agent.role",
                            "template": f"You are a {obj.role}",
                            "input_variables": [],
                            "partial_variables": {}
                        })
                    
                    if hasattr(obj, 'backstory') and obj.backstory:
                        system_prompts.append({
                            "type": "backstory_prompt",
                            "source": "CrewAI.Agent.backstory",
                            "template": obj.backstory,
                            "input_variables": [],
                            "partial_variables": {}
                        })
                
                elif class_name == 'Crew':
                    # Extract prompts from all agents in the crew
                    if hasattr(obj, 'agents') and obj.agents:
                        for i, agent in enumerate(obj.agents):
                            agent_prompts = self.extract_system_prompts(agent)
                            for prompt in agent_prompts:
                                prompt['source'] = f"CrewAI.Crew.agents[{i}].{prompt['source'].split('.')[-1]}"
                                system_prompts.append(prompt)
        
        except Exception as e:
            self.logger.debug(f"Error extracting system prompts: {e}")
        
        return system_prompts
    
    def extract_tools_info(self, obj: Any) -> List[Dict[str, Any]]:
        """
        Extract tools information from a CrewAI component.
        
        Args:
            obj: The CrewAI object
            
        Returns:
            List of tools with their metadata
        """
        tools_info = []
        
        try:
            if hasattr(obj, 'tools') and obj.tools:
                for tool in obj.tools:
                    tool_info = {
                        "name": getattr(tool, 'name', getattr(tool, '__name__', str(tool))),
                        "type": type(tool).__name__,
                        "description": getattr(tool, 'description', None),
                        "framework": "crewai"
                    }
                    tools_info.append(tool_info)
            
            # For crews, also extract tools from agents
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'Crew':
                if hasattr(obj, 'agents') and obj.agents:
                    for i, agent in enumerate(obj.agents):
                        agent_tools = self.extract_tools_info(agent)
                        for tool in agent_tools:
                            tool['source_agent'] = f"agent_{i}_{getattr(agent, 'role', 'unknown')}"
                            tools_info.append(tool)
        
        except Exception as e:
            self.logger.debug(f"Error extracting tools info: {e}")
        
        return tools_info
    
    def extract_llm_info(self, obj: Any) -> Dict[str, Any]:
        """
        Extract LLM configuration from a CrewAI component.
        
        Args:
            obj: The CrewAI object
            
        Returns:
            Dict containing LLM configuration
        """
        llm_info = {}
        
        try:
            if hasattr(obj, 'llm') and obj.llm:
                llm = obj.llm
                llm_info = {
                    "type": type(llm).__name__,
                    "model": getattr(llm, 'model', getattr(llm, 'model_name', None)),
                    "temperature": getattr(llm, 'temperature', None),
                    "max_tokens": getattr(llm, 'max_tokens', getattr(llm, 'max_completion_tokens', None)),
                    "top_p": getattr(llm, 'top_p', None),
                    "presence_penalty": getattr(llm, 'presence_penalty', None),
                    "frequency_penalty": getattr(llm, 'frequency_penalty', None),
                    "framework": "crewai"
                }
        
        except Exception as e:
            self.logger.debug(f"Error extracting LLM info: {e}")
        
        return llm_info
    
    def create_monitored_wrapper(self, agent: Any, observer: Any, config: Any) -> Any:
        """
        Create a CrewAI-specific monitored wrapper.
        
        For CrewAI, we use the existing OpenTelemetry instrumentation rather than
        creating a custom wrapper, as CrewAI's architecture is better suited to
        method-level instrumentation.
        
        Args:
            agent: The original CrewAI object
            observer: The AgentObserver instance
            config: Configuration object
            
        Returns:
            The original agent with instrumentation enabled
        """
        try:
            # Try to import and enable CrewAI instrumentation
            from ..opentelemetry_integration import enable_crewai_instrumentation
            enable_crewai_instrumentation(observer, config)
            
            # Return the original agent - instrumentation happens at the method level
            return agent
            
        except ImportError:
            self.logger.warning("CrewAI OpenTelemetry instrumentation not available")
            # Fallback to a basic monitored wrapper
            return CrewAIMonitoredWrapper(agent, observer, config)
    
    def _extract_agent_metadata(self, agent: Any) -> Dict[str, Any]:
        """Extract metadata specific to CrewAI agents."""
        metadata = {
            "agent_specific": {},
            "system_prompts": self.extract_system_prompts(agent),
            "tools": self.extract_tools_info(agent),
            "llm_info": self.extract_llm_info(agent)
        }
        
        # Extract standard agent attributes
        agent_attrs = [
            'role', 'goal', 'backstory', 'verbose', 'allow_delegation',
            'max_iter', 'cache', 'system_template', 'prompt_template',
            'response_template', 'config'
        ]
        
        for attr in agent_attrs:
            if hasattr(agent, attr):
                value = getattr(agent, attr)
                if value is not None:
                    metadata["agent_specific"][attr] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        
        return metadata
    
    def _extract_task_metadata(self, task: Any) -> Dict[str, Any]:
        """Extract metadata specific to CrewAI tasks."""
        metadata = {
            "task_specific": {},
            "tools": self.extract_tools_info(task)
        }
        
        # Extract standard task attributes
        task_attrs = [
            'description', 'expected_output', 'async_execution', 'context',
            'output_file', 'human_input', 'config'
        ]
        
        for attr in task_attrs:
            if hasattr(task, attr):
                value = getattr(task, attr)
                if value is not None:
                    metadata["task_specific"][attr] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        
        # Add agent info if task has an assigned agent
        if hasattr(task, 'agent') and task.agent:
            metadata["task_specific"]["agent_role"] = getattr(task.agent, 'role', 'unknown')
            metadata["task_specific"]["agent_id"] = str(getattr(task.agent, 'id', 'unknown'))
        
        return metadata
    
    def _extract_crew_metadata(self, crew: Any) -> Dict[str, Any]:
        """Extract metadata specific to CrewAI crews."""
        metadata = {
            "crew_specific": {},
            "agents": [],
            "tasks": [],
            "system_prompts": self.extract_system_prompts(crew),
            "tools": self.extract_tools_info(crew)
        }
        
        # Extract standard crew attributes
        crew_attrs = [
            'process', 'verbose', 'config', 'max_rpm', 'language',
            'memory', 'full_output', 'share_crew', 'planning'
        ]
        
        for attr in crew_attrs:
            if hasattr(crew, attr):
                value = getattr(crew, attr)
                if value is not None:
                    metadata["crew_specific"][attr] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        
        # Extract agents information
        if hasattr(crew, 'agents') and crew.agents:
            for i, agent in enumerate(crew.agents):
                agent_info = {
                    "index": i,
                    "role": getattr(agent, 'role', 'unknown'),
                    "goal": getattr(agent, 'goal', ''),
                    "id": str(getattr(agent, 'id', f'agent_{i}'))
                }
                metadata["agents"].append(agent_info)
        
        # Extract tasks information
        if hasattr(crew, 'tasks') and crew.tasks:
            for i, task in enumerate(crew.tasks):
                task_info = {
                    "index": i,
                    "description": getattr(task, 'description', 'unknown'),
                    "expected_output": getattr(task, 'expected_output', ''),
                    "agent_role": getattr(task.agent, 'role', 'unknown') if hasattr(task, 'agent') and task.agent else None
                }
                metadata["tasks"].append(task_info)
        
        return metadata
    
    def _extract_llm_metadata(self, llm: Any) -> Dict[str, Any]:
        """Extract metadata specific to CrewAI LLM objects."""
        metadata = {
            "llm_specific": {},
            "llm_info": self.extract_llm_info(llm)
        }
        
        # Extract LLM attributes
        llm_attrs = [
            'model', 'temperature', 'max_tokens', 'max_completion_tokens',
            'top_p', 'n', 'stop', 'presence_penalty', 'frequency_penalty', 'seed'
        ]
        
        for attr in llm_attrs:
            if hasattr(llm, attr):
                value = getattr(llm, attr)
                if value is not None:
                    metadata["llm_specific"][attr] = value
        
        return metadata


class CrewAIMonitoredWrapper:
    """
    Basic monitored wrapper for CrewAI components when OpenTelemetry instrumentation is not available.
    
    This is a fallback wrapper that provides basic observability capabilities.
    """
    
    def __init__(self, component: Any, observer: Any, config: Any):
        """
        Initialize the CrewAI monitored wrapper.
        
        Args:
            component: The CrewAI component to wrap
            observer: The AgentObserver instance
            config: Configuration for observability
        """
        self.component = component
        self.observer = observer
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"CrewAI monitored wrapper initialized for {type(component).__name__}")
    
    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped component.
        
        Args:
            name: Attribute name
            
        Returns:
            Any: The attribute value
        """
        attr = getattr(self.component, name)
        
        # If it's a method that should be monitored, wrap it
        if callable(attr) and name in ['kickoff', 'execute_task', 'execute_sync', 'execute_async']:
            return self._wrap_method(attr, name)
        
        return attr
    
    def _wrap_method(self, method, method_name):
        """Wrap a method with basic observability."""
        def wrapped(*args, **kwargs):
            import uuid
            trace_id = str(uuid.uuid4())
            
            try:
                # Start trace
                self.observer.start_trace(trace_id, {
                    "method": method_name,
                    "component_type": type(self.component).__name__,
                    "args": str(args)[:1000],  # Limit size
                    "kwargs": str(kwargs)[:1000]  # Limit size
                })
                
                # Execute method
                result = method(*args, **kwargs)
                
                # End trace successfully
                self.observer.end_trace(trace_id, {
                    "result": str(result)[:1000] if result else None  # Limit size
                })
                
                return result
                
            except Exception as e:
                # End trace with error
                self.observer.end_trace(trace_id, None, e)
                raise
        
        return wrapped 