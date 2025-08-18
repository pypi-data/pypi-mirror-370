"""
Lexia Integration Package
========================

Clean, minimal package for Lexia platform integration.
Contains only essential components for communication.
"""

__version__ = "1.1.0"

from .models import ChatResponse, ChatMessage, Variable
from .response_handler import create_success_response
from .unified_handler import LexiaHandler

# Web framework utilities
try:
    from .web import create_lexia_app, add_standard_endpoints
    __all__ = [
        'ChatResponse', 'ChatMessage', 'Variable',
        'create_success_response', 'LexiaHandler',
        'create_lexia_app', 'add_standard_endpoints',
        '__version__'
    ]
except ImportError:
    # Fallback if web dependencies aren't available
    __all__ = [
        'ChatResponse', 'ChatMessage', 'Variable',
        'create_success_response', 'LexiaHandler',
        '__version__'
    ]
