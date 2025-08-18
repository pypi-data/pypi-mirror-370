"""
Lexia Models
============

Pydantic models for Lexia API communication.
"""

from typing import Optional, List, Any
from pydantic import BaseModel


class Variable(BaseModel):
    """Variable model for environment variables from Lexia request."""
    name: str
    value: str


class ChatMessage(BaseModel):
    """Request model for chat messages matching Lexia's expected format."""
    thread_id: str
    model: str
    message: str
    conversation_id: int
    response_uuid: str
    message_uuid: str
    channel: str
    file_type: str = ""
    file_url: str = ""
    variables: List[Variable]
    url: str
    url_update: str = ""
    url_upload: str = ""
    force_search: bool = False
    force_code: Optional[bool] = None
    system_message: Optional[str] = None
    memory: List = []
    project_system_message: Optional[str] = None
    first_message: bool = False
    project_id: str = ""
    project_files: Optional[Any] = None
    stream_url: Optional[str] = None
    stream_token: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat requests matching Lexia's expected format."""
    status: str
    message: str
    response_uuid: str
    thread_id: str
