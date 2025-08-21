#!/usr/bin/env python3
"""Main entry point for SpecPHP Scanner.

This module allows the package to be executed directly using:
    python -m specphp_scanner
"""
from __future__ import annotations

from specphp_scanner.cli import app

if __name__ == '__main__':
    app()
