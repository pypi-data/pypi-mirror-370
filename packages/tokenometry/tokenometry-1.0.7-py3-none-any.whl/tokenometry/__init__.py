"""
Tokenometry - A sophisticated multi-strategy crypto analysis bot for trading signals.

This package provides a flexible framework for cryptocurrency market analysis,
supporting multiple trading strategies including day trading, swing trading,
and long-term investment approaches.

Example:
    >>> from tokenometry import Tokenometry
    >>> bot = Tokenometry(config=config, logger=logger)
    >>> signals = bot.scan()
"""

__version__ = "1.0.7"
__author__ = "nguyenph88"
__email__ = "your.email@example.com"
__license__ = "MIT"
__url__ = "https://github.com/nguyenph88/Tokenometry"

from .core import Tokenometry

__all__ = ["Tokenometry"]
