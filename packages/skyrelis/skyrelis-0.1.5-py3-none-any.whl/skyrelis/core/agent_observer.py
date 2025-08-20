"""
Main AgentObserver class for adding observability to LangChain agents.
"""

import os
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage
from langchain.callbacks.base import BaseCallbackHandler

from ..config.observer_config import ObserverConfig
from ..utils.remote_observer_client import RemoteObserverClient


class AgentObserver:
    """
    Simplified class for adding observability to AI agents.
    
    This class provides basic tracing capabilities and sends trace data
    to a remote observability monitor.
    """
    
    def __init__(self, config: Optional[ObserverConfig] = None):
        """
        Initialize the AgentObserver.
        
        Args:
            config: Configuration object for observability settings
        """
        self.config = config or ObserverConfig()
        
        # Initialize remote observer client if enabled
        self.remote_observer_client = None
        if self.config.enable_remote_observer and self.config.remote_observer_url:
            self.remote_observer_client = RemoteObserverClient(self.config)
        
        # Setup logging
        self._setup_logging()
        
        # Custom metadata and tags
        self.custom_metadata: Dict[str, Any] = {}
        self.custom_tags: Dict[str, str] = {}
        
        # Track active traces
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("AgentObserver initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper())
        
        if self.config.log_file:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.config.log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.logger = logging.getLogger(__name__)
    
    def wrap_agent(self, agent: AgentExecutor):
        """
        Wrap a LangChain agent with observability capabilities.
        
        Args:
            agent: The LangChain agent to wrap
            
        Returns:
            MonitoredAgent: The wrapped agent with observability
        """
        # Lazy import to avoid circular dependency
        from .monitored_agent import MonitoredAgent
        
        self.logger.info(f"Wrapping agent with observability: {type(agent).__name__}")
        
        # Create monitored agent
        monitored_agent = MonitoredAgent(
            agent=agent,
            observer=self,
            config=self.config
        )
        
        return monitored_agent
    
    def add_custom_metadata(self, key: str, value: Any):
        """
        Add custom metadata to all traces.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.custom_metadata[key] = value
        self.logger.debug(f"Added custom metadata: {key} = {value}")
    
    def set_tags(self, tags: Dict[str, str]):
        """
        Set custom tags for all traces.
        
        Args:
            tags: Dictionary of tags to add
        """
        self.custom_tags.update(tags)
        self.logger.debug(f"Set custom tags: {tags}")
    
    def start_trace(self, trace_id: str, input_data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new trace.
        
        Args:
            trace_id: Unique identifier for the trace
            input_data: Input data for the trace
            metadata: Additional metadata for the trace
            
        Returns:
            str: The trace ID
        """
        if not self._should_sample_trace():
            return trace_id
        
        trace_data = {
            "trace_id": trace_id,
            "start_time": datetime.utcnow(),
            "input_data": input_data,
            "metadata": metadata or {},
            "custom_metadata": self.custom_metadata.copy(),
            "custom_tags": self.custom_tags.copy(),
            "steps": [],
            "status": "running"
        }
        
        # Add configuration tags
        trace_data["custom_tags"].update(self.config.custom_tags)
        trace_data["custom_metadata"].update(self.config.custom_metadata)
        
        self.active_traces[trace_id] = trace_data
        
        # Send to remote observer if available
        if self.remote_observer_client:
            self.remote_observer_client.send_trace_sync(trace_data)
        
        self.logger.info(f"Started trace: {trace_id}")
        return trace_id
    
    def add_trace_step(self, trace_id: str, step_type: str, step_data: Dict[str, Any]):
        """
        Add a step to an active trace.
        
        Args:
            trace_id: The trace ID
            step_type: Type of step (e.g., 'tool_call', 'llm_invocation')
            step_data: Step data
        """
        if trace_id not in self.active_traces:
            self.logger.warning(f"Trace {trace_id} not found, skipping step")
            return
        
        step = {
            "step_id": str(uuid.uuid4()),
            "step_type": step_type,
            "timestamp": datetime.utcnow(),
            "data": step_data
        }
        
        self.active_traces[trace_id]["steps"].append(step)
        
        # Send updated trace to remote observer if available
        if self.remote_observer_client:
            self.remote_observer_client.send_trace_sync(self.active_traces[trace_id])
        
        self.logger.debug(f"Added step to trace {trace_id}: {step_type}")
    
    def end_trace(self, trace_id: str, output_data: Any, error: Optional[Exception] = None):
        """
        End a trace.
        
        Args:
            trace_id: The trace ID
            output_data: Output data from the trace
            error: Optional error that occurred
        """
        if trace_id not in self.active_traces:
            self.logger.warning(f"Trace {trace_id} not found, skipping end")
            return
        
        trace_data = self.active_traces[trace_id]
        trace_data["end_time"] = datetime.utcnow()
        trace_data["duration"] = (trace_data["end_time"] - trace_data["start_time"]).total_seconds()
        trace_data["output_data"] = output_data
        trace_data["status"] = "error" if error else "completed"
        
        if error:
            trace_data["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": str(error.__traceback__) if error.__traceback__ else None
            }
        
        # Send to remote observer if available
        if self.remote_observer_client:
            # Use synchronous method for compatibility
            self.remote_observer_client.send_trace_sync(trace_data)
        
        # Trace is now complete
        
        # Remove from active traces
        del self.active_traces[trace_id]
        
        status = "completed" if not error else "error"
        self.logger.info(f"Ended trace {trace_id}: {status}")
    
    def _should_sample_trace(self) -> bool:
        """
        Determine if a trace should be sampled based on sampling rate.
        
        Returns:
            bool: True if trace should be sampled
        """
        import random
        return random.random() <= self.config.trace_sampling_rate
    
    def get_trace_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get trace history from active traces.
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            List[Dict[str, Any]]: List of trace data
        """
        traces = list(self.active_traces.values())
        if limit:
            traces = traces[-limit:]
        return traces
    
    def get_active_traces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get currently active traces.
        
        Returns:
            Dict[str, Dict[str, Any]]: Active traces
        """
        return self.active_traces.copy()
    
    def clear_trace_history(self):
        """Clear active traces."""
        self.active_traces.clear()
        self.logger.info("Active traces cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get observability statistics.
        
        Returns:
            Dict[str, Any]: Statistics about traces and performance
        """
        stats = {
            "active_traces": len(self.active_traces),
            "sampling_rate": self.config.trace_sampling_rate,
            "remote_observer_enabled": self.remote_observer_client is not None
        }
        
        return stats 