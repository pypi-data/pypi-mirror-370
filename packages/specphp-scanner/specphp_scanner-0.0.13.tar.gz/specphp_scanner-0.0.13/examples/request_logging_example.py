#!/usr/bin/env python3
"""Example script demonstrating request logging functionality.

This script shows how to use the request logging feature to track all HTTP requests
and responses with unique UUIDs and save them to JSONL files.
"""
from __future__ import annotations

import json
from pathlib import Path

from specphp_scanner.core.scanner import scan_api
from specphp_scanner.utils.request_logger import RequestLogger


def main():
    """Demonstrate request logging functionality."""

    # Example OpenAPI specification data
    openapi_spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Example API',
            'version': '1.0.0',
        },
        'paths': {
            '/api/users': {
                'get': {
                    'summary': 'Get users',
                    'responses': {
                        '200': {
                            'description': 'Success',
                        },
                    },
                },
                'post': {
                    'summary': 'Create user',
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'},
                                        'email': {'type': 'string'},
                                    },
                                },
                            },
                        },
                    },
                    'responses': {
                        '201': {
                            'description': 'Created',
                        },
                    },
                },
            },
            '/api/users/{id}': {
                'get': {
                    'summary': 'Get user by ID',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'string'},
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'Success',
                        },
                    },
                },
            },
        },
    }

    # Initialize request logger
    log_file = Path('example_requests.jsonl')
    request_logger = RequestLogger(log_file=log_file)

    print(f"Request logging enabled. Logs will be saved to: {log_file}")

    # Example headers and cookies
    headers = {
        'User-Agent': 'SpecPHP-Scanner/1.0',
        'Accept': 'application/json',
    }
    cookies = {}

    # Run the scanner with request logging
    try:
        results = scan_api(
            host='localhost',
            port=8000,
            headers=headers,
            cookies=cookies,
            data=openapi_spec,
            replace_params=True,
            request_logger=request_logger,
        )

        print(f"\nScan completed. Found {len(results)} endpoints.")

        # Display request logging statistics
        stats = request_logger.get_stats()
        print('\nRequest Logging Statistics:')
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Total responses: {stats['total_responses']}")
        print(f"  Total errors: {stats['total_errors']}")
        print(f"  Log file: {stats['log_file']}")

        if stats['method_distribution']:
            print(f"  Method distribution: {stats['method_distribution']}")
        if stats['status_code_distribution']:
            print(
                f"  Status code distribution: {stats['status_code_distribution']}",
            )

        # Display some sample log entries
        print('\nSample log entries:')
        all_pairs = request_logger.get_all_pairs()
        for i, pair in enumerate(all_pairs[:3]):  # Show first 3 pairs
            print(f"\nRequest-Response Pair {i + 1}:")
            print(f"  Request ID: {pair['request_id']}")
            print(f"  Method: {pair['request']['method']}")
            print(f"  URL: {pair['request']['url']}")
            if pair['response']:
                print(f"  Status: {pair['response']['status_code']}")
                print(
                    f"  Response Time: {pair['response']['response_time']:.3f}s",
                )
            if pair['error']:
                print(f"  Error: {pair['error']['error']}")

        # Show the JSONL file contents
        print('\nJSONL file contents:')
        if log_file.exists():
            with open(log_file, encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        data = json.loads(line)
                        print(
                            f"  Line {line_num}: {data['type']} - {data.get('method', 'N/A')} {data.get('url', 'N/A')}",
                        )
        else:
            print('  Log file not created (no actual requests were made)')

    except Exception as e:
        print(f"Error during scanning: {e}")

    print('\nRequest logging demonstration completed.')
    print(
        f"Check the log file '{log_file}' for detailed request/response data.",
    )


if __name__ == '__main__':
    main()
