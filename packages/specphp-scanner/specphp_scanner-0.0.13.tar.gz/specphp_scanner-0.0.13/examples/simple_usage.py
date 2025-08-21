#!/usr/bin/env python3
"""Simple usage example for SpecPHP Scanner with request logging."""
from __future__ import annotations


def simple_example():
    """Demonstrate the new request logging functionality."""

    print('=== SpecPHP Scanner Request Logging Demo ===\n')

    print('1. Default behavior (console output only):')
    print('   python -m specphp_scanner spec.yaml --host localhost --port 8000')
    print('   -> All request logs will be output to stderr in JSON format\n')

    print('2. With file output (optional):')
    print('   python -m specphp_scanner spec.yaml --host localhost --port 8000 --request-log-file logs.jsonl')
    print('   -> Logs will be output to both stderr and the specified file\n')

    print('3. Disable request logging:')
    print('   python -m specphp_scanner spec.yaml --host localhost --port 8000 --disable-request-logging')
    print('   -> No request logs will be output\n')

    print('4. Example log output to stderr:')
    print('   Each request/response will be logged as JSON to stderr:')
    print('   {')
    print('     "request_id": "550e8400-e29b-41d4-a716-446655440000",')
    print('     "timestamp": "2024-01-15T10:30:45.123456",')
    print('     "type": "request",')
    print('     "request": {')
    print('       "method": "POST",')
    print('       "url": "http://localhost:8000/api/users",')
    print('       "headers": {...},')
    print('       "cookies": {...},')
    print('       "body": {...},')
    print('       "path_params": null')
    print('     }')
    print('   }\n')

    print('5. Benefits of the new approach:')
    print('   - Request logs are always visible in real-time')
    print('   - Easy to pipe logs to other tools (grep, jq, etc.)')
    print('   - Optional file output for persistence')
    print('   - Clean separation between user output and log data')
    print('   - JSON format for easy parsing and analysis\n')

    print('6. Usage in scripts:')
    print('   # Capture logs to file while still seeing them in terminal')
    print('   python -m specphp_scanner spec.yaml --host localhost --port 8000 --request-log-file logs.jsonl 2> logs.jsonl')
    print('   # Or redirect stderr to a file')
    print('   python -m specphp_scanner spec.yaml --host localhost --port 8000 2> request_logs.jsonl')


if __name__ == '__main__':
    simple_example()
