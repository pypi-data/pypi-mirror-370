"""Report generation utilities for OpenAPI Scanner.

This module provides functionality for generating scan results in various formats.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

import jinja2
import structlog

from specphp_scanner.core.result import ScanResult

logger = structlog.get_logger(__name__)


class ReportFormat(Enum):
    """Supported report formats."""
    CONSOLE = 'console'
    HTML = 'html'
    CSV = 'csv'
    JSONL = 'jsonl'


def generate_report(
    results: list[ScanResult],
    format: ReportFormat,
    output_file: Path | None,
) -> None:
    """Generate a report in the specified format.

    Args:
        results: List of scan results
        format: Desired output format
        output_file: Path to save the report

    Raises:
        ValueError: If the format is not supported, output file is invalid, or results is None/empty
    """
    if results is None:
        raise ValueError('No scan results to report')

    if not results:
        logger.warning('No scan results to report')
        return

    if format == ReportFormat.HTML:
        generate_html_report(results, output_file)  # type: ignore
    elif format == ReportFormat.CSV:
        generate_csv_report(results, output_file)  # type: ignore
    elif format == ReportFormat.JSONL:
        generate_jsonl_report(results, output_file)  # type: ignore
    else:
        raise ValueError(f"Unsupported report format: {format}")


def generate_html_report(results: list[ScanResult], output_file: Path) -> None:
    """Generate an HTML report.

    Args:
        results: List of scan results
        output_file: Path to save the HTML report

    Raises:
        ValueError: If the output file is invalid or template rendering fails
    """
    logger.debug(f"Generating HTML report to {output_file}")

    # Calculate summary statistics
    total_requests = len(results)
    success_count = sum(1 for r in results if r.is_success)
    redirect_count = sum(
        1 for r in results if r.status_code and 300 <= r.status_code < 400
    )
    error_count = sum(1 for r in results if r.is_error)

    # Get template directory
    template_dir = Path(__file__).parent / 'templates'

    # Create Jinja2 environment
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
    template = env.get_template('report.html')

    # Render template
    html = template.render(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        results=results,
        total_requests=total_requests,
        success_count=success_count,
        redirect_count=redirect_count,
        error_count=error_count,
    )

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    logger.debug('HTML report generated successfully')


def generate_csv_report(results: list[ScanResult], output_file: Path) -> None:
    """Generate a CSV report.

    Args:
        results: List of scan results
        output_file: Path to save the CSV report

    Raises:
        ValueError: If the output file is invalid or CSV generation fails
    """
    try:
        # Define CSV fields
        fields = ['method', 'url', 'status_code', 'response_time', 'error']

        # Write CSV file
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for result in results:
                # Extract relevant fields
                row = {
                    'method': result.method,
                    'url': result.url,
                    'status_code': str(result.status_code) if result.status_code is not None else '',
                    'response_time': str(result.response_time) if result.response_time is not None else '',
                    'error': result.error or '',
                }
                writer.writerow(row)
    except Exception as e:
        raise ValueError(f"Failed to generate CSV report: {e}")


def generate_jsonl_report(results: list[ScanResult], output_file: Path) -> None:
    """Generate a JSONL report.

    Args:
        results: List of scan results
        output_file: Path to save the JSONL report

    Raises:
        ValueError: If the output file is invalid or JSONL generation fails
    """
    try:
        # Write JSONL file
        with open(output_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result.to_dict()) + '\n')
    except Exception as e:
        raise ValueError(f"Failed to generate JSONL report: {e}")
