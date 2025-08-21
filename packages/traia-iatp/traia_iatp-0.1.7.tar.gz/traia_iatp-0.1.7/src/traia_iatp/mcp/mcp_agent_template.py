#!/usr/bin/env python
"""
MCP Agent Template

This template provides a structured way to create agents that use MCP server tools.
It offers a simplified interface for creating specialized agents that can leverage
any MCP server by providing the server configuration.

Features:
- Automatic detection of authentication requirements
- Support for both authenticated and non-authenticated MCP servers
- Flexible agent creation with optional tool filtering
- Health checks for MCP servers

Authentication:
The template automatically detects if an MCP server requires authentication
based on metadata fields:
- requires_api_key: boolean indicating if authentication is needed
- api_key_header: the header name to use (default: "Authorization")
- headers: dictionary containing the actual API key

Usage for MCP Agents:
    1. Import the MCPAgentBuilder from this module
    2. Create your specialized agent(s) with the builder
    3. Create tasks for your agents
    4. Run your agents as a CrewAI crew with MCP server configuration

Example:
    ```python
    from mcp_agent_template import MCPAgentBuilder, run_with_mcp_tools, MCPServerInfo
    
    # Create MCP server info (you would get this from registry or configuration)
    mcp_server = MCPServerInfo(
        id="weather-123",
        name="weather-mcp",
        url="http://localhost:8080",
        description="Weather information MCP server",
        server_type="streamable-http",
        capabilities=["get_weather", "get_forecast"],
        metadata={},
        tags=["weather", "api"]
    )
    
    # For authenticated servers, include auth info in metadata:
    # metadata={
    #     "requires_api_key": True,
    #     "api_key_header": "Authorization",
    #     "headers": {"Authorization": "Bearer YOUR_API_KEY"}
    # }
    
    # Create an agent for the MCP server
    analyst = MCPAgentBuilder.create_agent(
        role="Weather Analyst",
        goal="Analyze weather conditions and provide forecasts",
        backstory="You are an expert meteorologist...",
        verbose=True
    )
    
    # Create task for the agent
    task = Task(
        description="Analyze current weather conditions in New York...",
        expected_output="A comprehensive weather report...",
        agent=analyst
    )
    
    # Run the agent with MCP tools
    result = run_with_mcp_tools([task], mcp_server=mcp_server)
    print(result)
    ```
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Import CrewAI components
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import MCPServerAdapter

# Import our custom adapter for API key support
from .traia_mcp_adapter import create_mcp_adapter, create_mcp_adapter_with_auth


logger = logging.getLogger(__name__)

# Create default LLM instance
DEFAULT_LLM = LLM(model="openai/gpt-4.1", temperature=0.7)


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    id: str
    name: str
    url: str
    description: str
    server_type: str
    capabilities: List[str]
    metadata: Dict[str, Any]
    tags: List[str]


class MCPServerConfig:
    """Configuration for an MCP server - used for utility agency creation."""
    
    def __init__(
        self,
        name: str,
        url: str,
        description: str,
        server_type: str = "streamable-http",  # Only streamable-http is supported
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.url = url
        self.description = description
        self.server_type = server_type
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "server_type": self.server_type,
            "capabilities": self.capabilities,
            "metadata": self.metadata
        }


class MCPAgentBuilder:
    """
    Builder class for creating agents that use MCP server tools.
    """
    
    # Class variable to store tool subsets for agents (using agent id as key)
    _agent_tool_subsets = {}
    
    @staticmethod
    def create_agent(
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = True,
        allow_delegation: bool = False,
        llm: LLM = None,
        tools_subset: List[str] = None
    ) -> Agent:
        """
        Create a CrewAI agent for use with MCP tools.
        
        Args:
            role: The role of the agent
            goal: The primary goal of the agent
            backstory: Background story for the agent
            verbose: Whether to enable verbose output
            allow_delegation: Whether to allow the agent to delegate tasks
            llm: The LLM instance to use (defaults to gpt-4.1 with temperature 0.7)
            tools_subset: Optional list of specific tool names to include (if None, all tools are included)
            
        Returns:
            CrewAI Agent configured for MCP tools
        """
        # Use specified LLM or default
        if llm is None:
            llm = DEFAULT_LLM
        
        # We'll set tools later when run_with_mcp_tools is called
        # This is because tools require the MCP server connection
        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
            llm=llm
        )
        
        # Store the tools_subset in the class dictionary
        if tools_subset is not None:
            MCPAgentBuilder._agent_tool_subsets[id(agent)] = tools_subset
        
        return agent
    
    @staticmethod
    def get_tools_subset(agent: Agent) -> Optional[List[str]]:
        """Get the tools subset for a specific agent"""
        return MCPAgentBuilder._agent_tool_subsets.get(id(agent))


def check_server_health(server_info: MCPServerInfo, api_key: Optional[str] = None) -> bool:
    """
    Check if the MCP server is running and healthy by attempting to connect
    and list available tools.
    
    Args:
        server_info: MCPServerInfo object with server details
        api_key: Optional API key for authenticated servers
        
    Returns:
        True if the server is healthy, False otherwise
    """
    try:
        # Check if authentication is required
        requires_api_key = server_info.metadata.get("requires_api_key", False)
        api_key_header = server_info.metadata.get("api_key_header", "Authorization")
        
        # Create appropriate adapter
        if requires_api_key and api_key:
            # Use the provided API key directly (user provides raw key without Bearer prefix)
            adapter = create_mcp_adapter_with_auth(
                url=server_info.url,
                api_key=api_key,
                auth_header=api_key_header,
                auth_prefix="Bearer"  # We add the Bearer prefix
            )
        else:
            # No authentication required or no API key provided
            adapter = create_mcp_adapter(url=server_info.url)
        
        # Try to connect and list tools
        with adapter as mcp_tools:
            tools = list(mcp_tools)
            print(f"✓ MCP server '{server_info.name}' is healthy ({len(tools)} tools available)")
            return True
            
    except Exception as e:
        print(f"✗ MCP server '{server_info.name}' health check failed: {e}")
        return False


def run_with_mcp_tools(
    tasks: List[Task], 
    mcp_server: MCPServerInfo,
    agents: Optional[List[Agent]] = None,
    process: Process = Process.sequential,
    verbose: bool = True,
    inputs: Optional[Dict[str, Any]] = None,
    skip_health_check: bool = False,
    api_key: Optional[str] = None
) -> Any:
    """
    Run tasks with agents that have access to MCP server tools.
    
    NOTE ON AUTHENTICATION:
    This function automatically detects if the MCP server requires authentication
    based on the server's metadata. If authentication is required, you must provide
    your API key using the api_key parameter.
    
    Args:
        tasks: List of tasks to run
        mcp_server: MCPServerInfo object with server details
        agents: Optional list of agents (if None, will use agents from tasks)
        process: CrewAI process type (sequential or hierarchical)
        verbose: Whether to enable verbose output
        inputs: Optional inputs for the crew
        skip_health_check: Skip server health check
        api_key: Optional API key for authenticated MCP servers
        
    Returns:
        Result from the crew execution
    """
    # Check if the server is healthy (unless skipped)
    if not skip_health_check:
        # Pass the API key for health check if authentication is required
        if not check_server_health(mcp_server, api_key):
            print(f"MCP server '{mcp_server.name}' is not healthy.")
            print(f"Server URL: {mcp_server.url}")
            sys.exit(1)
    
    # Check if authentication is required
    requires_api_key = mcp_server.metadata.get("requires_api_key", False)
    api_key_header = mcp_server.metadata.get("api_key_header", "Authorization")
    
    # Create appropriate adapter
    if requires_api_key:
        if not api_key:
            print(f"\n⚠️  WARNING: MCP server '{mcp_server.name}' requires authentication")
            print(f"Expected header: {api_key_header}")
            print("But no API key was provided.")
            print("\nTo provide authentication:")
            print("Pass your API key using the 'api_key' parameter")
            print("Example: run_with_mcp_tools(tasks, mcp_server, api_key='YOUR_API_KEY')")
            sys.exit(1)
        
        # Use the provided API key directly (user provides raw key without Bearer prefix)
        adapter = create_mcp_adapter_with_auth(
            url=mcp_server.url,
            api_key=api_key,
            auth_header=api_key_header,
            auth_prefix="Bearer"  # We add the Bearer prefix
        )
        print(f"\n🔐 Using authenticated connection (header: {api_key_header})")
    else:
        # No authentication required
        adapter = create_mcp_adapter(url=mcp_server.url)
        print("\n🔓 Using standard connection (no authentication)")
    
    # Get agents from tasks if not provided
    if agents is None:
        agents = [task.agent for task in tasks]
        # Remove duplicates while preserving order
        seen = set()
        agents = [agent for agent in agents if not (agent in seen or seen.add(agent))]
    
    try:
        # Use context manager for MCP server connection
        with adapter as all_tools:
            print(f"Connected to MCP server '{mcp_server.name}'")
            print(f"Available tools: {[tool.name for tool in all_tools]}")
            
            # Assign tools to each agent based on their tools_subset if defined
            for agent in agents:
                # Get the tools subset from the class dictionary
                tools_subset = MCPAgentBuilder.get_tools_subset(agent)
                if tools_subset:
                    # Filter tools by name if a subset is specified
                    agent.tools = [tool for tool in all_tools if tool.name in tools_subset]
                    print(f"Agent '{agent.role}' assigned tools: {[tool.name for tool in agent.tools]}")
                else:
                    # Use all tools if no subset is specified
                    agent.tools = all_tools
                    print(f"Agent '{agent.role}' assigned all available tools")
            
            # Create and run the crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=verbose,
                process=process
            )
            
            # Kickoff the crew with inputs
            result = crew.kickoff(inputs=inputs or {})
            return result
            
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# Example usage when running this file directly
if __name__ == "__main__":
    # This example shows how to use the template without registry
    print("MCP Agent Template Example")
    print("=" * 80)
    
    # Example MCP server configuration (would normally come from registry or config)
    example_server = MCPServerInfo(
        id="example-123",
        name="example-mcp",
        url="http://localhost:8080/mcp/",  # Add trailing slash
        description="Example MCP server for demonstration",
        server_type="streamable-http",
        capabilities=["example_tool1", "example_tool2"],
        metadata={},
        tags=["example", "demo"]
    )
    
    # Example of MCP server that requires authentication:
    # authenticated_server = MCPServerInfo(
    #     id="news-456",
    #     name="newsapi-mcp",
    #     url="http://localhost:8000/mcp/",  # Add trailing slash
    #     description="NewsAPI MCP server",
    #     server_type="streamable-http",
    #     capabilities=["search_news", "get_headlines"],
    #     metadata={
    #         "requires_api_key": True,
    #         "api_key_header": "Authorization",
    #         "headers": {
    #             "Authorization": "Bearer YOUR_API_KEY"  # Client API key
    #         }
    #     },
    #     tags=["news", "api"]
    # )
    
    print(f"Using MCP Server: {example_server.name}")
    print(f"Description: {example_server.description}")
    print(f"URL: {example_server.url}")
    print(f"Capabilities: {example_server.capabilities}")
    print()
    
    # Create an example agent
    analyst = MCPAgentBuilder.create_agent(
        role="Example Analyst",
        goal="Demonstrate the usage of MCP tools",
        backstory="""
            You are an expert in using MCP server tools.
            Your job is to demonstrate how to use the available tools effectively.
        """,
        verbose=True
    )
    
    # Create a task
    demo_task = Task(
        description="""
            Use the available MCP tools to perform a simple demonstration.
            Show what the tools can do and provide a summary.
        """,
        expected_output="""
            A demonstration report showing the capabilities of the MCP tools.
        """,
        agent=analyst
    )
    
    print("Note: This is a template example. To run actual MCP tools:")
    print("1. Ensure an MCP server is running at the specified URL")
    print("2. Get the server configuration from the registry or config")
    print("3. Create agents and tasks specific to your use case")
    print("4. Run with: run_with_mcp_tools([task], mcp_server)")
    print("=" * 80) 