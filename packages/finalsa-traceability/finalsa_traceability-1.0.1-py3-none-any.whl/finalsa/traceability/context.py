"""
Context management for traceability IDs using Python's contextvars.

This module provides thread-safe context management for correlation IDs, trace IDs,
and span IDs using Python's contextvars module. This ensures that traceability
information is properly isolated between different execution contexts (threads,
async tasks, etc.).

Example:
    Basic usage:
        from finalsa.traceability import set_context, get_context

        # Set context for current execution
        set_context(
            correlation_id="user-request-123",
            trace_id="trace-456",
            span_id="span-789"
        )

        # Get current context
        context = get_context()
        print(context["correlation_id"])  # "user-request-123-XXXXX"

    Service integration:
        # Set context from HTTP headers
        set_context_from_dict({
            "correlation_id": request.headers.get("X-Correlation-ID"),
            "trace_id": request.headers.get("X-Trace-ID"),
            "span_id": request.headers.get("X-Span-ID")
        }, service_name="my-service")
"""

from contextvars import ContextVar
from typing import Dict, Optional, Union

from finalsa.traceability.functions import (
    add_hop_to_correlation,
    default_correlation_id,
    default_span_id,
    default_trace_id,
    generate_traceparent,
    generate_tracestate,
    parse_traceparent,
    parse_tracestate,
)

# Context variables for thread-safe traceability ID management
correlation_id: ContextVar[Optional[str]] = ContextVar(
    'correlation_id',
    default=None
)
"""Context variable for correlation ID storage.

The correlation ID is used to track a request or operation across multiple services.
It gets automatically extended with hops when set via set_correlation_id().
"""

trace_id: ContextVar[Optional[str]] = ContextVar(
    'trace_id',
    default=None
)
"""Context variable for trace ID storage.

The trace ID represents a single trace spanning multiple spans/operations.
Typically follows UUID format when auto-generated.
"""

span_id: ContextVar[Optional[str]] = ContextVar(
    'span_id',
    default=None
)
"""Context variable for span ID storage.

The span ID represents a single operation or span within a trace.
Typically follows UUID format when auto-generated.
"""

other_vars: ContextVar[Optional[Dict]] = ContextVar(
    'other_vars',
    default=None
)
"""Context variable for additional custom variables.

Stores any extra key-value pairs passed to set_context() or set_context_from_dict().
"""


def get_context() -> Dict[str, Union[Optional[str], Dict]]:
    """Get the complete current traceability context.

    Returns a dictionary containing all current traceability IDs plus any
    additional variables that were set via set_context() or set_context_from_dict().

    Returns:
        Dict containing:
            - correlation_id: Current correlation ID (may be None)
            - trace_id: Current trace ID (may be None)
            - span_id: Current span ID (may be None)
            - **other_vars: Any additional custom variables

    Example:
        >>> set_context(correlation_id="test", custom_field="value")
        >>> context = get_context()
        >>> print(context)
        {
            'correlation_id': 'test-A1B2C',
            'trace_id': None,
            'span_id': None,
            'custom_field': 'value'
        }
    """
    return {
        'correlation_id': get_correlation_id(),
        'trace_id': get_trace_id(),
        'span_id': get_span_id(),
        **(other_vars.get() or {})
    }


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID.

    Returns:
        The current correlation ID or None if not set.

    Example:
        >>> set_correlation_id("user-123")
        >>> get_correlation_id()
        'user-123-A1B2C'
    """
    return correlation_id.get()


def set_correlation_id(
    value: Optional[str] = None,
    service_name: Optional[str] = None,
):
    """Set the correlation ID for the current context.

    If value is provided, it will be extended with a hop using add_hop_to_correlation().
    If value is None, a new correlation ID will be generated using the service_name.

    Args:
        value: The base correlation ID to extend with a hop. If None, generates new ID.
        service_name: Service name to use when generating new correlation ID.
                     Defaults to "DEFAULT" if not provided.

    Raises:
        AttributeError: If value is an empty string (correlation ID cannot be empty).

    Examples:
        Generate new correlation ID:
        >>> set_correlation_id(service_name="user-service")
        >>> get_correlation_id()
        'user-service-A1B2C'

        Extend existing correlation ID:
        >>> set_correlation_id("request-456")
        >>> get_correlation_id()
        'request-456-X9Y8Z'

        Handle service request:
        >>> # Extend correlation ID from upstream service
        >>> incoming_corr_id = request.headers.get("X-Correlation-ID")
        >>> set_correlation_id(incoming_corr_id, service_name="my-service")
    """
    if value is None:
        value = default_correlation_id(
            service_name
        )
    else:
        value = add_hop_to_correlation(
            value
        )
    correlation_id.set(value)


def get_trace_id() -> Optional[str]:
    """Get the current trace ID.

    Returns:
        The current trace ID or None if not set.

    Example:
        >>> set_trace_id("trace-789")
        >>> get_trace_id()
        'trace-789'
    """
    return trace_id.get()


def set_trace_id(value: Optional[str] = None):
    """Set the trace ID for the current context.

    If value is None, a new UUID will be generated automatically.

    Args:
        value: The trace ID to set. If None, generates a new UUID.

    Examples:
        Set specific trace ID:
        >>> set_trace_id("custom-trace-123")
        >>> get_trace_id()
        'custom-trace-123'

        Generate new trace ID:
        >>> set_trace_id()
        >>> get_trace_id()
        '550e8400-e29b-41d4-a716-446655440000'
    """
    if value is None:
        value = default_trace_id()
    trace_id.set(value)


def get_span_id() -> Optional[str]:
    """Get the current span ID.

    Returns:
        The current span ID or None if not set.

    Example:
        >>> set_span_id("span-456")
        >>> get_span_id()
        'span-456'
    """
    return span_id.get()


def set_span_id(value: Optional[str] = None):
    """Set the span ID for the current context.

    If value is None, a new UUID will be generated automatically.

    Args:
        value: The span ID to set. If None, generates a new UUID.

    Examples:
        Set specific span ID:
        >>> set_span_id("database-query-span")
        >>> get_span_id()
        'database-query-span'

        Generate new span ID:
        >>> set_span_id()
        >>> get_span_id()
        '6ba7b810-9dad-11d1-80b4-00c04fd430c8'
    """
    if value is None:
        value = default_span_id()
    span_id.set(value)


def set_context(
    correlation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    service_name: Optional[str] = None,
    **kwargs
):
    """Set multiple traceability IDs and custom variables in one call.

    This is a convenience function that sets correlation_id, trace_id, span_id,
    and any additional custom variables in the current context.

    Args:
        correlation_id: Correlation ID to set (will be extended with hop if provided).
        trace_id: Trace ID to set (generates UUID if None).
        span_id: Span ID to set (generates UUID if None).
        service_name: Service name for correlation ID generation (if correlation_id is None).
        **kwargs: Additional custom variables to store in context.

    Examples:
        Set all IDs explicitly:
        >>> set_context(
        ...     correlation_id="request-123",
        ...     trace_id="trace-456",
        ...     span_id="span-789",
        ...     user_id="user-999"
        ... )

        Let some IDs be auto-generated:
        >>> set_context(
        ...     correlation_id="request-123",
        ...     service_name="auth-service",
        ...     operation="login"
        ... )
        # trace_id and span_id will be auto-generated UUIDs

        Start fresh context:
        >>> set_context(service_name="payment-service")
        # All IDs will be auto-generated
    """
    set_correlation_id(correlation_id, service_name)
    set_trace_id(trace_id)
    set_span_id(span_id)
    other_vars.set(kwargs)


def set_context_from_dict(
    context: dict,
    service_name: Optional[str] = None,
    **kwargs
):
    """Set traceability context from a dictionary (e.g., HTTP headers).

    This is particularly useful for extracting traceability information from
    HTTP request headers or message queue metadata.

    Args:
        context: Dictionary containing traceability IDs. Expected keys:
                - 'correlation_id': Correlation ID to extend
                - 'trace_id': Trace ID to use
                - 'span_id': Span ID to use
        service_name: Service name for new correlation ID generation.
        **kwargs: Additional custom variables to store in context.

    Examples:
        From HTTP request headers:
        >>> headers = {
        ...     'correlation_id': request.headers.get('X-Correlation-ID'),
        ...     'trace_id': request.headers.get('X-Trace-ID'),
        ...     'span_id': request.headers.get('X-Span-ID')
        ... }
        >>> set_context_from_dict(headers, service_name="api-gateway")

        From message queue:
        >>> message_metadata = {
        ...     'correlation_id': message.properties.correlation_id,
        ...     'trace_id': message.properties.trace_id
        ... }
        >>> set_context_from_dict(
        ...     message_metadata,
        ...     service_name="order-processor",
        ...     queue_name="orders",
        ...     message_id=message.id
        ... )

        Empty context (generates new IDs):
        >>> set_context_from_dict({}, service_name="background-job")
    """
    set_context(
        context.get('correlation_id'),
        context.get('trace_id'),
        context.get('span_id'),
        service_name,
        **kwargs
    )


# W3C Trace Context functions

def set_context_from_w3c_headers(
    traceparent: Optional[str] = None,
    tracestate: Optional[str] = None,
    service_name: Optional[str] = None,
    vendor_key: str = "finalsa",
    **kwargs
):
    """Set traceability context from W3C Trace Context headers.

    Args:
        traceparent: W3C traceparent header value (e.g., "00-trace_id-parent_id-flags")
        tracestate: W3C tracestate header value (e.g., "vendor1=value1,vendor2=value2")
        service_name: Service name for new correlation ID generation.
        vendor_key: Key to look for correlation ID in tracestate. Defaults to "finalsa".
        **kwargs: Additional custom variables to store in context.

    Examples:
        >>> # Extract correlation ID from tracestate
        >>> set_context_from_w3c_headers(
        ...     traceparent="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        ...     tracestate="finalsa=user-service-A1B2C,rojo=00f067aa0ba902b7",
        ...     service_name="my-service"
        ... )
        >>> # correlation_id will be "user-service-A1B2C-XXXXX" (extended with hop)

        >>> # Generate new context if no traceparent provided
        >>> set_context_from_w3c_headers(service_name="my-service")
    """
    trace_id_val = None
    span_id_val = None
    vendor_data = {}
    correlation_id_val = None

    if traceparent:
        try:
            parsed = parse_traceparent(traceparent)
            trace_id_val = parsed['trace_id']
            # Use parent_id as the incoming span ID, generate new span for this service
            span_id_val = default_span_id()
        except ValueError:
            # Invalid traceparent, generate new IDs
            trace_id_val = None
            span_id_val = None

    if tracestate:
        try:
            vendor_data = parse_tracestate(tracestate)
            # Extract correlation ID from tracestate if present
            correlation_id_val = vendor_data.get(vendor_key)
        except Exception:
            # Invalid tracestate, ignore
            vendor_data = {}

    # Set the context with extracted or generated values
    set_context(
        correlation_id=correlation_id_val,  # Use extracted correlation ID or generate new
        trace_id=trace_id_val,
        span_id=span_id_val,
        service_name=service_name,
        w3c_vendor_data=vendor_data,
        **kwargs
    )


def get_w3c_traceparent() -> str:
    """Generate W3C traceparent header value from current context.

    Returns:
        traceparent header value in format "00-trace_id-parent_id-01"

    Examples:
        >>> set_context(trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
        ...              span_id="00f067aa0ba902b7")
        >>> get_w3c_traceparent()
        '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01'
    """
    current_trace_id = get_trace_id()
    current_span_id = get_span_id()

    return generate_traceparent(
        trace_id=current_trace_id,
        parent_id=current_span_id,
        trace_flags="01"  # Always set sampled flag
    )


def get_w3c_tracestate(vendor_key: Optional[str] = "finalsa") -> str:
    """Generate W3C tracestate header value from current context.

    Args:
        vendor_key: Optional vendor key to include correlation_id in tracestate

    Returns:
        tracestate header value in format "key1=value1,key2=value2"

    Examples:
        >>> set_context(correlation_id="service-A1B2C", w3c_vendor_data={'rojo': 'value1'})
        >>> get_w3c_tracestate(vendor_key="finalsa")
        'finalsa=service-A1B2C,rojo=value1'
    """
    context = get_context()
    vendor_data = context.get('w3c_vendor_data', {}).copy()

    # Optionally include correlation_id in tracestate
    if vendor_key and context.get('correlation_id'):
        # Sanitize correlation ID to be W3C compliant
        correlation_id = context['correlation_id']
        # Replace invalid characters with dashes (W3C compliant)
        sanitized_correlation_id = ''.join(
            c if (c.isalnum() or c in '_-*/') else '-'
            for c in correlation_id
        )
        vendor_data[vendor_key] = sanitized_correlation_id

    try:
        return generate_tracestate(vendor_data)
    except ValueError as e:
        # If tracestate generation fails, log warning and return empty
        import logging
        logging.warning(f"Failed to generate W3C compliant tracestate: {e}")
        return ""


def get_w3c_headers(vendor_key: Optional[str] = "finalsa") -> Dict[str, str]:
    """Get both W3C headers (traceparent and tracestate) from current context.

    Args:
        vendor_key: Vendor key to use for including correlation_id in tracestate

    Returns:
        Dictionary with 'traceparent' and 'tracestate' keys

    Examples:
        >>> set_context(service_name="my-service")
        >>> headers = get_w3c_headers()
        >>> print(headers['traceparent'])
        '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01'
        >>> print(headers['tracestate'])
        'finalsa=my-service-A1B2C'
    """
    return {
        'traceparent': get_w3c_traceparent(),
        'tracestate': get_w3c_tracestate(vendor_key)
    }
