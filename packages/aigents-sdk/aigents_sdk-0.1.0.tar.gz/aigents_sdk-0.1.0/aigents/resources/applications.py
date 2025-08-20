"""
Applications resource manager - handles app-related operations.
"""

from typing import List, Dict, Any, Optional
from ..models import Application, Agent, Tool, MCP, Dataset


class Applications:
    """
    Applications resource manager.
    
    Provides methods to manage applications and their nested resources
    (agents, tools, MCPs, datasets).
    """
    
    def __init__(self, client):
        self._client = client
        self.agents = AgentManager(client)
        self.tools = ToolManager(client)
        self.mcps = MCPManager(client)
        self.datasets = DatasetManager(client)
    
    def list(self) -> List[Application]:
        """
        List all applications owned by the current user.
        
        Returns:
            List of Application objects
        """
        response = self._client.get("/applications")
        return [Application.from_dict(app) for app in response]
    
    def get(self, application_id: str) -> Application:
        """
        Get a specific application by ID.
        
        Args:
            application_id: The application ID
            
        Returns:
            Application object
        """
        response = self._client.get(f"/applications/{application_id}")
        return Application.from_dict(response)
    
    def create(
        self, 
        name: str, 
        description: Optional[str] = None
    ) -> Application:
        """
        Create a new application.
        
        Args:
            name: Application name
            description: Optional description
            
        Returns:
            Created Application object
        """
        data = {"name": name}
        if description:
            data["description"] = description
        
        response = self._client.post("/applications", data=data)
        return Application.from_dict(response)
    
    def update(
        self,
        application_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Application:
        """
        Update an existing application.
        
        Args:
            application_id: The application ID
            name: New application name
            description: New description
            
        Returns:
            Updated Application object
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        
        response = self._client.put(f"/applications/{application_id}", data=data)
        return Application.from_dict(response)
    
    def delete(self, application_id: str) -> None:
        """
        Delete an application.
        
        Args:
            application_id: The application ID
        """
        self._client.delete(f"/applications/{application_id}")


class AgentManager:
    """Manages agents within an application."""
    
    def __init__(self, client):
        self._client = client
    
    def list(self, application_id: str) -> List[Agent]:
        """List all agents in an application."""
        response = self._client.get(f"/applications/{application_id}/agents")
        return [Agent.from_dict(agent) for agent in response]
    
    def get(self, application_id: str, agent_id: str) -> Agent:
        """Get a specific agent by ID."""
        response = self._client.get(f"/applications/{application_id}/agents/{agent_id}")
        return Agent.from_dict(response)
    
    def create(
        self,
        application_id: str,
        name: str,
        description: Optional[str] = None,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Agent:
        """Create a new agent."""
        data = {"name": name}
        if description:
            data["description"] = description
        if model_id:
            data["model_id"] = model_id
        if system_prompt:
            data["system_prompt"] = system_prompt
        if temperature is not None:
            data["temperature"] = temperature
        if max_output_tokens:
            data["max_output_tokens"] = max_output_tokens
        
        response = self._client.post(f"/applications/{application_id}/agents", data=data)
        return Agent.from_dict(response)


class ToolManager:
    """Manages tools within an application."""
    
    def __init__(self, client):
        self._client = client
    
    def list(self, application_id: str, agent_id: Optional[str] = None) -> List[Tool]:
        """List tools in an application or agent."""
        if agent_id:
            response = self._client.get(f"/applications/{application_id}/agents/{agent_id}/tools")
        else:
            response = self._client.get(f"/applications/{application_id}/tools")
        return [Tool.from_dict(tool) for tool in response]


class MCPManager:
    """Manages MCP servers within an application."""
    
    def __init__(self, client):
        self._client = client
    
    def list(self, application_id: str, agent_id: Optional[str] = None) -> List[MCP]:
        """List MCP servers in an application or agent."""
        if agent_id:
            response = self._client.get(f"/applications/{application_id}/agents/{agent_id}/mcps")
        else:
            response = self._client.get(f"/applications/{application_id}/mcps")
        return [MCP.from_dict(mcp) for mcp in response]


class DatasetManager:
    """Manages datasets within an application."""
    
    def __init__(self, client):
        self._client = client
    
    def list(self, application_id: str) -> List[Dataset]:
        """List all datasets in an application."""
        response = self._client.get(f"/applications/{application_id}/datasets")
        return [Dataset.from_dict(dataset) for dataset in response]
    
    def get(self, application_id: str, dataset_id: str) -> Dataset:
        """Get a specific dataset by ID."""
        response = self._client.get(f"/applications/{application_id}/datasets/{dataset_id}")
        return Dataset.from_dict(response)
    
    def create(
        self,
        application_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Dataset:
        """Create a new dataset."""
        data = {"name": name}
        if description:
            data["description"] = description
        
        response = self._client.post(f"/applications/{application_id}/datasets", data=data)
        return Dataset.from_dict(response)
    
    def add_session(
        self,
        application_id: str,
        dataset_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a conversation session to a dataset.
        
        Args:
            application_id: The application ID
            dataset_id: The dataset ID
            messages: List of message dicts with 'role' and 'content'
            metadata: Optional metadata for the session
            
        Returns:
            Response data
        """
        data = {
            "messages": messages
        }
        if metadata:
            data["metadata"] = metadata
        
        # Note: This endpoint may need to be implemented in the backend
        return self._client.post(
            f"/applications/{application_id}/datasets/{dataset_id}/sessions",
            data=data
        )