"""
OpenTelemetry integration for enterprise-grade distributed tracing.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..config.observer_config import ObserverConfig


class OpenTelemetryIntegration:
    """
    Integration with OpenTelemetry for enterprise-grade distributed tracing.
    
    This class provides OpenTelemetry instrumentation for comprehensive
    tracing across distributed systems.
    """
    
    def __init__(self, config: ObserverConfig):
        """
        Initialize the OpenTelemetry integration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenTelemetry components
        self.tracer = None
        self.meter = None
        self.exporter = None
        
        # Set up OpenTelemetry if enabled
        if self.config.enable_opentelemetry:
            self._setup_opentelemetry()
        
        self.logger.info("OpenTelemetry integration initialized")
    
    def _setup_opentelemetry(self):
        """Set up OpenTelemetry instrumentation."""
        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.instrumentation.requests import RequestsInstrumentor
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
            
            # Set up trace provider
            trace_provider = TracerProvider()
            trace.set_tracer_provider(trace_provider)
            
            # Set up meter provider
            metric_reader = PeriodicExportingMetricReader(
                JaegerExporter(endpoint=self.config.otel_endpoint)
            )
            meter_provider = MeterProvider(metric_reader=metric_reader)
            metrics.set_meter_provider(meter_provider)
            
            # Create tracer and meter
            self.tracer = trace.get_tracer(__name__)
            self.meter = metrics.get_meter(__name__)
            
            # Set up exporter if endpoint is configured
            if self.config.otel_endpoint:
                self.exporter = JaegerExporter(endpoint=self.config.otel_endpoint)
                span_processor = BatchSpanProcessor(self.exporter)
                trace_provider.add_span_processor(span_processor)
            
            # Instrument HTTP libraries
            RequestsInstrumentor().instrument()
            HTTPXClientInstrumentor().instrument()
            
            self.logger.info("OpenTelemetry setup completed successfully")
            
        except ImportError:
            self.logger.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation opentelemetry-exporter-jaeger")
        except Exception as e:
            self.logger.error(f"Failed to setup OpenTelemetry: {e}")
    
    def start_trace(self, trace_data: Dict[str, Any]):
        """
        Start a trace with OpenTelemetry.
        
        Args:
            trace_data: Trace data
        """
        if not self.tracer:
            return
        
        try:
            trace_id = trace_data.get('trace_id', 'unknown')
            span_name = f"agent_trace_{trace_id[:8]}"
            
            # Create span with attributes
            span = self.tracer.start_span(
                name=span_name,
                attributes={
                    "trace.id": trace_id,
                    "agent.input": str(trace_data.get('input_data', '')),
                    "agent.status": trace_data.get('status', 'running'),
                    "agent.start_time": str(trace_data.get('start_time', '')),
                }
            )
            
            # Add custom attributes
            for key, value in trace_data.get('custom_tags', {}).items():
                span.set_attribute(f"custom.{key}", str(value))
            
            # Store span for later use
            trace_data['_otel_span'] = span
            
            self.logger.debug(f"OpenTelemetry trace started: {trace_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to start OpenTelemetry trace: {e}")
    
    def add_step(self, trace_id: str, step_data: Dict[str, Any]):
        """
        Add a step to an OpenTelemetry trace.
        
        Args:
            trace_id: The trace ID
            step_data: Step data
        """
        if not self.tracer:
            return
        
        try:
            step_type = step_data.get('step_type', 'unknown')
            step_id = step_data.get('step_id', 'unknown')
            
            # Create child span for the step
            with self.tracer.start_span(
                name=f"step_{step_type}",
                attributes={
                    "step.id": step_id,
                    "step.type": step_type,
                    "step.timestamp": str(step_data.get('timestamp', '')),
                }
            ) as step_span:
                # Add step-specific attributes
                if step_type == 'llm_start':
                    step_span.set_attribute("llm.name", step_data.get('data', {}).get('llm_name', 'unknown'))
                elif step_type == 'tool_start':
                    step_span.set_attribute("tool.name", step_data.get('data', {}).get('tool_name', 'unknown'))
                elif step_type == 'agent_action':
                    action = step_data.get('data', {}).get('action', {})
                    step_span.set_attribute("action.tool", action.get('tool', 'unknown'))
                    step_span.set_attribute("action.input", action.get('tool_input', ''))
                
                # Add step data as events
                step_span.add_event("step.data", attributes=step_data.get('data', {}))
            
            self.logger.debug(f"OpenTelemetry step added: {step_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to add OpenTelemetry step: {e}")
    
    def end_trace(self, trace_id: str, trace_data: Dict[str, Any]):
        """
        End an OpenTelemetry trace.
        
        Args:
            trace_id: The trace ID
            trace_data: Complete trace data
        """
        if not self.tracer:
            return
        
        try:
            span = trace_data.get('_otel_span')
            if not span:
                return
            
            # Update span attributes
            span.set_attribute("agent.status", trace_data.get('status', 'unknown'))
            span.set_attribute("agent.duration", trace_data.get('duration', 0))
            span.set_attribute("agent.steps_count", len(trace_data.get('steps', [])))
            
            if trace_data.get('output_data'):
                span.set_attribute("agent.output", str(trace_data.get('output_data', '')))
            
            if trace_data.get('error'):
                error = trace_data.get('error', {})
                span.set_attribute("agent.error.type", error.get('type', 'unknown'))
                span.set_attribute("agent.error.message", error.get('message', ''))
                span.record_exception(Exception(error.get('message', 'Unknown error')))
            
            # End the span
            span.end()
            
            # Record metrics
            self._record_metrics(trace_data)
            
            self.logger.debug(f"OpenTelemetry trace ended: {trace_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to end OpenTelemetry trace: {e}")
    
    def _record_metrics(self, trace_data: Dict[str, Any]):
        """
        Record metrics for the trace.
        
        Args:
            trace_data: Trace data
        """
        if not self.meter:
            return
        
        try:
            # Create counters and histograms
            trace_counter = self.meter.create_counter("agent.traces.total")
            duration_histogram = self.meter.create_histogram("agent.trace.duration")
            error_counter = self.meter.create_counter("agent.traces.errors")
            
            # Record trace count
            trace_counter.add(1, {
                "status": trace_data.get('status', 'unknown'),
                "has_error": str(bool(trace_data.get('error'))).lower()
            })
            
            # Record duration
            duration = trace_data.get('duration', 0)
            if duration > 0:
                duration_histogram.record(duration, {
                    "status": trace_data.get('status', 'unknown')
                })
            
            # Record errors
            if trace_data.get('error'):
                error_counter.add(1, {
                    "error_type": trace_data.get('error', {}).get('type', 'unknown')
                })
            
        except Exception as e:
            self.logger.error(f"Failed to record OpenTelemetry metrics: {e}")
    
    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Create a custom span.
        
        Args:
            name: Span name
            attributes: Span attributes
            
        Returns:
            Optional: Span object if available
        """
        if not self.tracer:
            return None
        
        try:
            span = self.tracer.start_span(name)
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            return span
            
        except Exception as e:
            self.logger.error(f"Failed to create OpenTelemetry span: {e}")
            return None
    
    def add_event(self, span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Add an event to a span.
        
        Args:
            span: The span to add the event to
            name: Event name
            attributes: Event attributes
        """
        if not span:
            return
        
        try:
            span.add_event(name, attributes or {})
        except Exception as e:
            self.logger.error(f"Failed to add OpenTelemetry event: {e}")
    
    def set_attribute(self, span, key: str, value: Any):
        """
        Set an attribute on a span.
        
        Args:
            span: The span to set the attribute on
            key: Attribute key
            value: Attribute value
        """
        if not span:
            return
        
        try:
            span.set_attribute(key, str(value))
        except Exception as e:
            self.logger.error(f"Failed to set OpenTelemetry attribute: {e}")
    
    def is_available(self) -> bool:
        """
        Check if OpenTelemetry integration is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return (
            self.config.enable_opentelemetry and
            self.tracer is not None and
            self.config.otel_endpoint is not None
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the OpenTelemetry integration.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            'enabled': self.config.enable_opentelemetry,
            'available': self.is_available(),
            'tracer_initialized': self.tracer is not None,
            'meter_initialized': self.meter is not None,
            'exporter_configured': self.exporter is not None,
            'endpoint_configured': self.config.otel_endpoint is not None
        }
    
    def shutdown(self):
        """Shutdown OpenTelemetry components."""
        try:
            if self.exporter:
                self.exporter.shutdown()
            
            self.logger.info("OpenTelemetry integration shutdown")
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown OpenTelemetry: {e}") 