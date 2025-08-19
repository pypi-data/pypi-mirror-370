"""
Utility functions for generating and manipulating traceability IDs.

This module provides functions for generating correlation IDs, trace IDs, span IDs,
and for adding hops to correlation IDs as they flow through different services.

Constants:
    HTTP_HEADER_*: Standard HTTP header names for traceability IDs
    ASYNC_CONTEXT_*: Keys for storing traceability data in async contexts

Example:
    Basic ID generation:
        from finalsa.traceability.functions import (
            default_correlation_id,
            default_trace_id,
            add_hop_to_correlation
        )

        # Generate new correlation ID
        corr_id = default_correlation_id("user-service")
        print(corr_id)  # "user-service-A1B2C"

        # Add hop to existing correlation ID
        extended = add_hop_to_correlation(corr_id)
        print(extended)  # "user-service-A1B2C-X9Y8Z"

        # Generate trace ID
        trace = default_trace_id()
        print(trace)  # "550e8400-e29b-41d4-a716-446655440000"
"""

import random
import string
from typing import Optional

# W3C Trace Context standard headers
HTTP_HEADER_TRACEPARENT = "traceparent"
"""W3C Trace Context standard header for trace context propagation.

Format: version-trace_id-parent_id-trace_flags
Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
"""

HTTP_HEADER_TRACESTATE = "tracestate"
"""W3C Trace Context standard header for vendor-specific trace state.

Format: key1=value1,key2=value2
Example: rojo=00f067aa0ba902b7,congo=t61rcWkgMzE
"""

# Traditional HTTP Header constants (still fully supported)
HTTP_HEADER_CORRELATION_ID = "X-Correlation-ID"
"""Traditional HTTP header name for correlation ID.

Use this constant when setting/getting correlation IDs from HTTP headers
to ensure consistency across your application.
This header is still fully supported and works alongside W3C headers.
"""

HTTP_HEADER_TRACE_ID = "X-Trace-ID"
"""Traditional HTTP header name for trace ID.

Use this constant when setting/getting trace IDs from HTTP headers
to ensure consistency across your application.
This header is still fully supported and works alongside W3C headers.
"""

HTTP_HEADER_SPAN_ID = "X-Span-ID"
"""Traditional HTTP header name for span ID.

Use this constant when setting/getting span IDs from HTTP headers
to ensure consistency across your application.
This header is still fully supported and works alongside W3C headers.
"""

HTTP_AUTHORIZATION_HEADER = "Authorization"
"""Standard HTTP authorization header name.

Included for convenience when working with authenticated requests
that also need traceability.
"""

# Async context variable keys
ASYNC_CONTEXT_CORRELATION_ID = "correlation_id"
"""Key name for correlation ID in async context storage."""

ASYNC_CONTEXT_TRACE_ID = "trace_id"
"""Key name for trace ID in async context storage."""

ASYNC_CONTEXT_SPAN_ID = "span_id"
"""Key name for span ID in async context storage."""

ASYNC_CONTEXT_TOPIC = "topic"
"""Key name for topic information in async context storage.

Useful for message queue or pub/sub systems where you need to track
which topic/channel a message came from.
"""

ASYNC_CONTEXT_SUBTOPIC = "subtopic"
"""Key name for subtopic information in async context storage.

Useful for more granular topic tracking in message systems.
"""

ASYNC_CONTEXT_AUTHORIZATION = "auth"
"""Key name for authorization information in async context storage.

Use this for storing auth tokens or user context that should flow
with traceability information.
"""


def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    """Generate a random alphanumeric ID string.

    Creates a random string using the specified character set. By default,
    uses uppercase letters and digits.

    Args:
        size: Length of the generated ID. Defaults to 5.
        chars: Character set to use for generation. Defaults to uppercase letters + digits.

    Returns:
        Random string of specified length.

    Raises:
        IndexError: If chars is empty.
        TypeError: If chars is not a string.

    Examples:
        >>> id_generator()
        'A1B2C'

        >>> id_generator(10)
        'X9Y8Z7W6V5'

        >>> id_generator(3, 'ABC')
        'BAC'

    Note:
        This function uses Python's random module, which is not cryptographically
        secure. For security-sensitive applications, consider using the secrets module.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def default_correlation_id(
    service_name: Optional[str] = None
) -> str:
    """Generate a default correlation ID with service name prefix.

    Creates a correlation ID in the format: "{service_name}-{random_id}"

    Args:
        service_name: Name of the service generating the ID. If None, uses "DEFAULT".

    Returns:
        Correlation ID string in format "service_name-XXXXX".

    Examples:
        >>> default_correlation_id("user-service")
        'user-service-A1B2C'

        >>> default_correlation_id()
        'DEFAULT-X9Y8Z'

        >>> default_correlation_id("")
        '-M4N5P'

    Note:
        This function is typically used when starting a new request trace
        or when no correlation ID is provided by upstream services.
    """
    if service_name is None:
        service_name = "DEFAULT"
    return f"{service_name}-{id_generator()}"


def default_span_id() -> str:
    """Generate a W3C Trace Context-compliant span ID (16 hex chars, lowercase, no dashes).

    Returns:
        Span ID string in format "0123456789abcdef" (16 lowercase hex chars).

    Examples:
        >>> default_span_id()
        '4bf92f3577b34da6'

    Note:
        Each call generates a unique ID. Span IDs should be unique within
        a trace and are used to identify individual operations.
    """
    # 8 bytes = 16 hex chars
    return ''.join(random.choices('0123456789abcdef', k=16))


def default_trace_id() -> str:
    """Generate a W3C Trace Context-compliant trace ID (32 hex chars, lowercase, no dashes).

    Returns:
        Trace ID string in format "0123456789abcdef0123456789abcdef" (32 lowercase hex chars).

    Examples:
        >>> default_trace_id()
        '4bf92f3577b34da6a3ce929d0e0e4736'

    Note:
        Each call generates a unique ID. Trace IDs should be unique across
        your entire system and represent the top-level request or operation.
    """
    # 16 bytes = 32 hex chars
    while True:
        trace_id = ''.join(random.choices('0123456789abcdef', k=32))
        if trace_id != '0' * 32:
            return trace_id


def add_hop_to_correlation(
    correlation_id: str,
) -> str:
    """Add a hop to an existing correlation ID.

    Extends a correlation ID by appending a new random segment, creating
    a trail of hops as the request flows through different services.

    Args:
        correlation_id: The existing correlation ID to extend.

    Returns:
        Extended correlation ID in format "original_id-XXXXX".

    Raises:
        AttributeError: If correlation_id is empty or falsy.

    Examples:
        >>> add_hop_to_correlation("user-service-A1B2C")
        'user-service-A1B2C-X9Y8Z'

        >>> add_hop_to_correlation("request-123")
        'request-123-M4N5P'

        Chain multiple hops:
        >>> original = "service-A1B2C"
        >>> hop1 = add_hop_to_correlation(original)
        >>> hop2 = add_hop_to_correlation(hop1)
        >>> print(hop2)
        'service-A1B2C-X9Y8Z-Q7R8S'

    Note:
        This function is crucial for distributed tracing. Each service should
        add its own hop when processing a request, creating a traceable path
        through your service architecture.
    """
    if not correlation_id:
        raise AttributeError("Correlation ID cannot be empty")
    hop = id_generator()
    return f"{correlation_id}-{hop}"


# W3C Trace Context functions

def generate_traceparent(
    trace_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    trace_flags: str = "01"
) -> str:
    """Generate a W3C Trace Context compliant traceparent header value.

    Args:
        trace_id: 32 lowercase hex chars. If None, generates a new one.
        parent_id: 16 lowercase hex chars. If None, generates a new one.
        trace_flags: 2 hex chars representing trace flags. Defaults to "01" (sampled).

    Returns:
        traceparent header value in format: "00-{trace_id}-{parent_id}-{trace_flags}"

    Examples:
        >>> generate_traceparent()
        '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01'

        >>> generate_traceparent("abc123...", "def456...")
        '00-abc123...-def456...-01'
    """
    if trace_id is None:
        trace_id = default_trace_id()
    if parent_id is None:
        parent_id = default_span_id()

    return f"00-{trace_id}-{parent_id}-{trace_flags}"


def parse_traceparent(traceparent: str) -> dict:
    """Parse a W3C Trace Context traceparent header value.

    Args:
        traceparent: traceparent header value in format "version-trace_id-parent_id-trace_flags"

    Returns:
        Dictionary with keys: version, trace_id, parent_id, trace_flags

    Raises:
        ValueError: If traceparent format is invalid.

    Examples:
        >>> parse_traceparent("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
        {
            'version': '00',
            'trace_id': '4bf92f3577b34da6a3ce929d0e0e4736',
            'parent_id': '00f067aa0ba902b7',
            'trace_flags': '01'
        }
    """
    parts = traceparent.split('-')
    if len(parts) != 4:
        raise ValueError(f"Invalid traceparent format: {traceparent}")

    version, trace_id, parent_id, trace_flags = parts

    # Validate format according to W3C spec
    if len(version) != 2 or not all(c in '0123456789abcdef' for c in version):
        raise ValueError(f"Invalid version format: {version}")
    if len(trace_id) != 32 or not all(c in '0123456789abcdef' for c in trace_id):
        raise ValueError(f"Invalid trace_id format: {trace_id}")
    if len(parent_id) != 16 or not all(c in '0123456789abcdef' for c in parent_id):
        raise ValueError(f"Invalid parent_id format: {parent_id}")
    if len(trace_flags) != 2 or not all(c in '0123456789abcdef' for c in trace_flags):
        raise ValueError(f"Invalid trace_flags format: {trace_flags}")

    # Check for invalid trace_id (all zeros)
    if trace_id == '0' * 32:
        raise ValueError("trace_id cannot be all zeros")

    # Check for invalid parent_id (all zeros)
    if parent_id == '0' * 16:
        raise ValueError("parent_id cannot be all zeros")

    return {
        'version': version,
        'trace_id': trace_id,
        'parent_id': parent_id,
        'trace_flags': trace_flags
    }


def generate_tracestate(vendor_data: dict) -> str:
    """Generate a W3C Trace Context compliant tracestate header value.

    According to W3C spec:
    - Keys must start with lowercase letter
    - Keys can contain lowercase letters, digits, underscores, dashes, asterisks, forward slashes
    - Values must be URL-safe and not contain commas or equals signs
    - Maximum 32 key-value pairs
    - Maximum 512 characters total

    Args:
        vendor_data: Dictionary of vendor-specific key-value pairs.

    Returns:
        tracestate header value in format "key1=value1,key2=value2"

    Examples:
        >>> generate_tracestate({'rojo': '00f067aa0ba902b7', 'congo': 't61rcWkgMzE'})
        'rojo=00f067aa0ba902b7,congo=t61rcWkgMzE'

    Raises:
        ValueError: If keys or values don't meet W3C specification requirements.
    """
    if not vendor_data:
        return ""

    # Validate and format key-value pairs
    valid_pairs = []
    for key, value in vendor_data.items():
        # Validate key according to W3C spec
        if not _is_valid_tracestate_key(key):
            raise ValueError(f"Invalid tracestate key '{key}': must start with lowercase letter and contain only lowercase letters, digits, underscores, dashes, asterisks, forward slashes")

        # Validate value according to W3C spec
        if not _is_valid_tracestate_value(value):
            raise ValueError(f"Invalid tracestate value '{value}': must not contain commas, equals signs, or non-printable characters")

        valid_pairs.append(f"{key}={value}")

    # Check limits
    if len(valid_pairs) > 32:
        raise ValueError("tracestate cannot contain more than 32 key-value pairs")

    result = ','.join(valid_pairs)
    if len(result) > 512:
        raise ValueError("tracestate cannot exceed 512 characters")

    return result


def _is_valid_tracestate_key(key: str) -> bool:
    """Validate tracestate key according to W3C specification.

    Key must:
    - Start with lowercase letter
    - Contain only lowercase letters, digits, underscores, dashes, asterisks, forward slashes
    - Be between 1 and 256 characters
    """
    if not key or len(key) > 256:
        return False

    # Must start with lowercase letter
    if not key[0].islower() or not key[0].isalpha():
        return False

    # Check allowed characters: lowercase letters, digits, _, -, *, /
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-*/')
    return all(c in allowed_chars for c in key)


def _is_valid_tracestate_value(value: str) -> bool:
    """Validate tracestate value according to W3C specification.

    Value must:
    - Not contain commas or equals signs
    - Be printable ASCII characters
    - Be between 1 and 256 characters
    """
    if not value or len(value) > 256:
        return False

    # Must not contain commas or equals
    if ',' in value or '=' in value:
        return False

    # Must be printable ASCII (32-126)
    return all(32 <= ord(c) <= 126 for c in value)


def parse_tracestate(tracestate: str) -> dict:
    """Parse a W3C Trace Context tracestate header value.

    Parses according to W3C specification with validation:
    - Ignores malformed key-value pairs
    - Validates keys and values according to spec
    - Preserves order (though dict doesn't guarantee order in Python < 3.7)
    - Maximum 32 key-value pairs
    - Maximum 512 characters total

    Args:
        tracestate: tracestate header value in format "key1=value1,key2=value2"
    Returns:
        Dictionary of vendor-specific key-value pairs.
    Examples:
        >>> parse_tracestate("rojo=00f067aa0ba902b7,congo=t61rcWkgMzE")
        {'rojo': '00f067aa0ba902b7', 'congo': 't61rcWkgMzE'}
        >>> parse_tracestate("invalid=value,valid-key=good-value")
        {'valid-key': 'good-value'}  # Invalid entries are skipped
    """
    if not tracestate:
        return {}

    # Check total length limit
    if len(tracestate) > 512:
        # Truncate to 512 characters and continue parsing
        tracestate = tracestate[:512]

    result = {}
    pairs = tracestate.split(',')

    # Limit to 32 key-value pairs
    if len(pairs) > 32:
        pairs = pairs[:32]

    for pair in pairs:
        pair = pair.strip()
        if '=' not in pair:
            continue  # Skip malformed pairs

        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Validate key and value according to W3C spec
        if _is_valid_tracestate_key(key) and _is_valid_tracestate_value(value):
            result[key] = value
        # Silently skip invalid key-value pairs as per W3C recommendation

    return result
