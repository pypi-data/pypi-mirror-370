"""
Lexia Web Package
================

Web framework utilities for creating FastAPI applications with Lexia integration.
Provides standard endpoints, middleware, and app factory functions.
"""

from .app_factory import create_lexia_app
from .endpoints import add_standard_endpoints

__all__ = [
    'create_lexia_app',
    'add_standard_endpoints'
]
