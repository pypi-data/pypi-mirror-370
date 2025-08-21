#!/usr/bin/env python3
"""Demonstration of the new dataclass-based request logging system."""
from __future__ import annotations

from pathlib import Path

import structlog

from specphp_scanner.utils.request_logger import RequestLogger


def demo_dataclass_logging():
    """Demonstrate the new dataclass-based logging system."""
    logger = structlog.get_logger()

    # Create request logger
    log_file = Path('dataclass_demo.jsonl')
    request_logger = RequestLogger(log_file)

    logger.info('Dataclass-based request logger initialized')
    logger.info('Logs will be saved', log_file=str(log_file))

    # Simulate some API requests
    headers = {
        'User-Agent': 'DataclassDemo/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    cookies = {'session_id': 'demo_session_123'}

    logger.info('=== Logging GET Request ===')
    # Log a GET request
    request_id1 = request_logger.log_request(
        method='GET',
        url='http://localhost:8000/api/users',
        headers=headers,
        cookies=cookies,
    )
    logger.info('Logged GET request', request_id=request_id1)

    # Log response for the GET request
    request_logger.log_response(
        request_id=request_id1,
        status_code=200,
        response_headers={
            'Content-Type': 'application/json', 'X-Total-Count': '5',
        },
        response_body='{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}',
        response_time=0.125,
    )
    logger.info('Logged response for request', request_id=request_id1)

    logger.info('=== Logging POST Request ===')
    # Log a POST request
    request_id2 = request_logger.log_request(
        method='POST',
        url='http://localhost:8000/api/users',
        headers=headers,
        cookies=cookies,
        body={'name': 'Charlie', 'email': 'charlie@example.com', 'role': 'admin'},
    )
    logger.info('Logged POST request', request_id=request_id2)

    # Log response for the POST request
    request_logger.log_response(
        request_id=request_id2,
        status_code=201,
        response_headers={
            'Content-Type': 'application/json',
            'Location': '/api/users/3',
        },
        response_body='{"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "admin"}',
        response_time=0.234,
    )
    logger.info('Logged response for request', request_id=request_id2)

    logger.info('=== Logging Request with Path Parameters ===')
    # Log a request with path parameters
    request_id3 = request_logger.log_request(
        method='GET',
        url='http://localhost:8000/api/users/1',
        headers=headers,
        cookies=cookies,
        path_params={'id': '1'},
    )
    logger.info('Logged GET request with path params', request_id=request_id3)

    # Log response for the path parameter request
    request_logger.log_response(
        request_id=request_id3,
        status_code=200,
        response_headers={'Content-Type': 'application/json'},
        response_body='{"id": 1, "name": "Alice", "email": "alice@example.com"}',
        response_time=0.089,
    )
    logger.info('Logged response for request', request_id=request_id3)

    logger.info('=== Logging Error ===')
    # Log an error
    request_id4 = request_logger.log_request(
        method='DELETE',
        url='http://localhost:8000/api/users/999',
        headers=headers,
        cookies=cookies,
    )
    request_logger.log_error(
        request_id=request_id4,
        error='User not found: 999',
        error_type='not_found_error',
    )
    logger.info('Logged error for request', request_id=request_id4)

    # Save logs to file
    request_logger.save_logs()
    logger.info('Logs saved', log_file=str(log_file))

    # Display statistics
    stats = request_logger.get_stats()
    logger.info('=== Statistics ===')
    logger.info('Statistics', stats=stats)

    # Show request-response pairs
    logger.info('=== Request-Response Pairs ===')
    pairs = request_logger.get_all_pairs()
    for i, pair in enumerate(pairs, 1):
        logger.info(
            f"Pair {i}",
            pair_number=i,
            request_id=pair.request_id,
            method=pair.request.request.method,
            url=pair.request.request.url,
            timestamp=pair.request.timestamp,
        )

        if pair.request.request.path_params:
            logger.info(
                'Path parameters',
                path_params=pair.request.request.path_params,
            )

        if pair.request.request.body:
            logger.info('Request body', body=pair.request.request.body)

        if pair.response:
            logger.info(
                'Response',
                status_code=pair.response.response.status_code,
                response_time=pair.response.response.response_time,
                headers=pair.response.response.headers,
                body_preview=pair.response.response.body[:100],
            )

        if pair.error:
            logger.info(
                'Error',
                error=pair.error.error.error,
                error_type=pair.error.error.error_type,
            )

    # Demonstrate accessing specific log entries
    logger.info('=== Individual Log Entries ===')
    for entry in request_logger.log_entries:
        logger.info(
            'Log entry',
            entry_type=entry.__class__.__name__,
            request_id=entry.request_id,
            timestamp=entry.timestamp,
        )

        if hasattr(entry, 'request'):
            logger.info(
                'Request entry',
                method=entry.request.method,
                url=entry.request.url,
            )
        elif hasattr(entry, 'response'):
            logger.info(
                'Response entry',
                status_code=entry.response.status_code,
            )
        elif hasattr(entry, 'error'):
            logger.info('Error entry', error_type=entry.error.error_type)


if __name__ == '__main__':
    demo_dataclass_logging()
