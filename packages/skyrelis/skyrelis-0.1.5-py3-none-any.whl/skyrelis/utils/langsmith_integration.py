"""
LangSmith integration for sending trace data to LangSmith.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..config.observer_config import ObserverConfig


class LangSmithIntegration:
    """
    Integration with LangSmith for trace visualization and analysis.
    
    This class handles sending trace data to LangSmith for visualization,
    debugging, and analysis purposes.
    """
    
    def __init__(self, config: ObserverConfig):
        """
        Initialize the LangSmith integration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up LangSmith environment variables
        self._setup_langsmith_env()
        
        # Import LangSmith client
        try:
            from langsmith import Client
            self.client = Client()
            self.logger.info("LangSmith integration initialized successfully")
        except ImportError:
            self.logger.warning("LangSmith client not available. Install with: pip install langsmith")
            self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize LangSmith client: {e}")
            self.client = None
    
    def _setup_langsmith_env(self):
        """Set up LangSmith environment variables."""
        if self.config.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.config.langsmith_api_key
        
        if self.config.langsmith_project:
            os.environ["LANGSMITH_PROJECT"] = self.config.langsmith_project
        
        if self.config.langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
        else:
            os.environ["LANGSMITH_TRACING"] = "false"
        
        self.logger.debug("LangSmith environment variables configured")
    
    def start_trace(self, trace_data: Dict[str, Any]):
        """
        Start a trace in LangSmith.
        
        Args:
            trace_data: Trace data
        """
        if not self.client:
            return
        
        try:
            # LangSmith automatically handles trace creation when using LangChain
            # This method is mainly for logging and custom trace metadata
            trace_id = trace_data.get('trace_id')
            self.logger.debug(f"LangSmith trace started: {trace_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to start LangSmith trace: {e}")
    
    def add_step(self, trace_id: str, step_data: Dict[str, Any]):
        """
        Add a step to a LangSmith trace.
        
        Args:
            trace_id: The trace ID
            step_data: Step data
        """
        if not self.client:
            return
        
        try:
            # LangSmith automatically captures steps through LangChain callbacks
            # This method is mainly for logging and custom step metadata
            step_type = step_data.get('step_type', 'unknown')
            self.logger.debug(f"LangSmith step added to {trace_id}: {step_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to add LangSmith step: {e}")
    
    def end_trace(self, trace_id: str, trace_data: Dict[str, Any]):
        """
        End a trace in LangSmith.
        
        Args:
            trace_id: The trace ID
            trace_data: Complete trace data
        """
        if not self.client:
            return
        
        try:
            # LangSmith automatically handles trace completion when using LangChain
            # This method is mainly for logging and custom trace metadata
            status = trace_data.get('status', 'unknown')
            duration = trace_data.get('duration', 0)
            
            self.logger.debug(f"LangSmith trace ended: {trace_id} ({status}, {duration:.2f}s)")
            
        except Exception as e:
            self.logger.error(f"Failed to end LangSmith trace: {e}")
    
    def create_run(self, trace_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a custom run in LangSmith.
        
        Args:
            trace_data: Trace data
            
        Returns:
            Optional[str]: Run ID if successful, None otherwise
        """
        if not self.client:
            return None
        
        try:
            from langsmith import Run
            
            # Create a custom run
            run = Run(
                name=f"Custom Trace - {trace_data.get('trace_id', 'unknown')}",
                inputs=trace_data.get('input_data', {}),
                outputs=trace_data.get('output_data', {}),
                start_time=trace_data.get('start_time'),
                end_time=trace_data.get('end_time'),
                error=trace_data.get('error'),
                tags=list(trace_data.get('custom_tags', {}).keys()),
                extra=trace_data.get('custom_metadata', {})
            )
            
            run_id = self.client.create_run(run)
            self.logger.debug(f"Created LangSmith run: {run_id}")
            return run_id
            
        except Exception as e:
            self.logger.error(f"Failed to create LangSmith run: {e}")
            return None
    
    def update_run(self, run_id: str, trace_data: Dict[str, Any]):
        """
        Update a LangSmith run with additional data.
        
        Args:
            run_id: The run ID
            trace_data: Updated trace data
        """
        if not self.client:
            return
        
        try:
            self.client.update_run(
                run_id,
                outputs=trace_data.get('output_data', {}),
                end_time=trace_data.get('end_time'),
                error=trace_data.get('error')
            )
            
            self.logger.debug(f"Updated LangSmith run: {run_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update LangSmith run: {e}")
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a LangSmith run by ID.
        
        Args:
            run_id: The run ID
            
        Returns:
            Optional[Dict[str, Any]]: Run data if found, None otherwise
        """
        if not self.client:
            return None
        
        try:
            run = self.client.read_run(run_id)
            return run.dict() if run else None
            
        except Exception as e:
            self.logger.error(f"Failed to get LangSmith run: {e}")
            return None
    
    def list_runs(self, limit: int = 100, **filters) -> list:
        """
        List LangSmith runs with filters.
        
        Args:
            limit: Maximum number of runs to return
            **filters: Additional filters
            
        Returns:
            list: List of runs
        """
        if not self.client:
            return []
        
        try:
            runs = self.client.list_runs(limit=limit, **filters)
            return [run.dict() for run in runs]
            
        except Exception as e:
            self.logger.error(f"Failed to list LangSmith runs: {e}")
            return []
    
    def share_run(self, run_id: str, share_token: Optional[str] = None) -> Optional[str]:
        """
        Share a LangSmith run and get a shareable URL.
        
        Args:
            run_id: The run ID
            share_token: Optional share token
            
        Returns:
            Optional[str]: Shareable URL if successful, None otherwise
        """
        if not self.client:
            return None
        
        try:
            share_url = self.client.share_run(run_id, share_token=share_token)
            self.logger.debug(f"Shared LangSmith run: {share_url}")
            return share_url
            
        except Exception as e:
            self.logger.error(f"Failed to share LangSmith run: {e}")
            return None
    
    def get_project_url(self) -> Optional[str]:
        """
        Get the URL for the current LangSmith project.
        
        Returns:
            Optional[str]: Project URL if available, None otherwise
        """
        if not self.config.langsmith_project:
            return None
        
        try:
            # Construct LangSmith project URL
            base_url = "https://smith.langchain.com"
            project_url = f"{base_url}/o/default/p/{self.config.langsmith_project}"
            return project_url
            
        except Exception as e:
            self.logger.error(f"Failed to construct project URL: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if LangSmith integration is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.client is not None and self.config.langsmith_api_key is not None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the LangSmith integration.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            'available': self.is_available(),
            'api_key_configured': self.config.langsmith_api_key is not None,
            'project_configured': self.config.langsmith_project is not None,
            'tracing_enabled': self.config.langsmith_tracing,
            'project_url': self.get_project_url()
        } 