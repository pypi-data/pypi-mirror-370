"""Request logging functionality for API scanning operations.

This module provides request logging capabilities, using dataclasses to define
log entry structures for better type safety and clarity.
"""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class RequestInfo:
    """Information about an HTTP request."""

    method: str
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    body: dict[str, Any] | None = None
    path_params: dict[str, Any] | None = None


@dataclass
class ResponseInfo:
    """Information about an HTTP response."""

    status_code: int
    headers: dict[str, str]
    body: str
    response_time: float


@dataclass
class ErrorInfo:
    """Information about an error that occurred."""

    error: str
    error_type: str


@dataclass
class LogEntry:
    """Base class for all log entries."""

    request_id: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert the log entry to a dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class RequestLogEntry(LogEntry):
    """Log entry for an outgoing HTTP request."""

    request: RequestInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert the request log entry to a dictionary."""
        data = super().to_dict()
        data['type'] = 'request'
        return data


@dataclass
class ResponseLogEntry(LogEntry):
    """Log entry for an HTTP response."""

    response: ResponseInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert the response log entry to a dictionary."""
        data = super().to_dict()
        data['type'] = 'response'
        return data


@dataclass
class ErrorLogEntry(LogEntry):
    """Log entry for an error that occurred."""

    error: ErrorInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert the error log entry to a dictionary."""
        data = super().to_dict()
        data['type'] = 'error'
        return data


@dataclass
class RequestResponsePair:
    """Complete request-response pair with all related information."""

    request_id: str
    request: RequestLogEntry
    response: ResponseLogEntry | None = None
    error: ErrorLogEntry | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the pair to a dictionary."""
        return {
            'request_id': self.request_id,
            'request': self.request.to_dict(),
            'response': self.response.to_dict() if self.response else None,
            'error': self.error.to_dict() if self.error else None,
        }


class RequestLogger:
    """Logs HTTP requests and responses with unique identifiers using dataclasses."""

    def __init__(self, log_file: Path | None = None, console_output: bool = True):
        """Initialize the request logger.

        Args:
            log_file: Path to the JSONL log file. If None, logs will only be stored in memory.
            console_output: Whether to output logs to stderr (default: True)
        """
        self.log_file = log_file
        self.console_output = console_output
        self.log_entries: list[LogEntry] = []

        # Create log file directory if it doesn't exist
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info(
                'Request logs will be saved',
                log_file=str(self.log_file),
            )

        if self.console_output:
            logger.info('Request logs will be output to stderr')

    def generate_request_id(self) -> str:
        """Generate a unique request identifier.

        Returns:
            A unique UUID string for the request.
        """
        return str(uuid.uuid4())

    def _output_to_console(self, log_entry: LogEntry) -> None:
        """Output log entry to stderr in JSON format."""
        if self.console_output:
            json_data = log_entry.to_dict()
            print(json.dumps(json_data, ensure_ascii=False), file=sys.stderr)

    def log_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        body: dict[str, Any] | None = None,
        path_params: dict[str, Any] | None = None,
    ) -> str:
        """Log an outgoing HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            cookies: Request cookies
            body: Request body (for POST/PUT requests)
            path_params: Path parameters used in the request

        Returns:
            The generated request ID for this request.
        """
        request_id = self.generate_request_id()

        # Create request info
        request_info = RequestInfo(
            method=method.upper(),
            url=url,
            headers=headers,
            cookies=cookies,
            body=body,
            path_params=path_params,
        )

        # Create request log entry
        request_entry = RequestLogEntry(
            request_id=request_id,
            timestamp=datetime.now(),
            request=request_info,
        )

        self.log_entries.append(request_entry)

        # Output to console if enabled
        self._output_to_console(request_entry)

        # Add request ID to headers for tracking
        headers['X-Request-ID'] = request_id

        logger.debug(
            'Logged request',
            request_id=request_id,
            method=method,
            url=url,
        )
        return request_id

    def log_response(
        self,
        request_id: str,
        status_code: int,
        response_headers: dict[str, str],
        response_body: str,
        response_time: float,
    ) -> None:
        """Log an HTTP response.

        Args:
            request_id: The ID of the corresponding request
            status_code: HTTP response status code
            response_headers: Response headers
            response_body: Response body content
            response_time: Response time in seconds
        """
        # Create response info
        response_info = ResponseInfo(
            status_code=status_code,
            headers=response_headers,
            body=response_body,
            response_time=response_time,
        )

        # Create response log entry
        response_entry = ResponseLogEntry(
            request_id=request_id,
            timestamp=datetime.now(),
            response=response_info,
        )

        self.log_entries.append(response_entry)

        # Output to console if enabled
        self._output_to_console(response_entry)

        logger.debug(
            'Logged response',
            request_id=request_id,
            status_code=status_code,
            response_time=response_time,
        )

    def log_error(
        self,
        request_id: str,
        error: str,
        error_type: str = 'request_error',
    ) -> None:
        """Log an error that occurred during request processing.

        Args:
            request_id: The ID of the corresponding request
            error: Error message
            error_type: Type of error (e.g., 'request_error', 'timeout_error')
        """
        # Create error info
        error_info = ErrorInfo(
            error=error,
            error_type=error_type,
        )

        # Create error log entry
        error_entry = ErrorLogEntry(
            request_id=request_id,
            timestamp=datetime.now(),
            error=error_info,
        )

        self.log_entries.append(error_entry)

        # Output to console if enabled
        self._output_to_console(error_entry)

        logger.debug(
            'Logged error',
            request_id=request_id,
            error=error,
            error_type=error_type,
        )

    def save_logs(self) -> None:
        """Save all logged entries to the JSONL file."""
        if not self.log_file:
            logger.warning('No log file specified, logs will not be saved')
            return

        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                for log_entry in self.log_entries:
                    f.write(
                        json.dumps(
                            log_entry.to_dict(),
                            ensure_ascii=False,
                        ) + '\n',
                    )

            logger.info(
                'Saved log entries',
                count=len(self.log_entries),
                log_file=str(self.log_file),
            )
        except Exception as e:
            logger.error(
                'Failed to save logs',
                log_file=str(self.log_file),
                error=str(e),
            )

    def get_request_response_pair(self, request_id: str) -> RequestResponsePair | None:
        """Get a complete request-response pair by request ID.

        Args:
            request_id: The request ID to look up

        Returns:
            RequestResponsePair object containing the request and response data, or None if not found.
        """
        request_entry = None
        response_entry = None
        error_entry = None

        for log_entry in self.log_entries:
            if log_entry.request_id == request_id:
                if isinstance(log_entry, RequestLogEntry):
                    request_entry = log_entry
                elif isinstance(log_entry, ResponseLogEntry):
                    response_entry = log_entry
                elif isinstance(log_entry, ErrorLogEntry):
                    error_entry = log_entry

        if not request_entry:
            return None

        return RequestResponsePair(
            request_id=request_id,
            request=request_entry,
            response=response_entry,
            error=error_entry,
        )

    def get_all_pairs(self) -> list[RequestResponsePair]:
        """Get all complete request-response pairs.

        Returns:
            List of RequestResponsePair objects.
        """
        request_ids = set()
        for log_entry in self.log_entries:
            if isinstance(log_entry, RequestLogEntry):
                request_ids.add(log_entry.request_id)

        pairs = []
        for request_id in request_ids:
            pair = self.get_request_response_pair(request_id)
            if pair:
                pairs.append(pair)

        return pairs

    def clear_logs(self) -> None:
        """Clear all stored log entries from memory."""
        self.log_entries.clear()
        logger.debug('Cleared all stored logs')

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the logged requests.

        Returns:
            Dictionary containing request statistics.
        """
        requests = [
            e for e in self.log_entries if isinstance(
                e, RequestLogEntry,
            )
        ]
        responses = [
            e for e in self.log_entries if isinstance(
                e, ResponseLogEntry,
            )
        ]
        errors = [e for e in self.log_entries if isinstance(e, ErrorLogEntry)]

        # Count by HTTP method
        method_counts: dict[str, int] = {}
        for req in requests:
            method = req.request.method
            method_counts[method] = method_counts.get(method, 0) + 1

        # Count by status code
        status_counts: dict[int, int] = {}
        for resp in responses:
            status = resp.response.status_code
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            'total_requests': len(requests),
            'total_responses': len(responses),
            'total_errors': len(errors),
            'method_distribution': method_counts,
            'status_code_distribution': status_counts,
            'log_file': str(self.log_file) if self.log_file else None,
        }
