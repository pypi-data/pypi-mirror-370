"""
Utilities
========

Common utility functions for Lexia integration.
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def set_env_variables(variables):
    """
    Set environment variables from the variables list.
    
    Lexia sends variables in format: [{"name": "OPENAI_API_KEY", "value": "..."}]
    Supports both Pydantic models and dictionaries.
    
    Args:
        variables: List of Variable objects or dictionaries from request
    """
    if not variables:
        logger.warning("No variables provided to set_env_variables")
        return
        
    for var in variables:
        try:
            # Handle Pydantic models
            if hasattr(var, 'name') and hasattr(var, 'value'):
                os.environ[var.name] = var.value
                logger.info(f"Set environment variable: {var.name}")
            # Handle dictionaries
            elif isinstance(var, dict) and 'name' in var and 'value' in var:
                os.environ[var['name']] = var['value']
                logger.info(f"Set environment variable: {var['name']}")
            else:
                logger.warning(f"Invalid variable format: {var}")
        except Exception as e:
            logger.error(f"Error setting environment variable: {e}")


def get_openai_api_key(variables) -> Optional[str]:
    """
    Extract OpenAI API key from variables list.
    
    Supports both Pydantic models and dictionaries.
    
    Args:
        variables: List of Variable objects or dictionaries from request
        
    Returns:
        OpenAI API key string or None if not found
    """
    if not variables:
        logger.warning("No variables provided to get_openai_api_key")
        return None
        
    for var in variables:
        try:
            # Handle Pydantic models
            if hasattr(var, 'name') and hasattr(var, 'value'):
                if var.name == "OPENAI_API_KEY":
                    return var.value
            # Handle dictionaries
            elif isinstance(var, dict) and 'name' in var and 'value' in var:
                if var['name'] == "OPENAI_API_KEY":
                    return var['value']
            else:
                logger.warning(f"Invalid variable format: {var}")
        except Exception as e:
            logger.error(f"Error processing variable: {e}")
    
    logger.warning("OPENAI_API_KEY not found in variables")
    return None


def format_system_prompt(system_message: str = None, project_system_message: str = None) -> str:
    """
    Format the system prompt for OpenAI API.
    
    Args:
        system_message: Custom system message
        project_system_message: Project-specific system message
        
    Returns:
        Formatted system prompt string
    """
    default_system_prompt = """You are a helpful AI assistant. You provide clear, accurate, and helpful responses.
    
Guidelines:
- Be concise but informative
- Use markdown formatting when helpful
- If you don't know something, say so
- Be friendly and professional
- Provide examples when helpful"""

    # Use project system message if available, then custom system message, then default
    return project_system_message or system_message or default_system_prompt


def format_messages_for_openai(system_prompt: str, conversation_history: List[Dict[str, str]], current_message: str) -> List[Dict[str, str]]:
    """
    Format messages for OpenAI API call.
    
    Args:
        system_prompt: System prompt to use
        conversation_history: Previous conversation messages
        current_message: Current user message
        
    Returns:
        List of messages formatted for OpenAI API
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history (excluding the current user message)
    for hist_msg in conversation_history[:-1]:  # Exclude the last message (current user message)
        messages.append(hist_msg)
    
    # Add current user message
    messages.append({"role": "user", "content": current_message})
    
    return messages
