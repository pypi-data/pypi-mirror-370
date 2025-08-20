"""
OpenTelemetry integration for CrewAI framework adapter.

This module provides integration between the existing OpenTelemetry CrewAI
instrumentation and our agent observability system.
"""

import logging
from typing import Any, Optional


def enable_crewai_instrumentation(observer: Any, config: Any) -> bool:
    """
    Enable CrewAI OpenTelemetry instrumentation and integrate it with our observability system.
    
    Args:
        observer: The AgentObserver instance
        config: Configuration object
        
    Returns:
        bool: True if instrumentation was successfully enabled
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Import the CrewAI instrumentor from the existing package
        from ...opentelemetry_instrumentation_crewai.opentelemetry.instrumentation.crewai import CrewAIInstrumentor
        
        # Create and configure the instrumentor
        instrumentor = CrewAIInstrumentor()
        
        # Check if already instrumented
        if instrumentor.is_instrumented_by_opentelemetry:
            logger.debug("CrewAI is already instrumented")
            return True
        
        # Set up the tracer and meter providers if needed
        tracer_provider = _setup_tracer_provider(observer, config)
        meter_provider = _setup_meter_provider(observer, config)
        
        # Instrument CrewAI
        instrumentor.instrument(
            tracer_provider=tracer_provider,
            meter_provider=meter_provider
        )
        
        logger.info("CrewAI OpenTelemetry instrumentation enabled successfully")
        return True
        
    except ImportError as e:
        logger.warning(f"CrewAI OpenTelemetry instrumentation not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to enable CrewAI instrumentation: {e}")
        return False


def disable_crewai_instrumentation() -> bool:
    """
    Disable CrewAI OpenTelemetry instrumentation.
    
    Returns:
        bool: True if instrumentation was successfully disabled
    """
    logger = logging.getLogger(__name__)
    
    try:
        from ...opentelemetry_instrumentation_crewai.opentelemetry.instrumentation.crewai import CrewAIInstrumentor
        
        instrumentor = CrewAIInstrumentor()
        
        if instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.uninstrument()
            logger.info("CrewAI OpenTelemetry instrumentation disabled")
            return True
        else:
            logger.debug("CrewAI is not currently instrumented")
            return True
            
    except ImportError as e:
        logger.warning(f"CrewAI OpenTelemetry instrumentation not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to disable CrewAI instrumentation: {e}")
        return False


def _setup_tracer_provider(observer: Any, config: Any) -> Optional[Any]:
    """
    Set up the tracer provider for CrewAI instrumentation.
    
    Args:
        observer: The AgentObserver instance
        config: Configuration object
        
    Returns:
        Tracer provider instance or None
    """
    logger = logging.getLogger(__name__)
    
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        # Check if there's already a tracer provider
        current_provider = trace.get_tracer_provider()
        if hasattr(current_provider, 'get_tracer'):
            # Use existing provider
            return current_provider
        
        # Create a new tracer provider
        tracer_provider = TracerProvider()
        
        # Add a custom span processor that integrates with our observer
        span_processor = ObserverSpanProcessor(observer, config)
        tracer_provider.add_span_processor(span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        logger.debug("Tracer provider set up successfully")
        return tracer_provider
        
    except Exception as e:
        logger.error(f"Failed to setup tracer provider: {e}")
        return None


def _setup_meter_provider(observer: Any, config: Any) -> Optional[Any]:
    """
    Set up the meter provider for CrewAI instrumentation.
    
    Args:
        observer: The AgentObserver instance
        config: Configuration object
        
    Returns:
        Meter provider instance or None
    """
    logger = logging.getLogger(__name__)
    
    try:
        from opentelemetry import metrics
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        
        # Check if there's already a meter provider
        current_provider = metrics.get_meter_provider()
        if hasattr(current_provider, 'get_meter'):
            # Use existing provider
            return current_provider
        
        # Create a new meter provider
        meter_provider = MeterProvider()
        
        # Add a custom metric reader that integrates with our observer
        metric_reader = ObserverMetricReader(observer, config)
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        
        # Set as global meter provider
        metrics.set_meter_provider(meter_provider)
        
        logger.debug("Meter provider set up successfully")
        return meter_provider
        
    except Exception as e:
        logger.error(f"Failed to setup meter provider: {e}")
        return None


class ObserverSpanProcessor:
    """
    Custom span processor that integrates OpenTelemetry spans with our observer system.
    """
    
    def __init__(self, observer: Any, config: Any):
        """
        Initialize the span processor.
        
        Args:
            observer: The AgentObserver instance
            config: Configuration object
        """
        self.observer = observer
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def on_start(self, span: Any, parent_context: Any = None) -> None:
        """Called when a span starts."""
        try:
            # Extract span information
            span_name = span.name
            span_attributes = dict(span.attributes) if span.attributes else {}
            
            # Create a trace in our observer system
            trace_id = str(span.context.span_id)
            
            # Convert OpenTelemetry attributes to our format
            trace_data = {
                "span_name": span_name,
                "span_kind": str(span.kind),
                "attributes": span_attributes,
                "start_time": span.start_time
            }
            
            self.observer.start_trace(trace_id, trace_data)
            
        except Exception as e:
            self.logger.error(f"Error in span processor on_start: {e}")
    
    def on_end(self, span: Any) -> None:
        """Called when a span ends."""
        try:
            trace_id = str(span.context.span_id)
            
            # Extract final span information
            output_data = {
                "span_name": span.name,
                "status": str(span.status.status_code),
                "attributes": dict(span.attributes) if span.attributes else {},
                "end_time": span.end_time,
                "duration": span.end_time - span.start_time if span.end_time and span.start_time else None
            }
            
            # Check if the span has an error
            error = None
            if span.status.status_code.name == 'ERROR':
                error = Exception(span.status.description or "Unknown error")
            
            self.observer.end_trace(trace_id, output_data, error)
            
        except Exception as e:
            self.logger.error(f"Error in span processor on_end: {e}")
    
    def shutdown(self) -> bool:
        """Shutdown the span processor."""
        self.logger.debug("Span processor shutdown")
        return True
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush the span processor."""
        self.logger.debug("Span processor force flush")
        return True


class ObserverMetricReader:
    """
    Custom metric reader that integrates OpenTelemetry metrics with our observer system.
    """
    
    def __init__(self, observer: Any, config: Any):
        """
        Initialize the metric reader.
        
        Args:
            observer: The AgentObserver instance
            config: Configuration object
        """
        self.observer = observer
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def collect(self, timeout_millis: int = 10000) -> Any:
        """Collect metrics."""
        try:
            # For now, we'll just log that metrics are being collected
            # In a full implementation, you might want to extract and forward
            # metrics to your observer system
            self.logger.debug("Collecting metrics from CrewAI instrumentation")
            return None
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return None
    
    def shutdown(self, timeout_millis: int = 30000) -> bool:
        """Shutdown the metric reader."""
        self.logger.debug("Metric reader shutdown")
        return True 