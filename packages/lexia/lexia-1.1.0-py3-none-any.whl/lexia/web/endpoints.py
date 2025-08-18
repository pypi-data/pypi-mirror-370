"""
Lexia Standard Endpoints
========================

Standard endpoint patterns for Lexia applications.
These can be added to any FastAPI app using add_standard_endpoints().
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import asyncio

logger = logging.getLogger(__name__)

def add_standard_endpoints(app, conversation_manager=None, lexia_handler=None, process_message_func=None):
    """
    Add standard Lexia endpoints to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        conversation_manager: Optional conversation manager for history endpoints
        lexia_handler: Optional LexiaHandler instance for communication
        process_message_func: Optional function to process messages (custom AI logic)
    """
    
    # Create router for standard endpoints
    router = APIRouter(prefix="/api/v1", tags=["standard"])
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy", 
            "service": "Lexia AI Agent",
            "version": "1.1.0"
        }
    
    @router.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "message": "Lexia AI Agent - Ready",
            "endpoints": [
                "/api/v1/health",
                "/api/v1/send_message",
                "/docs"
            ]
        }
    
    # Add the main send_message endpoint if lexia_handler is provided
    if lexia_handler and process_message_func:
        from ..models import ChatMessage, ChatResponse
        from ..response_handler import create_success_response
        
        @router.post("/send_message", response_model=ChatResponse)
        async def send_message(data: ChatMessage):
            """Main chat endpoint - inherited from Lexia package."""
            if not data.message.strip() or not data.channel or not data.variables:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # Start processing in background
            asyncio.create_task(process_message_func(data))
            
            # Return immediate success response
            return create_success_response(
                response_uuid=data.response_uuid,
                thread_id=data.thread_id
            )
    
    # Add conversation history endpoints if conversation manager is provided
    if conversation_manager:
        @router.get("/conversation/{thread_id}/history")
        async def get_history(thread_id: str):
            """Get conversation history for a thread."""
            try:
                history = conversation_manager.get_history(thread_id)
                return {
                    "thread_id": thread_id, 
                    "history": history, 
                    "count": len(history)
                }
            except Exception as e:
                logger.error(f"Error getting history for thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to get conversation history")
        
        @router.delete("/conversation/{thread_id}/history")
        async def clear_history(thread_id: str):
            """Clear conversation history for a thread."""
            try:
                conversation_manager.clear_history(thread_id)
                return {
                    "status": "success", 
                    "thread_id": thread_id,
                    "message": "Conversation history cleared"
                }
            except Exception as e:
                logger.error(f"Error clearing history for thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to clear conversation history")
    
    # Include the router in the app
    app.include_router(router)
    
    return app
