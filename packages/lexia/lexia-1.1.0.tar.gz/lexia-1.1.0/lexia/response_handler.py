"""
Lexia Response Handler
======================

Handles creation of Lexia-compatible API responses.
"""

from .models import ChatResponse


def create_success_response(response_uuid: str, thread_id: str, message: str = "Processing started") -> ChatResponse:
    """Create a standard success response for Lexia."""
    return ChatResponse(
        status="success",
        message=message,
        response_uuid=response_uuid,
        thread_id=thread_id
    )


def create_complete_response(response_uuid: str, thread_id: str, content: str, usage_info=None, file_url=None) -> dict:
    """Create a complete response with all required fields for Lexia API."""
    # Calculate default token counts if usage_info is missing
    if not usage_info:
        estimated_tokens = len(content.split()) if content else 1
        input_tokens = 1
        output_tokens = estimated_tokens
        total_tokens = input_tokens + output_tokens
    else:
        input_tokens = usage_info.get('prompt_tokens', 1)
        output_tokens = usage_info.get('completion_tokens', 1)
        total_tokens = usage_info.get('total_tokens', input_tokens + output_tokens)
    
    response_data = {
        'uuid': response_uuid,
        'conversation_id': None,  # Will be set by the handler
        'content': content,
        'role': 'assistant',
        'status': 'FINISHED',  # Changed from 'completed' to 'success'
        'usage': {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'input_token_details': {
                'tokens': [{"token": "default", "logprob": 0.0}] if input_tokens > 0 else []
            },
            'output_token_details': {
                'tokens': [{"token": "default", "logprob": 0.0}] if output_tokens > 0 else []
            }
        }
    }
    
    # Add file field if provided (for DALL-E generated images)
    if file_url:
        response_data['file'] = file_url
    
    return response_data
