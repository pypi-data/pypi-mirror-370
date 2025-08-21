#!/usr/bin/env python3
"""Test runner script for specphp-scanner."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Discover and run tests
if __name__ == '__main__':
    # Discover tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = str(project_root / 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
