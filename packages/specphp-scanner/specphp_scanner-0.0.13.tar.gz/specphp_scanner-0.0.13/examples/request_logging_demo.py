#!/usr/bin/env python3
"""Request logging demonstration script."""
from __future__ import annotations

from pathlib import Path

from specphp_scanner.utils.request_logger import RequestLogger


def demo_request_logging():
    """Demonstrate basic request logging functionality."""

    # Create request logger
    log_file = Path('demo_requests.jsonl')
    logger = RequestLogger(log_file)

    print(f"Request logger initialized. Logs will be saved to: {log_file}")

    # Simulate some requests
    headers = {'User-Agent': 'Demo/1.0'}
    cookies = {}

    # Log a GET request
    request_id1 = logger.log_request(
        method='GET',
        url='http://localhost:8000/api/users',
        headers=headers,
        cookies=cookies,
    )
    print(f"Logged GET request with ID: {request_id1}")

    # Log response for the GET request
    logger.log_response(
        request_id=request_id1,
        status_code=200,
        response_headers={'Content-Type': 'application/json'},
        response_body='{"users": []}',
        response_time=0.15,
    )
    print(f"Logged response for request: {request_id1}")

    # Log a POST request
    request_id2 = logger.log_request(
        method='POST',
        url='http://localhost:8000/api/users',
        headers=headers,
        cookies=cookies,
        body={'name': 'John', 'email': 'john@example.com'},
    )
    print(f"Logged POST request with ID: {request_id2}")

    # Log response for the POST request
    logger.log_response(
        request_id=request_id2,
        status_code=201,
        response_headers={'Content-Type': 'application/json'},
        response_body='{"id": 1, "name": "John"}',
        response_time=0.25,
    )
    print(f"Logged response for request: {request_id2}")

    # Log an error
    request_id3 = logger.log_request(
        method='GET',
        url='http://localhost:8000/api/invalid',
        headers=headers,
        cookies=cookies,
    )
    logger.log_error(
        request_id=request_id3,
        error='Connection timeout',
        error_type='timeout_error',
    )
    print(f"Logged error for request: {request_id3}")

    # Save logs to file
    logger.save_logs()
    print(f"Logs saved to {log_file}")

    # Display statistics
    stats = logger.get_stats()
    print('\nStatistics:')
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Total responses: {stats['total_responses']}")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Method distribution: {stats['method_distribution']}")
    print(f"  Status code distribution: {stats['status_code_distribution']}")

    # Show request-response pairs
    pairs = logger.get_all_pairs()
    print('\nRequest-Response Pairs:')
    for pair in pairs:
        print(
            f"  {pair['request_id']}: {pair['request']['method']} {pair['request']['url']}",
        )
        if pair['response']:
            print(
                f"    -> {pair['response']['status_code']} ({pair['response']['response_time']:.3f}s)",
            )
        if pair['error']:
            print(f"    -> ERROR: {pair['error']['error']}")


if __name__ == '__main__':
    demo_request_logging()
