"""
MonitoredAgent class that wraps LangChain agents with observability capabilities.
"""

import uuid
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage, AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler

from ..config.observer_config import ObserverConfig
from .agent_observer import AgentObserver


class ObservabilityCallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler for LangChain that integrates with the observability system.
    """
    
    def __init__(self, observer: AgentObserver, trace_id: str):
        """
        Initialize the callback handler.
        
        Args:
            observer: The AgentObserver instance
            trace_id: The current trace ID
        """
        self.observer = observer
        self.trace_id = trace_id
        self.logger = logging.getLogger(__name__)
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts."""
        step_data = {
            "llm_name": serialized.get("name", "unknown") if serialized else "unknown",
            "prompts": prompts,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "llm_start", step_data)
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM ends."""
        step_data = {
            "response": str(response),
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "llm_end", step_data)
    
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when LLM errors."""
        step_data = {
            "error": str(error),
            "error_type": type(error).__name__,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "llm_error", step_data)
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        """Called when chain starts."""
        step_data = {
            "chain_name": serialized.get("name", "unknown") if serialized else "unknown",
            "inputs": inputs,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "chain_start", step_data)
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs):
        """Called when chain ends."""
        step_data = {
            "outputs": outputs,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "chain_end", step_data)
    
    def on_chain_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when chain errors."""
        step_data = {
            "error": str(error),
            "error_type": type(error).__name__,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "chain_error", step_data)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Called when tool starts."""
        step_data = {
            "tool_name": serialized.get("name", "unknown") if serialized else "unknown",
            "input_str": input_str,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "tool_start", step_data)
    
    def on_tool_end(self, output: str, **kwargs):
        """Called when tool ends."""
        step_data = {
            "output": output,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "tool_end", step_data)
    
    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when tool errors."""
        step_data = {
            "error": str(error),
            "error_type": type(error).__name__,
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "tool_error", step_data)
    
    def on_agent_action(self, action: AgentAction, **kwargs):
        """Called when agent takes an action."""
        step_data = {
            "action": action.dict(),
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "agent_action", step_data)
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Called when agent finishes."""
        step_data = {
            "finish": finish.dict(),
            "kwargs": kwargs
        }
        self.observer.add_trace_step(self.trace_id, "agent_finish", step_data)


class MonitoredAgent:
    """
    Wrapper for LangChain agents that adds comprehensive observability.
    
    This class wraps a LangChain AgentExecutor and adds tracing, logging,
    and monitoring capabilities while maintaining the original agent's interface.
    """
    
    def __init__(self, agent: AgentExecutor, observer: AgentObserver, config: ObserverConfig):
        """
        Initialize the monitored agent.
        
        Args:
            agent: The LangChain agent to wrap
            observer: The AgentObserver instance
            config: Configuration for observability
        """
        self.agent = agent
        self.observer = observer
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Store original callbacks
        self.original_callbacks = getattr(self.agent, 'callbacks', [])
        
        self.logger.info("MonitoredAgent initialized successfully")
    
    def run(self, input_data: Union[str, Dict[str, Any]], **kwargs) -> Any:
        """
        Run the agent with observability.
        
        Args:
            input_data: Input data for the agent
            **kwargs: Additional arguments
            
        Returns:
            Any: The agent's output
        """
        trace_id = str(uuid.uuid4())
        
        try:
            # Start trace
            self.observer.start_trace(trace_id, input_data, kwargs)
            
            # Create callback handler for this run
            callback_handler = ObservabilityCallbackHandler(self.observer, trace_id)
            
            # Add callback handler to agent
            if not hasattr(self.agent, 'callbacks'):
                self.agent.callbacks = []
            
            self.agent.callbacks.append(callback_handler)
            
            # Run the agent
            result = self.agent.run(input_data, **kwargs)
            
            # End trace successfully
            self.observer.end_trace(trace_id, result)
            
            return result
            
        except Exception as e:
            # End trace with error
            self.observer.end_trace(trace_id, None, e)
            raise
        finally:
            # Clean up callback handler
            if hasattr(self.agent, 'callbacks') and callback_handler in self.agent.callbacks:
                self.agent.callbacks.remove(callback_handler)
    
    async def arun(self, input_data: Union[str, Dict[str, Any]], **kwargs) -> Any:
        """
        Run the agent asynchronously with observability.
        
        Args:
            input_data: Input data for the agent
            **kwargs: Additional arguments
            
        Returns:
            Any: The agent's output
        """
        trace_id = str(uuid.uuid4())
        
        try:
            # Start trace
            self.observer.start_trace(trace_id, input_data, kwargs)
            
            # Create callback handler for this run
            callback_handler = ObservabilityCallbackHandler(self.observer, trace_id)
            
            # Add callback handler to agent
            if not hasattr(self.agent, 'callbacks'):
                self.agent.callbacks = []
            
            self.agent.callbacks.append(callback_handler)
            
            # Run the agent asynchronously
            result = await self.agent.arun(input_data, **kwargs)
            
            # End trace successfully
            self.observer.end_trace(trace_id, result)
            
            return result
            
        except Exception as e:
            # End trace with error
            self.observer.end_trace(trace_id, None, e)
            raise
        finally:
            # Clean up callback handler
            if hasattr(self.agent, 'callbacks') and callback_handler in self.agent.callbacks:
                self.agent.callbacks.remove(callback_handler)
    
    def invoke(self, input_data: Union[str, Dict[str, Any]], **kwargs) -> Any:
        """
        Invoke the agent with observability.
        
        Args:
            input_data: Input data for the agent
            **kwargs: Additional arguments
            
        Returns:
            Any: The agent's output
        """
        trace_id = str(uuid.uuid4())
        
        try:
            # Start trace
            self.observer.start_trace(trace_id, input_data, kwargs)
            
            # Create callback handler for this run
            callback_handler = ObservabilityCallbackHandler(self.observer, trace_id)
            
            # Add callback handler to agent
            if not hasattr(self.agent, 'callbacks'):
                self.agent.callbacks = []
            
            self.agent.callbacks.append(callback_handler)
            
            # Invoke the agent
            result = self.agent.invoke(input_data, **kwargs)
            
            # End trace successfully
            self.observer.end_trace(trace_id, result)
            
            return result
            
        except Exception as e:
            # End trace with error
            self.observer.end_trace(trace_id, None, e)
            raise
        finally:
            # Clean up callback handler
            if hasattr(self.agent, 'callbacks') and callback_handler in self.agent.callbacks:
                self.agent.callbacks.remove(callback_handler)
    
    async def ainvoke(self, input_data: Union[str, Dict[str, Any]], **kwargs) -> Any:
        """
        Invoke the agent asynchronously with observability.
        
        Args:
            input_data: Input data for the agent
            **kwargs: Additional arguments
            
        Returns:
            Any: The agent's output
        """
        trace_id = str(uuid.uuid4())
        
        try:
            # Start trace
            self.observer.start_trace(trace_id, input_data, kwargs)
            
            # Create callback handler for this run
            callback_handler = ObservabilityCallbackHandler(self.observer, trace_id)
            
            # Add callback handler to agent
            if not hasattr(self.agent, 'callbacks'):
                self.agent.callbacks = []
            
            self.agent.callbacks.append(callback_handler)
            
            # Invoke the agent asynchronously
            result = await self.agent.ainvoke(input_data, **kwargs)
            
            # End trace successfully
            self.observer.end_trace(trace_id, result)
            
            return result
            
        except Exception as e:
            # End trace with error
            self.observer.end_trace(trace_id, None, e)
            raise
        finally:
            # Clean up callback handler
            if hasattr(self.agent, 'callbacks') and callback_handler in self.agent.callbacks:
                self.agent.callbacks.remove(callback_handler)
    
    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped agent.
        
        Args:
            name: Attribute name
            
        Returns:
            Any: The attribute value
        """
        return getattr(self.agent, name)
    
    def __setattr__(self, name, value):
        """
        Set attribute on the appropriate object.
        
        Args:
            name: Attribute name
            value: Attribute value
        """
        if name in ['agent', 'observer', 'config', 'logger', 'original_callbacks']:
            super().__setattr__(name, value)
        else:
            setattr(self.agent, name, value) 