"""
AIgents Client Data Models
=========================

Data models representing API responses, similar to OpenAI client.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Application:
    """Represents an AIgents application."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        """Create Application from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


@dataclass
class Agent:
    """Represents an AIgents agent."""
    id: str
    name: str
    description: Optional[str] = None
    model_id: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create Agent from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            model_id=data.get('model_id'),
            system_prompt=data.get('system_prompt'),
            temperature=data.get('temperature'),
            max_output_tokens=data.get('max_output_tokens'),
            created_at=data.get('created_at')
        )


@dataclass
class Tool:
    """Represents a tool available to agents."""
    id: str
    name: str
    description: Optional[str] = None
    tool_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tool':
        """Create Tool from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            tool_type=data.get('tool_type')
        )


@dataclass
class MCP:
    """Represents an MCP (Model Context Protocol) server."""
    id: str
    name: str
    description: Optional[str] = None
    server_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCP':
        """Create MCP from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            server_url=data.get('server_url')
        )


@dataclass
class Dataset:
    """Represents a training dataset."""
    id: str
    name: str
    description: Optional[str] = None
    session_count: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dataset':
        """Create Dataset from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            session_count=data.get('session_count'),
            created_at=data.get('created_at')
        )


@dataclass
class ToolCall:
    """Represents a tool call."""
    id: str
    function: Dict[str, Any]  # Contains name and arguments
    type: str = "function"


@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # For tool responses
    mcp_approval_request_id: Optional[str] = None
    mcp_approval_status: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for API requests."""
        data = {"role": self.role}
        
        if self.content:
            data["content"] = self.content
        
        if self.tool_calls:
            data["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": tc.function
                }
                for tc in self.tool_calls
            ]
        
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        
        if self.mcp_approval_request_id:
            data["mcp_approval_request_id"] = self.mcp_approval_request_id
            
        if self.mcp_approval_status is not None:
            data["mcp_approval_status"] = self.mcp_approval_status
        
        return data


@dataclass
class ChatResponse:
    """Represents a response from the chat API."""
    content: Optional[str] = None
    role: str = "assistant"
    tool_calls: Optional[List[ToolCall]] = None
    usage: Optional[Dict[str, Any]] = None
    requires_mcp_approval: bool = False
    mcp_approval_request_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatResponse':
        """Create ChatResponse from API response data."""
        tool_calls = None
        if data.get('tool_calls'):
            tool_calls = [
                ToolCall(
                    id=tc['id'],
                    type=tc.get('type', 'function'),
                    function=tc['function']
                )
                for tc in data['tool_calls']
            ]
        
        return cls(
            content=data.get('content'),
            role=data.get('role', 'assistant'),
            tool_calls=tool_calls,
            usage=data.get('usage'),
            requires_mcp_approval=data.get('requires_mcp_approval', False),
            mcp_approval_request_id=data.get('mcp_approval_request_id')
        )