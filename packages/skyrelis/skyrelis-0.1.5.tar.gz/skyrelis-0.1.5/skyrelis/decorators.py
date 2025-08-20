"""
Easy-to-use decorators for adding observability to AI agents from multiple frameworks.

This module provides simple decorators that allow users to quickly add
observability capabilities to their AI agents without complex setup.
Supports LangChain, CrewAI, and other frameworks through a plugin system.
"""

import functools
import os
import inspect
from typing import Optional, Callable, Any, Dict, Union, List
from datetime import datetime
import uuid


# Import the framework registry
from .core.framework_adapters import registry


def observe_agent(
    remote_observer_url: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_remote_observer: bool = True,
    capture_metadata: bool = True,
    **config_kwargs
):
    """
    Decorator to add observability to any supported AI agent framework.
    
    This decorator automatically detects the framework (LangChain, CrewAI, etc.)
    and applies the appropriate observability capabilities.
    
    Args:
        remote_observer_url: URL of the standalone observer (defaults to env var REMOTE_OBSERVER_URL)
        agent_name: Name for the agent (defaults to function name)
        enable_remote_observer: Whether to send traces to remote observer
        capture_metadata: Whether to capture agent metadata (LLM params, tools, etc.)
        **config_kwargs: Additional configuration options
    
    Example:
        @observe_agent(remote_observer_url="http://localhost:8000", agent_name="my_agent")
        def my_agent_function():
            # Your agent code here
            return agent  # Returns any supported agent framework
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Lazy imports to avoid requiring specific frameworks at import time
            from .core.agent_observer import AgentObserver
            from .config.observer_config import ObserverConfig
            
            # Get configuration
            config = ObserverConfig(
                remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
                enable_remote_observer=enable_remote_observer,
                **config_kwargs
            )
            
            # Create observer
            observer = AgentObserver(config)
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Check if result is a supported agent using the framework registry
            if registry.is_supported_agent(result):
                # Extract agent metadata if requested
                if capture_metadata:
                    agent_metadata = registry.extract_agent_metadata(result)
                    if agent_metadata:
                        observer.add_custom_metadata("agent_metadata", agent_metadata)
                
                # Create monitored wrapper using the appropriate framework adapter
                monitored_agent = registry.create_monitored_wrapper(result, observer, config)
                
                # Return the monitored agent if wrapper was created, otherwise return original
                return monitored_agent if monitored_agent else result
            else:
                # If not a supported agent, just return the result
                # but still create a trace for the function execution
                trace_id = str(uuid.uuid4())
                observer.start_trace(trace_id, {"args": args, "kwargs": kwargs})
                
                # Check if result contains spans
                spans = None
                if isinstance(result, dict) and "spans" in result:
                    spans = result["spans"]
                    # Use the result field as output_data if it exists
                    output_data = result.get("result", result)
                else:
                    output_data = result
                
                # Add spans to the trace if present
                if spans and trace_id in observer.active_traces:
                    observer.active_traces[trace_id]["spans"] = spans
                
                observer.end_trace(trace_id, output_data)
                return result
            
        return wrapper
    return decorator


def observe_langchain_agent(
    remote_observer_url: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_remote_observer: bool = True,
    capture_metadata: bool = True,
    **config_kwargs
):
    """
    Decorator specifically for LangChain agent classes.
    
    This decorator automatically captures system prompts, LLM parameters,
    tools, and all agent attributes when the class is instantiated.
    
    Args:
        remote_observer_url: URL of the standalone observer (defaults to env var REMOTE_OBSERVER_URL)
        agent_name: Name for the agent (defaults to class name)
        enable_remote_observer: Whether to send traces to remote observer
        capture_metadata: Whether to capture agent metadata (LLM params, tools, etc.)
        **config_kwargs: Additional configuration options
    
    Example:
        @observe_langchain_agent(remote_observer_url="http://localhost:8000")
        class MyAgent(AgentExecutor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
    """
    def decorator(cls):
        # Import datetime for trace timing
        from datetime import datetime
        from typing import Dict, Any
        
        original_init = cls.__init__
        original_invoke = getattr(cls, 'invoke', None)
        
        # Get agent name
        agent_name_final = agent_name or cls.__name__
        
        def __init__(self, *args, **kwargs):
            # Lazy imports to avoid requiring LangChain at import time
            from .core.agent_observer import AgentObserver
            from .core.monitored_agent import ObservabilityCallbackHandler
            from .config.observer_config import ObserverConfig
            import requests
            import uuid
            
            # Call original init first
            original_init(self, *args, **kwargs)
            
            # Generate unique agent ID and set on instance
            self._agent_id = str(uuid.uuid4())
            self._agent_name = agent_name_final
            
            # Get configuration
            config = ObserverConfig(
                remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
                enable_remote_observer=enable_remote_observer,
                **config_kwargs
            )
            
            # Set up observability
            self._observer = AgentObserver(config)
            
            # Extract agent metadata if requested (including system prompts)
            if capture_metadata:
                # Use the framework registry to extract metadata
                agent_metadata = registry.extract_agent_metadata(self)
                if agent_metadata:
                    self._agent_metadata = agent_metadata
                    print(f"🤖 Agent initialized with metadata: {agent_metadata}")
                    
                    # Add metadata to observer for inclusion in all traces
                    self._observer.add_custom_metadata("agent_metadata", agent_metadata)
                    if "system_prompts" in agent_metadata:
                        self._observer.add_custom_metadata("system_prompts", agent_metadata["system_prompts"])
                    
                    # Register agent with the monitor
                    self._register_agent_with_monitor(config.remote_observer_url, agent_metadata)
        
        def _register_agent_with_monitor(self, monitor_url: str, agent_metadata: Dict[str, Any]):
            """Register this agent instance with the monitor."""
            import requests
            import json
            
            def _make_json_serializable(obj):
                """Convert objects to JSON-serializable format."""
                if hasattr(obj, '__dict__'):
                    return str(obj)
                return obj
            
            try:
                # Ensure all data is JSON serializable
                registration_data = {
                    "agent_id": self._agent_id,
                    "agent_name": self._agent_name,
                    "agent_type": agent_metadata.get("agent_type", "unknown"),
                    "framework": agent_metadata.get("framework", "unknown"),
                    "system_prompts": agent_metadata.get("system_prompts", []),
                    "tools": agent_metadata.get("tools", []),
                    "llm_info": agent_metadata.get("llm_info", {}),
                    "metadata": {
                        "extraction_time": agent_metadata.get("extraction_time"),
                        "attributes": {},  # Skip complex attributes to avoid serialization issues
                        "agent_info": agent_metadata.get("agent_info", {})
                    }
                }
                
                # Test JSON serialization before sending
                json.dumps(registration_data)
                
                response = requests.post(
                    f"{monitor_url}/api/agents/register",
                    json=registration_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        print(f"✅ Agent registered with monitor: {self._agent_id}")
                    else:
                        print(f"⚠️  Agent registration failed: {result.get('message', 'unknown error')}")
                else:
                    print(f"⚠️  Agent registration HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Failed to register agent with monitor: {e}")
                # Don't raise - agent should still work without registration
        
        def invoke(self, input_data: Dict[str, Any], config=None, **kwargs):
            """Wrap the invoke method to add observability."""
            # Lazy imports
            from .core.monitored_agent import ObservabilityCallbackHandler
            import uuid
            
            # Generate trace ID
            trace_id = str(uuid.uuid4())
            
            # Start trace with correct API (including agent_id)
            metadata = {"agent_name": self._agent_name, "agent_id": self._agent_id}
            self._observer.start_trace(
                trace_id=trace_id,
                input_data=input_data,
                metadata=metadata
            )
            
            try:
                # Create observability callback
                observability_callback = ObservabilityCallbackHandler(self._observer, trace_id)
                
                # Prepare config with callbacks
                if config is None:
                    config = {}
                
                # Get existing callbacks and add ours
                callbacks = config.get("callbacks", [])
                if not isinstance(callbacks, list):
                    callbacks = [callbacks] if callbacks else []
                
                callbacks.append(observability_callback)
                config["callbacks"] = callbacks
                
                # Call original invoke with our callback
                result = original_invoke(self, input_data, config=config, **kwargs)
                
                # End trace with success (using correct API)
                self._observer.end_trace(
                    trace_id=trace_id,
                    output_data=result,
                    error=None
                )
                
                return result
                
            except Exception as e:
                # End trace with error (using correct API)
                self._observer.end_trace(
                    trace_id=trace_id,
                    output_data=None,
                    error=e
                )
                
                raise e

        # Replace methods
        cls.__init__ = __init__
        cls._register_agent_with_monitor = _register_agent_with_monitor
        if original_invoke:
            cls.invoke = invoke
        
        return cls
    return decorator


def observe_crewai_agent(
    remote_observer_url: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_remote_observer: bool = True,
    capture_metadata: bool = True,
    **config_kwargs
):
    """
    Decorator specifically for CrewAI agents, tasks, and crews.
    
    This decorator automatically integrates with CrewAI's OpenTelemetry instrumentation
    and captures comprehensive metadata about agents, tasks, and workflows.
    
    Args:
        remote_observer_url: URL of the standalone observer (defaults to env var REMOTE_OBSERVER_URL)
        agent_name: Name for the component (defaults to class name)
        enable_remote_observer: Whether to send traces to remote observer
        capture_metadata: Whether to capture component metadata
        **config_kwargs: Additional configuration options
    
    Example:
        @observe_crewai_agent(remote_observer_url="http://localhost:8000")
        class MyCrewAIAgent(Agent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
    """
    def decorator(cls_or_func):
        if inspect.isclass(cls_or_func):
            return _observe_crewai_class(cls_or_func, remote_observer_url, agent_name, 
                                       enable_remote_observer, capture_metadata, **config_kwargs)
        else:
            return _observe_crewai_function(cls_or_func, remote_observer_url, agent_name,
                                          enable_remote_observer, capture_metadata, **config_kwargs)
    
    return decorator


def _observe_crewai_class(cls, remote_observer_url, agent_name, enable_remote_observer, capture_metadata, **config_kwargs):
    """Handle CrewAI class decoration."""
    original_init = cls.__init__
    agent_name_final = agent_name or cls.__name__
    
    def __init__(self, *args, **kwargs):
        from .core.agent_observer import AgentObserver
        from .config.observer_config import ObserverConfig
        from .core.framework_adapters.opentelemetry_integration import enable_crewai_instrumentation
        import uuid
        
        # Call original init first
        original_init(self, *args, **kwargs)
        
        # Generate unique ID and set on instance
        self._agent_id = str(uuid.uuid4())
        self._agent_name = agent_name_final
        
        # Get configuration
        config = ObserverConfig(
            remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
            enable_remote_observer=enable_remote_observer,
            **config_kwargs
        )
        
        # Set up observability
        self._observer = AgentObserver(config)
        
        # Enable CrewAI instrumentation
        enable_crewai_instrumentation(self._observer, config)
        
        # Extract metadata if requested
        if capture_metadata:
            agent_metadata = registry.extract_agent_metadata(self)
            if agent_metadata:
                self._agent_metadata = agent_metadata
                print(f"🤖 CrewAI component initialized with metadata: {agent_metadata}")
                
                # Add metadata to observer
                self._observer.add_custom_metadata("agent_metadata", agent_metadata)
                if "system_prompts" in agent_metadata:
                    self._observer.add_custom_metadata("system_prompts", agent_metadata["system_prompts"])
    
    cls.__init__ = __init__
    return cls


def _observe_crewai_function(func, remote_observer_url, agent_name, enable_remote_observer, capture_metadata, **config_kwargs):
    """Handle CrewAI function decoration."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from .core.agent_observer import AgentObserver
        from .config.observer_config import ObserverConfig
        from .core.framework_adapters.opentelemetry_integration import enable_crewai_instrumentation
        
        # Get configuration
        config = ObserverConfig(
            remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
            enable_remote_observer=enable_remote_observer,
            **config_kwargs
        )
        
        # Create observer
        observer = AgentObserver(config)
        
        # Enable CrewAI instrumentation
        enable_crewai_instrumentation(observer, config)
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Extract metadata if the result is a CrewAI component
        if capture_metadata and registry.is_supported_agent(result):
            agent_metadata = registry.extract_agent_metadata(result)
            if agent_metadata:
                observer.add_custom_metadata("agent_metadata", agent_metadata)
        
        return result
    
    return wrapper


def quick_observe(func: Callable) -> Callable:
    """
    Simple decorator that adds basic observability with default settings.
    
    Uses environment variables for configuration:
    - REMOTE_OBSERVER_URL: URL of the standalone observer
    - AGENT_NAME: Name for the agent
    
    Example:
        @quick_observe
        def my_agent_function():
            # Your agent code here
            return agent  # Returns any supported agent framework
    """
    return observe_agent()(func)


def quick_observe_class(cls):
    """
    Simple decorator for agent classes with default settings.
    
    Example:
        @quick_observe_class
        class MyAgent:
            def run(self, input_text):
                # Your agent code here
                pass
    """
    return observe_agent()(cls)


# Convenience functions for manual usage
def create_observer(
    remote_observer_url: Optional[str] = None,
    agent_name: str = "unnamed_agent",
    enable_remote_observer: bool = True,
    **config_kwargs
):
    """
    Create an observer instance for manual usage.
    
    Args:
        remote_observer_url: URL of the standalone observer
        agent_name: Name for the agent
        enable_remote_observer: Whether to send traces to remote observer
        **config_kwargs: Additional configuration options
    
    Returns:
        AgentObserver instance
    """
    # Lazy imports to avoid requiring specific frameworks at import time
    from .core.agent_observer import AgentObserver
    from .config.observer_config import ObserverConfig
    
    config = ObserverConfig(
        remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
        enable_remote_observer=enable_remote_observer,
        **config_kwargs
    )
    return AgentObserver(config)


def send_trace(
    trace_data: Dict[str, Any],
    observer_url: Optional[str] = None,
    agent_name: str = "unnamed_agent"
):
    """
    Manually send a trace to the observer.
    
    Args:
        trace_data: Dictionary containing trace information
        observer_url: URL of the standalone observer
        agent_name: Name for the agent
    """
    # Lazy imports to avoid requiring specific frameworks at import time
    from .utils.remote_observer_client import RemoteObserverClient
    from .config.observer_config import ObserverConfig
    
    url = observer_url or os.getenv("OBSERVER_URL", "http://localhost:8000")
    config = ObserverConfig(remote_observer_url=url)
    client = RemoteObserverClient(config)
    
    # Add agent_name to trace_data
    if agent_name:
        trace_data["agent_name"] = agent_name
    
    return client.send_trace_sync(trace_data)


def capture_agent_metadata(agent) -> Dict[str, Any]:
    """
    Capture metadata from any supported agent framework.
    
    Args:
        agent: The agent object from any supported framework
        
    Returns:
        Dict containing agent metadata including LLM parameters, tools, etc.
    """
    return registry.extract_agent_metadata(agent)


def get_supported_frameworks() -> List[str]:
    """
    Get a list of currently supported agent frameworks.
    
    Returns:
        List of framework names that are currently supported
    """
    return registry.get_registered_frameworks()


def get_framework_info() -> List[Dict[str, Any]]:
    """
    Get detailed information about supported frameworks.
    
    Returns:
        List of framework information dictionaries
    """
    return registry.get_framework_info()


# Legacy function aliases for backward compatibility
def _is_langchain_agent(obj) -> bool:
    """Legacy function - use registry.detect_framework() instead."""
    adapter = registry.detect_framework(obj)
    return adapter is not None and adapter.framework_name == "langchain"


def _extract_agent_metadata(obj) -> Dict[str, Any]:
    """Legacy function - use registry.extract_agent_metadata() instead."""
    return registry.extract_agent_metadata(obj) or {} 