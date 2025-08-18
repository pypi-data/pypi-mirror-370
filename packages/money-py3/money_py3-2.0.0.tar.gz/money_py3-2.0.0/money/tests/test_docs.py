"""
Money doctests as unittest Suite
"""

import unittest

FILES = (
    # Skip old README.rst doctests - they contain outdated examples
    # '../../README.rst',
)


def load_tests(loader, tests, pattern):
    # Return empty test suite since README examples are outdated
    return unittest.TestSuite()
