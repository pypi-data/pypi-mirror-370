"""Parameter generation utilities for OpenAPI Scanner.

This module provides functionality for generating values for path parameters
based on their OpenAPI schema definitions.
"""
from __future__ import annotations

import random
import string
import uuid
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def get_param_schema(path: str, param_name: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Get parameter schema from OpenAPI specification."""
    path_item = data['paths'].get(path, {})

    # Check path parameters
    if 'parameters' in path_item:
        for param in path_item['parameters']:
            if param.get('name') == param_name:
                return param.get('schema', {})

    # Check operation parameters
    for method in ['get', 'post', 'put', 'delete', 'patch']:
        if method in path_item:
            operation = path_item[method]
            if 'parameters' in operation:
                for param in operation['parameters']:
                    if param.get('name') == param_name:
                        return param.get('schema', {})

    return None


def generate_path_params(parameters: list[dict[str, Any]]) -> dict[str, str]:
    """Generate values for path parameters based on their schemas.

    Args:
        parameters: List of parameter definitions from OpenAPI spec

    Returns:
        Dictionary mapping parameter names to generated values
    """
    logger.debug(f"Generating values for {len(parameters)} path parameters")

    param_values = {}
    for param in parameters:
        name = param.get('name')
        schema = param.get('schema', {})

        if not name:
            logger.warning('Found parameter without name, skipping')
            continue

        logger.debug(f"Generating value for parameter: {name}")

        # Try to infer type from parameter name
        param_type = infer_param_type(name)

        # Generate value based on inferred type or schema
        if param_type:
            value = generate_value_by_type(param_type)
        else:
            value = generate_value_from_schema(schema)

        param_values[name] = str(value)

    return param_values


def infer_param_type(param_name: str) -> str | None:
    """Infer parameter type from its name.

    Args:
        param_name: Parameter name

    Returns:
        Inferred type or None if type cannot be inferred
    """
    param_name = param_name.lower()

    # Common parameter name patterns
    if any(x in param_name for x in ['id', 'uuid']):
        return 'uuid'
    elif any(x in param_name for x in ['date', 'time']):
        return 'datetime'
    elif any(x in param_name for x in ['count', 'limit', 'page', 'size']):
        return 'integer'
    elif any(x in param_name for x in ['name', 'title', 'description']):
        return 'string'

    return None


def generate_value_by_type(param_type: str) -> Any:
    """Generate a value based on parameter type.

    Args:
        param_type: Parameter type

    Returns:
        Generated value
    """
    if param_type == 'uuid':
        return str(uuid.uuid4())
    elif param_type == 'datetime':
        return datetime.now().isoformat()
    elif param_type == 'integer':
        return random.randint(1, 100)
    elif param_type == 'string':
        return ''.join(random.choices(string.ascii_letters, k=8))
    else:
        return generate_default_value()


def generate_value_from_schema(schema: dict[str, Any]) -> Any:
    """Generate a value based on an OpenAPI schema.

    Args:
        schema: OpenAPI schema definition

    Returns:
        Generated value matching the schema
    """
    schema_type = schema.get('type')
    logger.debug(f"Generating value for schema type: {schema_type}")

    if not schema_type:
        logger.warning('Schema has no type, generating default value')
        return generate_default_value()

    if schema_type == 'string':
        return generate_string_value(schema)
    elif schema_type == 'integer':
        return generate_integer_value(schema)
    elif schema_type == 'number':
        return generate_number_value(schema)
    elif schema_type == 'boolean':
        return generate_boolean_value()
    else:
        logger.warning(
            f"Unsupported schema type: {schema_type}, generating default value",
        )
        return generate_default_value()


def generate_string_value(schema: dict[str, Any]) -> str:
    """Generate a string value based on schema constraints.

    Args:
        schema: String schema definition

    Returns:
        Generated string value
    """
    # Check for enum values
    if 'enum' in schema:
        values = schema['enum']
        logger.debug(f"Using enum values: {values}")
        return random.choice(values)

    # Check for format
    format_type = schema.get('format')
    if format_type == 'uuid':
        logger.debug('Generating UUID')
        return str(uuid.uuid4())
    elif format_type == 'date-time':
        logger.debug('Generating datetime')
        return datetime.now().isoformat()

    # Generate random string
    min_length = schema.get('minLength', 1)
    max_length = schema.get('maxLength', 10)
    length = random.randint(min_length, max_length)

    logger.debug(f"Generating random string of length {length}")
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_integer_value(schema: dict[str, Any]) -> int:
    """Generate an integer value based on schema constraints.

    Args:
        schema: Integer schema definition

    Returns:
        Generated integer value
    """
    minimum = schema.get('minimum', 0)
    maximum = schema.get('maximum', 100)

    logger.debug(f"Generating integer between {minimum} and {maximum}")
    return random.randint(minimum, maximum)


def generate_number_value(schema: dict[str, Any]) -> float:
    """Generate a number value based on schema constraints.

    Args:
        schema: Number schema definition

    Returns:
        Generated number value
    """
    minimum = schema.get('minimum', 0.0)
    maximum = schema.get('maximum', 100.0)

    logger.debug(f"Generating number between {minimum} and {maximum}")
    return random.uniform(minimum, maximum)


def generate_boolean_value() -> bool:
    """Generate a random boolean value.

    Returns:
        Random boolean value
    """
    logger.debug('Generating random boolean')
    return random.choice([True, False])


def generate_default_value() -> str:
    """Generate a default value when schema type is unknown.

    Returns:
        Default string value
    """
    logger.debug('Generating default value')
    return 'test'
