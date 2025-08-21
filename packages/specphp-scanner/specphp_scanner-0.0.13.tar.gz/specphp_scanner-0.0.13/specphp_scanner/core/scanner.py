"""Core scanning functionality for OpenAPI Scanner.

This module provides the main scanning logic for testing API endpoints defined in OpenAPI specifications.
It handles request generation, execution, and result collection.
"""
from __future__ import annotations

import random
import string
import uuid
from datetime import datetime
from typing import Any

import requests
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from specphp_scanner.core.result import ScanResult
from specphp_scanner.utils.param_generator import generate_path_params
from specphp_scanner.utils.request_logger import RequestLogger

logger = structlog.get_logger()

console = Console()


def scan_api(
    host: str,
    port: int,
    headers: dict[str, str],
    cookies: dict[str, str],
    data: dict[str, Any],
    request_logger: RequestLogger,
) -> list[ScanResult]:
    """Scan API endpoints defined in the OpenAPI specification.

    Args:
        host: Target host
        port: Target port
        headers: Request headers to include
        cookies: Cookies to include in requests
        data: OpenAPI specification data
        request_logger: Request logger for tracking requests and responses

    Returns:
        List of ScanResult objects containing scan results
    """
    logger.debug('Starting API scan', host=host, port=port)

    # Get base URL
    base_url = f"http://{host}:{port}"
    logger.debug('Using base URL', base_url=base_url)

    # Get paths from OpenAPI spec
    paths = data.get('paths', {})
    if not paths:
        logger.warning('No paths found in OpenAPI specification')
        return []

    logger.debug('Found paths to scan', count=len(paths))

    results = []

    # Scan each path
    for path, path_item in paths.items():
        logger.debug('Scanning path', path=path)

        # Get operations for this path
        operations = {
            method: details
            for method, details in path_item.items()
            if method in ['get', 'post', 'put', 'delete', 'patch']
        }

        if not operations:
            logger.warning('No operations found for path', path=path)
            continue

        # Scan each operation
        for method, operation in operations.items():
            logger.debug('Scanning operation', method=method.upper())

            # Get operation ID or use path + method as identifier
            operation_id = operation.get('operationId', f"{path}_{method}")
            logger.debug('Operation ID', operation_id=operation_id)

            # Get request parameters (both path-level and operation-level)
            path_level_params = path_item.get('parameters', [])
            operation_level_params = operation.get('parameters', [])

            # Combine all parameters, operation-level takes precedence
            all_parameters = path_level_params + operation_level_params

            # Extract path parameters
            path_params = [
                param for param in all_parameters
                if param.get('in') == 'path'
            ]

            # Debug logging for path parameters
            if path_params:
                logger.debug(
                    'Found path parameters',
                    params=[
                        {
                            'name': p.get('name'),
                            'type': p.get('schema', {}).get('type'),
                        }
                        for p in path_params
                    ],
                )
            else:
                logger.debug('No path parameters found')

            # Generate path parameter values if parameters exist
            if path_params:
                logger.debug('Generating path parameter values')
                param_values = generate_path_params(path_params)
                logger.debug('Generated parameter values', values=param_values)
                request_path = path.format(**param_values)
                logger.debug(
                    'Path after parameter replacement',
                    original=path,
                    replaced=request_path,
                )
            else:
                request_path = path
                param_values = None
                logger.debug('No path parameters found', path=path)

            # Build request URL
            url = f"{base_url}{request_path}"
            logger.debug('Request URL', url=url)

            # Get request body if present
            request_body = None
            if 'requestBody' in operation:
                content = operation['requestBody'].get('content', {})
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    request_body = generate_request_body(schema)
                    logger.debug('Request body', body=request_body)

            # Make the request
            try:
                # Log the request (logger is always provided)
                request_id = request_logger.log_request(
                    method=method,
                    url=url,
                    headers=headers.copy(),  # Copy to avoid modifying original
                    cookies=cookies,
                    body=request_body,
                    path_params=param_values,
                )

                logger.debug('Making request', method=method.upper(), url=url)
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    cookies=cookies,
                    json=request_body,
                    timeout=30,
                )

                # Log response
                request_logger.log_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    response_headers=dict(response.headers),
                    response_body=response.text,
                    response_time=response.elapsed.total_seconds(),
                )

                # Log response
                logger.debug(
                    'Response received',
                    status_code=response.status_code,
                    response_time=response.elapsed.total_seconds(),
                )

                # Add result to list
                results.append(
                    ScanResult(
                        method=method,
                        url=url,
                        status_code=response.status_code,
                        response=response.text,
                        response_time=response.elapsed.total_seconds(),
                    ),
                )

                # Display result
                display_result(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    response=response,
                    response_time=response.elapsed.total_seconds(),
                )

            except requests.RequestException as e:
                logger.error(
                    'Request failed', method=method,
                    url=url, error=str(e),
                )

                # Log error
                request_logger.log_error(
                    request_id=request_id,
                    error=str(e),
                    error_type='request_error',
                )

                results.append(
                    ScanResult(
                        method=method,
                        url=url,
                        status_code=None,
                        error=str(e),
                    ),
                )

                # Display error
                display_error(method=method, url=url, error=str(e))

    # Save logs
    request_logger.save_logs()

    return results


def generate_request_body(schema: dict[str, Any] | None) -> Any:
    """Generate a request body based on the schema.

    Args:
        schema: OpenAPI schema for the request body (with resolved $ref)

    Returns:
        Generated request body value (dict, list, str, int, float, or bool)
    """
    if not schema:
        return {}

    schema_type = schema.get('type')
    logger.debug(
        'Generating request body from schema',
        schema_type=schema_type,
    )

    if schema_type == 'object':
        return _generate_object_body(schema)
    elif schema_type == 'array':
        return _generate_array_body(schema)
    elif schema_type == 'string':
        return _generate_string_value(schema)
    elif schema_type == 'integer':
        return _generate_integer_value(schema)
    elif schema_type == 'number':
        return _generate_number_value(schema)
    elif schema_type == 'boolean':
        return _generate_boolean_value()
    else:
        logger.warning(
            f'Unsupported schema type: {schema_type}, returning empty object',
        )
        return {}


def _generate_object_body(schema: dict[str, Any]) -> dict[str, Any]:
    """Generate request body for object type schema."""
    properties = schema.get('properties', {})
    required = schema.get('required', [])

    body = {}

    # Always include required fields
    for field_name in required:
        if field_name in properties:
            body[field_name] = _generate_value_from_schema(
                properties[field_name],
            )

    # Randomly include optional fields
    for prop_name, prop_schema in properties.items():
        if prop_name not in required and random.choice([True, False]):
            body[prop_name] = _generate_value_from_schema(prop_schema)

    return body


def _generate_array_body(schema: dict[str, Any]) -> list[Any]:
    """Generate request body for array type schema."""
    items_schema = schema.get('items', {})
    min_items = schema.get('minItems', 1)
    max_items = schema.get('maxItems', 3)

    count = random.randint(min_items, max_items)
    return [_generate_value_from_schema(items_schema) for _ in range(count)]


def _generate_value_from_schema(schema: dict[str, Any]) -> Any:
    """Generate a value based on schema."""
    schema_type = schema.get('type')

    if schema_type == 'string':
        return _generate_string_value(schema)
    elif schema_type == 'integer':
        return _generate_integer_value(schema)
    elif schema_type == 'number':
        return _generate_number_value(schema)
    elif schema_type == 'boolean':
        return _generate_boolean_value()
    elif schema_type == 'object':
        return _generate_object_body(schema)
    elif schema_type == 'array':
        return _generate_array_body(schema)
    else:
        return 'test_value'


def _generate_string_value(schema: dict[str, Any]) -> str:
    """Generate string value based on schema constraints."""
    if 'enum' in schema:
        return random.choice(schema['enum'])

    format_type = schema.get('format')
    if format_type == 'email':
        return 'test@example.com'
    elif format_type == 'password':
        return 'testpassword123'
    elif format_type == 'uuid':
        return str(uuid.uuid4())
    elif format_type == 'date-time':
        return datetime.now().isoformat()

    min_length = schema.get('minLength', 1)
    max_length = schema.get('maxLength', 10)
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def _generate_integer_value(schema: dict[str, Any]) -> int:
    """Generate integer value based on schema constraints."""
    minimum = schema.get('minimum', 0)
    maximum = schema.get('maximum', 100)
    return random.randint(minimum, maximum)


def _generate_number_value(schema: dict[str, Any]) -> float:
    """Generate number value based on schema constraints."""
    minimum = schema.get('minimum', 0.0)
    maximum = schema.get('maximum', 100.0)
    return round(random.uniform(minimum, maximum), 2)


def _generate_boolean_value() -> bool:
    """Generate random boolean value."""
    return random.choice([True, False])


def display_result(
    method: str,
    url: str,
    status_code: int,
    response: requests.Response,
    response_time: float,
) -> None:
    """Display the result of an API request.

    Args:
        method: HTTP method used
        url: Request URL
        status_code: Response status code
        response: Response object
        response_time: Response time in seconds
    """
    # Create status color based on status code
    if 200 <= status_code < 300:
        status_color = 'green'
    elif 300 <= status_code < 400:
        status_color = 'yellow'
    else:
        status_color = 'red'

    # Create method color
    method_colors = {
        'get': 'blue',
        'post': 'green',
        'put': 'yellow',
        'delete': 'red',
        'patch': 'magenta',
    }
    method_color = method_colors.get(method.lower(), 'white')

    # Create result table
    table = Table(show_header=False, box=None)
    table.add_row(
        Text(method.upper(), style=method_color),
        Text(f"{status_code}", style=status_color),
        Text(f"{response_time:.3f}s", style='cyan'),
        Text(url),
    )

    # Create result panel
    result = Panel(
        table,
        title='API Scan Result',
        border_style=status_color,
    )

    console.print(result)


def display_error(method: str, url: str, error: str) -> None:
    """Display an error that occurred during an API request.

    Args:
        method: HTTP method used
        url: Request URL
        error: Error message
    """
    # Create method color
    method_colors = {
        'get': 'blue',
        'post': 'green',
        'put': 'yellow',
        'delete': 'red',
        'patch': 'magenta',
    }
    method_color = method_colors.get(method.lower(), 'white')

    # Create error table
    table = Table(show_header=False, box=None)
    table.add_row(
        Text(method.upper(), style=method_color),
        Text('ERROR', style='red'),
        Text(url),
    )

    # Create error panel
    result = Panel(
        table,
        title='API Scan Error',
        border_style='red',
    )

    console.print(result)
