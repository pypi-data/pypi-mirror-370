"""
Finalsa Traceability Library

A comprehensive Python library for managing distributed tracing and correlation IDs
across microservices and distributed systems. Provides thread-safe context management
using Python's contextvars for proper isolation between concurrent operations.

Main Components:
    - Context Management: Thread-safe storage and retrieval of traceability IDs
    - ID Generation: Functions for creating correlation IDs, trace IDs, and span IDs
    - HTTP Integration: Constants for standard HTTP headers
    - Async Support: Context variable keys for async operations

Quick Start:
    from finalsa.traceability import set_context, get_context

    # Set traceability context
    set_context(
        correlation_id="user-request-123",
        service_name="auth-service"
    )

    # Get current context
    context = get_context()
    print(context["correlation_id"])  # "user-request-123-XXXXX"

HTTP Integration:
    from finalsa.traceability import (
        set_context_from_dict,
        HTTP_HEADER_CORRELATION_ID
    )

    # Extract from HTTP headers
    headers = {
        'correlation_id': request.headers.get(HTTP_HEADER_CORRELATION_ID),
        'trace_id': request.headers.get('X-Trace-ID'),
        'span_id': request.headers.get('X-Span-ID')
    }
    set_context_from_dict(headers, service_name="api-gateway")
"""

from finalsa.traceability.context import (
    correlation_id,
    get_context,
    get_correlation_id,
    get_span_id,
    get_trace_id,
    get_w3c_headers,
    get_w3c_traceparent,
    get_w3c_tracestate,
    set_context,
    set_context_from_dict,
    set_context_from_w3c_headers,
    set_correlation_id,
    set_span_id,
    set_trace_id,
    span_id,
    trace_id,
)
from finalsa.traceability.functions import (
    ASYNC_CONTEXT_CORRELATION_ID,
    ASYNC_CONTEXT_SPAN_ID,
    ASYNC_CONTEXT_TRACE_ID,
    HTTP_HEADER_CORRELATION_ID,
    HTTP_HEADER_SPAN_ID,
    HTTP_HEADER_TRACE_ID,
    HTTP_HEADER_TRACEPARENT,
    HTTP_HEADER_TRACESTATE,
    default_correlation_id,
    default_span_id,
    default_trace_id,
    generate_traceparent,
    generate_tracestate,
    id_generator,
    parse_traceparent,
    parse_tracestate,
)

__all__ = [
    "correlation_id",
    "trace_id",
    "span_id",
    "id_generator",
    "default_correlation_id",
    "default_span_id",
    "default_trace_id",
    "set_span_id",
    "set_trace_id",
    "set_correlation_id",
    "set_context",
    "set_context_from_dict",
    "get_context",
    "get_w3c_traceparent",
    "get_w3c_tracestate",
    "get_correlation_id",
    "get_trace_id",
    "get_span_id",
    "get_w3c_headers",
    "set_context_from_w3c_headers",
    "HTTP_HEADER_CORRELATION_ID",
    "HTTP_HEADER_SPAN_ID",
    "HTTP_HEADER_TRACE_ID",
    "HTTP_HEADER_TRACEPARENT",
    "HTTP_HEADER_TRACESTATE",
    "generate_traceparent",
    "parse_traceparent",
    "generate_tracestate",
    "parse_tracestate",
    "ASYNC_CONTEXT_CORRELATION_ID",
    "ASYNC_CONTEXT_SPAN_ID",
    "ASYNC_CONTEXT_TRACE_ID"
]
