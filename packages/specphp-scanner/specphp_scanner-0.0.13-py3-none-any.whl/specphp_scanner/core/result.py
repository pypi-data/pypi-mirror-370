"""Result classes for API scanning operations.

This module defines result classes used to represent the outcomes of API scanning operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScanResult:
    """Represents the result of a single API endpoint scan."""

    method: str
    url: str
    status_code: int | None
    response: str | None = None
    response_time: float | None = None
    error: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def is_success(self) -> bool:
        """Check if the request was successful."""
        return self.status_code is not None and 200 <= self.status_code < 400

    @property
    def is_error(self) -> bool:
        """Check if the request resulted in an error."""
        return self.error is not None or (self.status_code is not None and self.status_code >= 400)

    def to_dict(self) -> dict:
        """Convert the result to a dictionary."""
        return {
            'method': self.method,
            'url': self.url,
            'status_code': self.status_code,
            'response': self.response,
            'response_time': self.response_time,
            'error': self.error,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class ScanSummary:
    """Represents a summary of all scan results."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    error_requests: int
    average_response_time: float
    results: list[ScanResult]

    @classmethod
    def from_results(cls, results: list[ScanResult]) -> ScanSummary:
        """Create a summary from a list of scan results."""
        total = len(results)
        successful = sum(1 for r in results if r.is_success)
        failed = sum(1 for r in results if r.is_error)
        error = sum(1 for r in results if r.error is not None)

        response_times = [
            r.response_time for r in results if r.response_time is not None
        ]
        avg_response_time = sum(response_times) / \
            len(response_times) if response_times else 0.0

        return cls(
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            error_requests=error,
            average_response_time=avg_response_time,
            results=results,
        )

    def to_dict(self) -> dict:
        """Convert the summary to a dictionary."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'error_requests': self.error_requests,
            'average_response_time': self.average_response_time,
            'results': [r.to_dict() for r in self.results],
        }
