"""
Package initializer for Goldloop modules.
Currently only affiliate_injector is active.
"""

from .affiliate_injector import run_affiliate_injection

__all__ = ["run_affiliate_injection"]
