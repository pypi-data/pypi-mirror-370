#!/usr/bin/env python3
"""Example usage of the new ScanResult class.

This example demonstrates how to use the updated scanner that returns
ScanResult objects instead of dictionaries.
"""
from __future__ import annotations

from specphp_scanner.core.result import ScanSummary
from specphp_scanner.core.scanner import scan_api


def main():
    """Example of using the scanner with ScanResult objects."""

    # Example OpenAPI specification data
    spec_data = {
        'paths': {
            '/api/users': {
                'get': {
                    'operationId': 'getUsers',
                    'responses': {
                        '200': {
                            'description': 'List of users',
                        },
                    },
                },
            },
            '/api/users/{id}': {
                'get': {
                    'operationId': 'getUser',
                    'parameters': [
                        {
                            'name': 'id',
                            'in': 'path',
                            'required': True,
                            'schema': {
                                'type': 'integer',
                            },
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'User details',
                        },
                    },
                },
            },
        },
    }

    # Run the scanner
    results = scan_api(
        host='localhost',
        port=8000,
        headers={'Content-Type': 'application/json'},
        cookies={},
        data=spec_data,
    )

    # Now results is a list of ScanResult objects instead of dictionaries
    print(f"Scan completed. Found {len(results)} endpoints.")

    # Access ScanResult attributes directly
    for result in results:
        print(f"\nMethod: {result.method}")
        print(f"URL: {result.url}")
        print(f"Status Code: {result.status_code}")
        print(f"Response Time: {result.response_time:.3f}s")

        # Use the convenience properties
        if result.is_success:
            print('✅ Request was successful')
        elif result.is_error:
            print('❌ Request failed')

        if result.error:
            print(f"Error: {result.error}")

        # Convert to dictionary if needed
        result_dict = result.to_dict()
        print(f"Timestamp: {result_dict['timestamp']}")

    # Create a summary
    summary = ScanSummary.from_results(results)
    print('\n📊 Scan Summary:')
    print(f"Total Requests: {summary.total_requests}")
    print(f"Successful: {summary.successful_requests}")
    print(f"Failed: {summary.failed_requests}")
    print(f"Errors: {summary.error_requests}")
    print(f"Average Response Time: {summary.average_response_time:.3f}s")


if __name__ == '__main__':
    main()
