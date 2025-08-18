# Lexia Package

Clean, minimal package for Lexia platform integration. Contains only essential components for communication with the Lexia platform.

## 🎯 Purpose

This package provides a clean interface for your AI agent to communicate with the Lexia platform. It handles all Lexia-specific communication while keeping your AI agent completely platform-agnostic.

## 🚀 Quick Start

### 1. Copy the `lexia` folder to your new project
```bash
# Copy the entire lexia folder to your new project
cp -r lexia/ /path/to/your/new/project/
```

### 2. Install dependencies
```bash
cd /path/to/your/new/project/
pip install -r lexia/requirements.txt
```

### 3. Import and use
```python
from lexia import LexiaHandler, ChatMessage, create_success_response

# Initialize the handler
lexia = LexiaHandler()

# Use in your AI agent
async def process_message(data: ChatMessage):
    # Your AI logic here...
    response = "Hello from your AI agent!"
    lexia.complete_response(data, response)
```

## 📁 Structure

```
lexia/
├── __init__.py             # Clean exports only
├── models.py               # Lexia data models (ChatMessage, ChatResponse, Variable)
├── response_handler.py     # Response creation utilities
├── unified_handler.py      # Single communication interface
├── api_client.py           # HTTP communication with Lexia backend
├── centrifugo_client.py    # Real-time updates via Centrifugo
├── utils.py                # Platform utilities (env vars, API keys)
├── web/                    # FastAPI web framework utilities
│   ├── __init__.py
│   ├── app_factory.py
│   └── endpoints.py
├── requirements.txt         # Package dependencies
└── README.md               # This file
```

## 🚀 Core Components

### 1. LexiaHandler (Main Interface)
**Purpose**: Single, clean interface for all Lexia communication

```python
from lexia import LexiaHandler

lexia = LexiaHandler()

# Stream AI response chunks
lexia.stream_chunk(data, content)

# Complete AI response (handles all Lexia communication)
lexia.complete_response(data, full_response)

# Send error messages
lexia.send_error(data, error_message)
```

### 2. Data Models
**Purpose**: Lexia's expected data formats

```python
from lexia import ChatMessage, ChatResponse, Variable

# ChatMessage - Lexia's request format
# ChatResponse - Lexia's expected response format  
# Variable - Environment variables from Lexia
```

### 3. Response Handler
**Purpose**: Create Lexia-compatible responses

```python
from lexia import create_success_response

response = create_success_response(
    response_uuid="uuid123",
    thread_id="thread456"
)
```

## 💡 Complete Usage Examples

### Example 1: Minimal AI Agent with FastAPI

```python
# main.py
import asyncio
from fastapi import FastAPI
from lexia import (
    LexiaHandler, 
    ChatMessage, 
    create_success_response,
    create_lexia_app,
    add_standard_endpoints
)

# Initialize services
lexia = LexiaHandler()

# Create FastAPI app using Lexia's utilities
app = create_lexia_app(
    title="My AI Agent",
    version="1.1.0",
    description="Custom AI agent with Lexia integration"
)

# Define your AI logic
async def process_message(data: ChatMessage):
    """Your custom AI processing logic goes here."""
    try:
        # Example: Simple echo response
        response = f"AI Agent processed: {data.message}"
        
        # Stream response chunks (optional)
        for word in response.split():
            lexia.stream_chunk(data, word + " ")
            await asyncio.sleep(0.1)  # Simulate processing time
        
        # Complete the response
        lexia.complete_response(data, response)
        
    except Exception as e:
        lexia.send_error(data, str(e))

# Add all standard Lexia endpoints
add_standard_endpoints(
    app, 
    conversation_manager=None,  # Add your conversation manager if needed
    lexia_handler=lexia,
    process_message_func=process_message
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 2: OpenAI Integration

```python
# openai_agent.py
import asyncio
from openai import OpenAI
from lexia import LexiaHandler, ChatMessage, create_lexia_app, add_standard_endpoints

class OpenAIAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.lexia = LexiaHandler()
    
    async def process_message(self, data: ChatMessage):
        """Process message using OpenAI and send via Lexia."""
        try:
            # Get OpenAI API key from variables
            api_key = None
            for var in data.variables:
                if var.name == "OPENAI_API_KEY":
                    api_key = var.value
                    break
            
            if not api_key:
                self.lexia.send_error(data, "OpenAI API key not found")
                return
            
            # Create OpenAI client
            client = OpenAI(api_key=api_key)
            
            # Stream response from OpenAI
            stream = client.chat.completions.create(
                model=data.model,
                messages=[{"role": "user", "content": data.message}],
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
            # Stream chunks to Lexia
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    self.lexia.stream_chunk(data, content)
            
            # Complete response
            self.lexia.complete_response(data, full_response)
            
        except Exception as e:
            self.lexia.send_error(data, str(e))

# Create FastAPI app
app = create_lexia_app(title="OpenAI Agent", version="1.1.0")

# Initialize agent
agent = OpenAIAgent(api_key="your-api-key-here")

# Add endpoints
add_standard_endpoints(
    app,
    conversation_manager=None,
    lexia_handler=agent.lexia,
    process_message_func=agent.process_message
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 3: Custom Endpoints with Lexia

```python
# custom_agent.py
from fastapi import FastAPI
from lexia import (
    LexiaHandler, 
    ChatMessage, 
    create_lexia_app, 
    add_standard_endpoints
)

# Initialize
lexia = LexiaHandler()
app = create_lexia_app(title="Custom Agent", version="1.1.0")

# Your custom AI logic
async def process_message(data: ChatMessage):
    response = f"Custom AI processed: {data.message}"
    lexia.complete_response(data, response)

# Add standard endpoints
add_standard_endpoints(
    app,
    conversation_manager=None,
    lexia_handler=lexia,
    process_message_func=process_message
)

# Add your custom endpoints
@app.post("/api/v1/custom_action")
async def custom_action(data: ChatMessage):
    """Custom endpoint that doesn't use Lexia communication."""
    return {"message": "Custom action executed", "input": data.message}

@app.get("/api/v1/agent_status")
async def agent_status():
    """Get agent status."""
    return {"status": "active", "version": "1.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 4: Environment Variables and Configuration

```python
# config_agent.py
import os
from lexia import LexiaHandler, ChatMessage, create_lexia_app, add_standard_endpoints
from lexia.utils import set_env_variables, get_openai_api_key

# Initialize
lexia = LexiaHandler()
app = create_lexia_app(title="Config Agent", version="1.1.0")

async def process_message(data: ChatMessage):
    """Process message with environment configuration."""
    try:
        # Set environment variables from Lexia request
        set_env_variables(data.variables)
        
        # Get configured API key
        api_key = get_openai_api_key(data.variables)
        if not api_key:
            lexia.send_error(data, "API key not configured")
            return
        
        # Your AI logic here...
        response = f"Processed with config: {data.message}"
        lexia.complete_response(data, response)
        
    except Exception as e:
        lexia.send_error(data, str(e))

# Add endpoints
add_standard_endpoints(
    app,
    conversation_manager=None,
    lexia_handler=lexia,
    process_message_func=process_message
)
```

## 🔧 What This Package Handles

✅ **Real-time streaming** via Centrifugo  
✅ **Backend communication** with Lexia  
✅ **Response formatting** for Lexia compatibility  
✅ **Data validation** with Pydantic models  
✅ **Error handling** and notifications  
✅ **FastAPI integration** with standard endpoints  
✅ **Environment variable management**  
✅ **API key handling**  

## ❌ What This Package Does NOT Handle

❌ **AI/LLM processing** (that's your agent's job)  
❌ **Conversation memory** (that's in your `memory/` module)  
❌ **Business logic** (that's in your main application)  
❌ **Database operations**  
❌ **Authentication/Authorization**  

## 🎯 Design Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **Clean Interface**: Simple, intuitive methods
3. **Platform Agnostic**: Your AI agent doesn't know about Lexia internals
4. **Minimal Dependencies**: Only what's absolutely necessary
5. **Easy Testing**: Simple, focused components

## 🚀 Benefits

- **Clean separation** between your AI agent and Lexia
- **Easy to maintain** - all Lexia logic in one place
- **Easy to replace** - switch platforms by replacing this package
- **Professional structure** - clean, organized code
- **Fast development** - no complex integrations to manage
- **Drop-in replacement** - copy folder and start using immediately

## 🔄 Integration Flow

```
Your AI Agent → LexiaHandler → Lexia Platform
     ↓              ↓              ↓
  OpenAI/LLM   Communication   Real-time + Backend
```

Your AI agent focuses on AI logic, this package handles all Lexia communication complexity behind a clean interface.

## 📋 Setup Checklist for New Project

1. ✅ Copy `lexia/` folder to your new project
2. ✅ Install dependencies: `pip install -r lexia/requirements.txt`
3. ✅ Import: `from lexia import LexiaHandler, ChatMessage`
4. ✅ Initialize: `lexia = LexiaHandler()`
5. ✅ Use: `lexia.complete_response(data, response)`
6. ✅ Test your integration

## 🧪 Testing Your Integration

```python
# test_lexia.py
import pytest
from lexia import LexiaHandler, ChatMessage, Variable

def test_lexia_handler():
    """Test basic LexiaHandler functionality."""
    handler = LexiaHandler()
    
    # Create test data
    test_data = ChatMessage(
        thread_id="test123",
        model="gpt-4",
        message="Hello",
        conversation_id=1,
        response_uuid="uuid123",
        message_uuid="msg123",
        channel="test",
        file_type="",
        file_url="",
        variables=[],
        url="http://test.com",
        url_update="",
        url_upload="",
        force_search=False,
        system_message=None,
        memory=[],
        project_system_message=None,
        first_message=False,
        project_id="",
        project_files=None
    )
    
    # Test that handler can be created
    assert handler is not None
    assert hasattr(handler, 'stream_chunk')
    assert hasattr(handler, 'complete_response')
    assert hasattr(handler, 'send_error')

if __name__ == "__main__":
    pytest.main([__file__])
```

## 🚨 Common Issues and Solutions

### Issue: Import Error
```bash
ModuleNotFoundError: No module named 'lexia'
```
**Solution**: Make sure you're in the correct directory or add the lexia folder to your Python path.

### Issue: Missing Dependencies
```bash
ImportError: No module named 'fastapi'
```
**Solution**: Install requirements: `pip install -r lexia/requirements.txt`

### Issue: Lexia Communication Fails
**Solution**: Check that your environment variables and API keys are properly configured in the Lexia request variables.

## 📞 Support

When you move this package to your new project:
1. All Lexia communication is handled automatically
2. Standard endpoints are provided out-of-the-box
3. Your AI agent remains completely platform-agnostic
4. You can focus on building your AI logic, not integration code

The package is designed to be a drop-in solution - just copy the folder and start building your AI agent!
