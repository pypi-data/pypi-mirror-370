"""
Configuration class for the AI Agent Observability System.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ObserverConfig(BaseModel):
    """
    Configuration for the AI Agent Observability System.
    
    This class manages all configuration settings for tracing, logging,
    and monitoring capabilities.
    """
    
    # Agent Configuration
    agent_name: Optional[str] = Field(
        default=None,
        description="Name of the agent being monitored"
    )
    
    # LangSmith Configuration
    enable_langsmith: bool = Field(
        default=True,
        description="Enable LangSmith integration for trace visualization"
    )
    langsmith_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key (will use environment variable if not provided)"
    )
    langsmith_project: str = Field(
        default="default",
        description="LangSmith project name"
    )
    langsmith_tracing: bool = Field(
        default=True,
        description="Enable LangSmith tracing"
    )
    
    # Local Logging Configuration
    enable_local_logging: bool = Field(
        default=True,
        description="Enable local logging of traces"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (if None, logs to console)"
    )
    
    # OpenTelemetry Configuration
    enable_opentelemetry: bool = Field(
        default=False,
        description="Enable OpenTelemetry integration for enterprise tracing"
    )
    otel_endpoint: Optional[str] = Field(
        default=None,
        description="OpenTelemetry collector endpoint"
    )
    
    # Monitor Configuration
    enable_monitor: bool = Field(
        default=True,
        description="Enable real-time monitoring dashboard"
    )
    monitor_host: str = Field(
        default="localhost",
        description="Monitor web server host"
    )
    monitor_port: int = Field(
        default=8000,
        description="Monitor web server port"
    )
    
    # Standalone Observer API Configuration
    enable_remote_observer: bool = Field(
        default=False,
        description="Enable sending traces to remote standalone observer"
    )
    remote_observer_url: str = Field(
        default="http://localhost:8000",
        description="URL of the standalone observer API"
    )
    remote_observer_api_key: Optional[str] = Field(
        default=None,
        description="API key for remote observer authentication"
    )
    remote_observer_timeout: int = Field(
        default=10,
        description="Timeout for remote observer API calls (seconds)"
    )
    
    # Redis Configuration (for persistent storage)
    enable_redis: bool = Field(
        default=False,
        description="Enable Redis for persistent trace storage"
    )
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Custom Configuration
    custom_tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom tags to add to all traces"
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata to add to all traces"
    )
    
    # Performance Configuration
    max_trace_history: int = Field(
        default=1000,
        description="Maximum number of traces to keep in memory"
    )
    trace_sampling_rate: float = Field(
        default=1.0,
        description="Trace sampling rate (0.0 to 1.0)"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
    
    def __init__(self, **data):
        """Initialize configuration with environment variable fallbacks."""
        # Set defaults from environment variables if not provided
        if "langsmith_api_key" not in data:
            data["langsmith_api_key"] = os.getenv("LANGSMITH_API_KEY")
        
        if "langsmith_project" not in data:
            data["langsmith_project"] = os.getenv("LANGSMITH_PROJECT", "default")
        
        if "langsmith_tracing" not in data:
            data["langsmith_tracing"] = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
        
        if "monitor_host" not in data:
            data["monitor_host"] = os.getenv("MONITOR_HOST", "localhost")
        
        if "monitor_port" not in data:
            data["monitor_port"] = int(os.getenv("MONITOR_PORT", "8000"))
        
        if "redis_url" not in data:
            data["redis_url"] = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        if "remote_observer_url" not in data:
            data["remote_observer_url"] = os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000")
        
        if "remote_observer_api_key" not in data:
            data["remote_observer_api_key"] = os.getenv("REMOTE_OBSERVER_API_KEY")
        
        if "enable_remote_observer" not in data:
            data["enable_remote_observer"] = os.getenv("ENABLE_REMOTE_OBSERVER", "false").lower() == "true"
        
        super().__init__(**data)
    
    def validate_config(self) -> bool:
        """
        Validate the configuration and return True if valid.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if self.enable_langsmith and not self.langsmith_api_key:
            raise ValueError("LangSmith API key is required when LangSmith is enabled")
        
        if self.enable_opentelemetry and not self.otel_endpoint:
            raise ValueError("OpenTelemetry endpoint is required when OpenTelemetry is enabled")
        
        if not (0.0 <= self.trace_sampling_rate <= 1.0):
            raise ValueError("Trace sampling rate must be between 0.0 and 1.0")
        
        return True
    
    def get_langsmith_config(self) -> Dict[str, Any]:
        """
        Get LangSmith-specific configuration.
        
        Returns:
            Dict[str, Any]: LangSmith configuration
        """
        return {
            "api_key": self.langsmith_api_key,
            "project": self.langsmith_project,
            "tracing": self.langsmith_tracing
        }
    
    def get_monitor_config(self) -> Dict[str, Any]:
        """
        Get monitor-specific configuration.
        
        Returns:
            Dict[str, Any]: Monitor configuration
        """
        return {
            "host": self.monitor_host,
            "port": self.monitor_port,
            "enable": self.enable_monitor
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """
        Get Redis-specific configuration.
        
        Returns:
            Dict[str, Any]: Redis configuration
        """
        return {
            "url": self.redis_url,
            "enable": self.enable_redis
        } 