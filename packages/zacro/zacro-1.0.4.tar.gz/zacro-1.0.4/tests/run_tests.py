#!/usr/bin/env python
"""
Test runner for zacro package tests
"""

import os
import sys
import unittest


# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def run_all_tests():
    """Run all zacro tests"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zacro_tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
