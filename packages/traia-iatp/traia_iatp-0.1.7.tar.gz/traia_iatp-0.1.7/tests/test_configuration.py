"""Test basic configuration and imports."""

import pytest
from unittest.mock import Mock, AsyncMock
from traia_iatp.core.models import MCPServer, UtilityAgent


def test_package_imports():
    """Test that the main package components can be imported."""
    # Test core imports
    from traia_iatp.core.models import MCPServer, MCPServerType, UtilityAgent
    from traia_iatp.client import A2AToolSchema
    from traia_iatp.registry import find_utility_agent, list_utility_agents
    from traia_iatp.server import IATPServerAgentGenerator
    from traia_iatp.mcp import MCPServerConfig, MCPAgentBuilder
    
    assert MCPServer is not None
    assert A2AToolSchema is not None
    assert find_utility_agent is not None
    assert IATPServerAgentGenerator is not None
    assert MCPServerConfig is not None


def test_mock_mcp_server_fixture(mock_mcp_server):
    """Test that the mock MCP server fixture works."""
    assert mock_mcp_server is not None
    assert mock_mcp_server.name == "test-mcp-server"
    assert mock_mcp_server.url == "http://localhost:8000/mcp"
    assert mock_mcp_server.description == "Test MCP server for unit tests"


def test_mock_utility_agent_fixture(mock_utility_agent):
    """Test that the mock utility agent fixture works."""
    assert mock_utility_agent is not None
    assert mock_utility_agent.name == "test-utility-agent"
    assert mock_utility_agent.description == "Test utility agent for unit tests"
    assert "test" in mock_utility_agent.capabilities
    assert "mock" in mock_utility_agent.capabilities


def test_mock_mongodb_client_fixture(mock_mongodb_client):
    """Test that the mock MongoDB client fixture works."""
    assert mock_mongodb_client is not None
    
    # Test that the mock has the expected structure
    database = mock_mongodb_client["test_db"]
    collection = database["test_collection"]
    
    assert database is not None
    assert collection is not None


def test_mock_a2a_client_fixture(mock_a2a_client):
    """Test that the mock A2A client fixture works."""
    assert mock_a2a_client is not None
    assert hasattr(mock_a2a_client, 'send_message')
    assert hasattr(mock_a2a_client, 'get_task')
    
    # Test that it's properly mocked
    assert isinstance(mock_a2a_client.send_message, AsyncMock)
    assert isinstance(mock_a2a_client.get_task, AsyncMock)


def test_sample_registry_entry_fixture(sample_registry_entry):
    """Test that the sample registry entry fixture works."""
    assert sample_registry_entry is not None
    assert sample_registry_entry.name == "sample-utility-agent"
    assert sample_registry_entry.description == "Sample utility agent for testing"
    assert "trading" in sample_registry_entry.capabilities
    assert "analysis" in sample_registry_entry.capabilities
    # Note: UtilityAgentRegistryEntry has base_url field, not endpoint
    assert sample_registry_entry.base_url is None  # Fixed: check correct field
    assert sample_registry_entry.agent_card is not None
    assert sample_registry_entry.agent_card.name == "sample-agent"


@pytest.mark.asyncio
async def test_async_functionality():
    """Test that async functionality works in the test environment."""
    import asyncio
    
    # Simple async test
    async def async_function():
        await asyncio.sleep(0.001)  # Very short delay
        return "async works"
    
    result = await async_function()
    assert result == "async works"


def test_core_models():
    """Test that core models can be instantiated."""
    from traia_iatp.core.models import MCPServer, MCPServerType
    
    # Test creating an MCP server
    mcp_server = MCPServer(
        name="test-server",
        url="http://localhost:8000",
        server_type=MCPServerType.STREAMABLE_HTTP,
        description="Test server"
    )
    
    assert mcp_server.name == "test-server"
    assert mcp_server.url == "http://localhost:8000"
    assert mcp_server.server_type == MCPServerType.STREAMABLE_HTTP


def test_a2a_tool_schema():
    """Test that A2A tool schema can be instantiated."""
    from traia_iatp.client.crewai_a2a_tools import A2AToolSchema
    
    schema = A2AToolSchema(request="test request")
    assert schema.request == "test request"


def test_environment_setup():
    """Test that the test environment is properly set up."""
    import sys
    import os
    
    # Check that we're in the correct environment
    assert sys.version_info >= (3, 12)
    
    # Check that we can access the package
    import traia_iatp
    assert traia_iatp is not None
    
    # Check that we're in a virtual environment
    assert hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) 