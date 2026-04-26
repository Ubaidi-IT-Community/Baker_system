"""
Logging System - DEPRECATED
This module has been moved to app_logging to avoid conflicts with Python's standard logging module.
Please import from app_logging.logger instead.
"""

# Redirect to new location for backwards compatibility
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app_logging.logger import SystemLogger, system_logger

__all__ = ['SystemLogger', 'system_logger']

