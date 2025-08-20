"""
Chat resource manager - handles conversation functionality.
"""

from typing import Dict, Any, Optional, List
from ..models import Message, ChatResponse


class Chat:
    """
    Chat resource manager.
    
    Provides methods to create and manage chat sessions with agents.
    """
    
    def __init__(self, client):
        self._client = client
    
    def create(
        self,
        application_id: str,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> 'ChatSession':
        """
        Create a new chat session or connect to existing one.
        
        Args:
            application_id: The application ID
            agent_id: The agent ID to chat with (optional)
            session_id: Existing session ID to continue (optional)
            
        Returns:
            ChatSession instance
        """
        return ChatSession(
            client=self._client,
            application_id=application_id,
            agent_id=agent_id,
            session_id=session_id
        )


class ChatSession:
    """
    Represents an active chat session with an agent.
    
    Provides a simple interface for sending messages and receiving responses.
    """
    
    def __init__(
        self,
        client,
        application_id: str,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self._client = client
        self.application_id = application_id
        self.agent_id = agent_id
        self.session_id = session_id
        self._messages: List[Message] = []
        
        # If no session_id provided, create a new session
        if not self.session_id:
            self._create_session()
    
    def _create_session(self) -> None:
        """Create a new chat session."""
        data = {}
        if self.agent_id:
            data["agent_id"] = self.agent_id
        
        response = self._client.post(
            f"/applications/{self.application_id}/chat/sessions",
            data=data
        )
        self.session_id = response.get("session_id", "default_session")
    
    def send(
        self,
        message: str,
        role: str = "user",
        stream: bool = False
    ) -> ChatResponse:
        """
        Send a message and get response.
        
        Args:
            message: The message content
            role: Message role (default: "user")
            stream: Whether to stream the response (not implemented yet)
            
        Returns:
            ChatResponse with the agent's reply
        """
        # Add user message to conversation history
        user_message = Message(role=role, content=message)
        self._messages.append(user_message)
        
        # Send message to API
        data = {
            "role": role,
            "content": message
        }
        
        response = self._client.post(
            f"/applications/{self.application_id}/chat/sessions/{self.session_id}/messages",
            data=data
        )
        
        # Parse response
        chat_response = ChatResponse.from_dict(response)
        
        # Add assistant response to conversation history
        assistant_message = Message(
            role=chat_response.role, 
            content=chat_response.content,
            tool_calls=chat_response.tool_calls,
            mcp_approval_request_id=chat_response.mcp_approval_request_id
        )
        self._messages.append(assistant_message)
        
        return chat_response
    
    def send_tool_result(
        self,
        tool_call_id: str,
        result: str,
        role: str = "tool"
    ) -> ChatResponse:
        """
        Send a tool result back to the conversation.
        
        Args:
            tool_call_id: The ID of the tool call being responded to
            result: The result of the tool execution
            role: Message role (default: "tool")
            
        Returns:
            ChatResponse with the agent's follow-up
        """
        # Add tool result message to conversation history
        tool_message = Message(
            role=role,
            content=result,
            tool_call_id=tool_call_id
        )
        self._messages.append(tool_message)
        
        # Send tool result to API
        data = {
            "role": role,
            "content": result,
            "tool_call_id": tool_call_id
        }
        
        response = self._client.post(
            f"/applications/{self.application_id}/chat/sessions/{self.session_id}/messages",
            data=data
        )
        
        # Parse response
        chat_response = ChatResponse.from_dict(response)
        
        # Add assistant response to conversation history
        assistant_message = Message(
            role=chat_response.role,
            content=chat_response.content,
            tool_calls=chat_response.tool_calls,
            mcp_approval_request_id=chat_response.mcp_approval_request_id
        )
        self._messages.append(assistant_message)
        
        return chat_response
    
    def approve_mcp_request(
        self,
        mcp_approval_request_id: str,
        approved: bool = True
    ) -> ChatResponse:
        """
        Approve or reject an MCP request.
        
        Args:
            mcp_approval_request_id: The ID of the MCP request
            approved: Whether to approve (True) or reject (False)
            
        Returns:
            ChatResponse with the result of the MCP execution
        """
        # Add approval message to conversation history
        approval_message = Message(
            role="system",
            content=f"MCP request {'approved' if approved else 'rejected'}",
            mcp_approval_request_id=mcp_approval_request_id,
            mcp_approval_status=approved
        )
        self._messages.append(approval_message)
        
        # Send approval to API
        data = {
            "role": "system",
            "content": "mcp_approval",
            "mcp_approval_request_id": mcp_approval_request_id,
            "mcp_approval_status": approved
        }
        
        response = self._client.post(
            f"/applications/{self.application_id}/chat/sessions/{self.session_id}/messages",
            data=data
        )
        
        # Parse response
        chat_response = ChatResponse.from_dict(response)
        
        # Add assistant response to conversation history
        assistant_message = Message(
            role=chat_response.role,
            content=chat_response.content,
            tool_calls=chat_response.tool_calls
        )
        self._messages.append(assistant_message)
        
        return chat_response
    
    def get_history(self) -> List[Message]:
        """
        Get the conversation history for this session.
        
        Returns:
            List of Message objects
        """
        return self._messages.copy()
    
    def clear_history(self) -> None:
        """Clear the local conversation history."""
        self._messages.clear()
    
    def __repr__(self) -> str:
        return f"ChatSession(application_id='{self.application_id}', session_id='{self.session_id}')"