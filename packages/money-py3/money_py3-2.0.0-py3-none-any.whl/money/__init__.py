"""
Python money class with optional CLDR-backed locale-aware formatting
and an extensible currency exchange solution.

This is a modernized Python 3.9+ version of the original 'money' library
by Carlos Palol (https://github.com/carlospalol/money).
"""
from .money import Money, XMoney  # noqa: F401
from .exchange import xrates  # noqa: F401


# RADAR: version
__version__ = '2.0.0'
