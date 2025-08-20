"""
Simplified remote observer client for sending traces to a remote monitor.

This module provides a lightweight client for sending trace data to a remote
observability monitor without the full monitoring capabilities.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import aiohttp
import requests

from ..config.observer_config import ObserverConfig


def _json_serialize_datetime(obj):
    """JSON serializer for datetime, UUID, and LangChain objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # Handle UUID objects
    if isinstance(obj, UUID):
        return str(obj)
    
    # Handle LangChain StructuredTool objects
    if hasattr(obj, '__class__') and 'StructuredTool' in str(type(obj)):
        return {
            'name': getattr(obj, 'name', 'unknown'),
            'description': getattr(obj, 'description', ''),
            'type': 'StructuredTool'
        }
    
    # Handle other complex objects by converting to string representation
    if hasattr(obj, '__dict__'):
        return str(obj)
    
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class RemoteObserverClient:
    """
    Lightweight client for sending traces to a remote observability monitor.
    
    This client is designed for the decorators package and only handles
    sending trace data to a remote monitor, not collecting or processing traces.
    """
    
    def __init__(self, config: ObserverConfig):
        """
        Initialize the remote observer client.
        
        Args:
            config: Configuration object containing remote observer settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.remote_observer_url.rstrip('/')
        
        if not self.base_url:
            raise ValueError("Remote observer URL is required")
        
        self.session = None
        self.logger.info(f"RemoteObserverClient initialized for {self.base_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def send_trace_async(self, trace_data: Dict[str, Any]) -> bool:
        """
        Send trace data to the remote observer asynchronously.
        
        Args:
            trace_data: The trace data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = await self._get_session()
            
            # Add metadata to trace
            enriched_trace = self._enrich_trace_data(trace_data)
            
            # Send to remote observer
            async with session.post(
                f"{self.base_url}/api/traces",
                data=json.dumps(enriched_trace, default=_json_serialize_datetime),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    self.logger.debug(f"Trace sent successfully: {trace_data.get('trace_id', 'unknown')}")
                    return True
                else:
                    self.logger.warning(f"Failed to send trace: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending trace: {e}")
            return False
    
    def send_trace_sync(self, trace_data: Dict[str, Any]) -> bool:
        """
        Send trace data to the remote observer synchronously.
        
        Args:
            trace_data: The trace data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata to trace
            enriched_trace = self._enrich_trace_data(trace_data)
            
            # Send to remote observer
            response = requests.post(
                f"{self.base_url}/api/traces",
                data=json.dumps(enriched_trace, default=_json_serialize_datetime),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Trace sent successfully: {trace_data.get('trace_id', 'unknown')}")
                return True
            else:
                self.logger.warning(f"Failed to send trace: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending trace: {e}")
            return False
    
    def send_trace_batch(self, traces: list[Dict[str, Any]]) -> bool:
        """
        Send multiple traces to the remote observer.
        
        Args:
            traces: List of trace data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Enrich all traces
            enriched_traces = [self._enrich_trace_data(trace) for trace in traces]
            
            # Send batch to remote observer
            response = requests.post(
                f"{self.base_url}/api/traces/batch",
                json=enriched_traces,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Batch of {len(traces)} traces sent successfully")
                return True
            else:
                self.logger.warning(f"Failed to send trace batch: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending trace batch: {e}")
            return False
    
    def _enrich_trace_data(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform trace data to match cloud monitor API format.
        
        Args:
            trace_data: Original trace data from agent_decorators
            
        Returns:
            Dict: Trace data in cloud monitor format
        """
        # Generate IDs and timestamps
        trace_id = trace_data.get("trace_id", str(uuid.uuid4()))
        current_time = datetime.utcnow()
        start_time = trace_data.get("start_time", current_time)
        end_time = trace_data.get("end_time", current_time)
        
        # Convert datetime objects to ISO strings if needed
        if isinstance(start_time, datetime):
            start_time = start_time.isoformat()
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()
        
        # Calculate duration if not provided
        duration = trace_data.get("duration", 0.0)
        if duration == 0.0 and trace_data.get("start_time") and trace_data.get("end_time"):
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if isinstance(start_time, str) else start_time
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if isinstance(end_time, str) else end_time
                duration = (end - start).total_seconds()
            except:
                duration = 1.0  # Default duration
        
        # Extract agent_id from metadata or custom_metadata
        agent_id = None
        if "metadata" in trace_data and trace_data["metadata"]:
            agent_id = trace_data["metadata"].get("agent_id")
        if not agent_id and "custom_metadata" in trace_data:
            agent_id = trace_data["custom_metadata"].get("agent_id")
        
        # Transform to cloud monitor format
        cloud_trace = {
            "trace_id": trace_id,
            "agent_id": agent_id,  # Include agent_id in the main trace data
            "status": trace_data.get("status", "completed"),
            "action_type": trace_data.get("action_type", "agent_run"),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "input_data": str(trace_data.get("input_data", trace_data.get("input", ""))),
            "output_data": str(trace_data.get("output_data", trace_data.get("output", ""))),
            "spans": self._transform_spans(trace_data.get("spans", trace_data.get("steps", []))),
            "tags": {
                "environment": "production",
                "version": "1.0.0",
                "agent_type": "assistant",
                "action_type": trace_data.get("action_type", "agent_run"),
                "client": "agent_decorators"
            },
            "metadata": {
                "user_id": trace_data.get("user_id", f"user_{int(time.time() % 1000)}"),
                "session_id": trace_data.get("session_id", f"session_{int(time.time() % 10000)}"),
                "request_id": trace_data.get("request_id", str(uuid.uuid4())),
                "agent_name": trace_data.get("agent_name", getattr(self.config, 'agent_name', 'unnamed_agent')),
                "agent_id": agent_id  # Also include in metadata for backward compatibility
            }
        }
        
        # Add custom metadata if present (including system_prompts)
        if "custom_metadata" in trace_data and trace_data["custom_metadata"]:
            for key, value in trace_data["custom_metadata"].items():
                if key not in cloud_trace["metadata"]:  # Don't override existing metadata
                    cloud_trace["metadata"][key] = value
        
        # Add error information if present
        if trace_data.get("error") or trace_data.get("status") == "error":
            error_info = trace_data.get("error", {})
            if isinstance(error_info, str):
                error_info = {"message": error_info}
            
            cloud_trace["error"] = {
                "message": error_info.get("message", trace_data.get("error_message", "Unknown error")),
                "type": error_info.get("type", "RuntimeError"),
                "timestamp": error_info.get("timestamp", current_time.isoformat())
            }
        
        return cloud_trace
    
    def _transform_spans(self, spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform spans/steps to cloud monitor format."""
        transformed_spans = []
        
        for span in spans:
            if isinstance(span, dict):
                transformed_span = {
                    "name": span.get("name", span.get("step_type", "unknown_span")),
                    "start_time": span.get("start_time", datetime.utcnow().isoformat()),
                    "end_time": span.get("end_time", datetime.utcnow().isoformat()),
                    "attributes": {
                        "step_id": span.get("step_id", ""),
                        "step_type": span.get("step_type", ""),
                        "status": span.get("status", "completed"),
                        **span.get("data", {}),
                        **span.get("attributes", {})
                    }
                }
                transformed_spans.append(transformed_span)
        
        return transformed_spans
    
    async def health_check(self) -> bool:
        """
        Check if the remote observer is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/api/health") as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def health_check_sync(self) -> bool:
        """
        Check if the remote observer is healthy (synchronous).
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Note: This is not ideal, but we can't use async in __del__
            # In production, users should call close() explicitly
            pass 