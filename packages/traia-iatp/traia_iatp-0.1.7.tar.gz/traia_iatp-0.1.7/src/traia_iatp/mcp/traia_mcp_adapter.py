#!/usr/bin/env python
"""
Traia MCP Adapter

A custom MCP adapter that extends CrewAI's MCPServerAdapter to support
passing headers (like Authorization) to streamable-http MCP servers.

This adapter transparently handles both authenticated and non-authenticated
MCP connections by injecting headers when provided.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import httpx
from functools import wraps

from crewai_tools import MCPServerAdapter
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class TraiaMCPAdapter(MCPServerAdapter):
    """
    MCP adapter that supports custom headers for streamable-http transport.
    
    This adapter extracts headers from server_params and injects them into
    all HTTP requests made to the MCP server. It works transparently for
    both authenticated and non-authenticated connections.
    
    Example:
        ```python
        # With authentication headers
        server_params = {
            "url": "https://mcp.example.com/mcp",
            "transport": "streamable-http",
            "headers": {"Authorization": "Bearer YOUR_API_KEY"}
        }
        
        # Without headers (standard connection)
        server_params = {
            "url": "https://mcp.example.com/mcp",
            "transport": "streamable-http"
        }
        
        with TraiaMCPAdapter(server_params) as tools:
            # Use tools with or without authentication
            agent = Agent(tools=tools)
        ```
    """
    
    def __init__(
        self,
        server_params: Union[Dict[str, Any], Any],
        *tool_names: str
    ):
        """
        Initialize the adapter with optional header support.
        
        Args:
            server_params: Server configuration. For streamable-http, can include:
                          - url: The MCP server URL
                          - transport: "streamable-http"
                          - headers: Optional dict of headers to include in requests
            *tool_names: Optional tool names to filter
        """
        # Handle dict params
        if isinstance(server_params, dict):
            # Extract headers if present (don't modify original)
            server_params_copy = server_params.copy()
            self._auth_headers = server_params_copy.pop("headers", {})
            
            if self._auth_headers:
                logger.info(f"TraiaMCPAdapter: Headers configured: {list(self._auth_headers.keys())}")
                # Apply monkey patch before parent initialization
                self._apply_httpx_patch()
            
            # Pass clean params to parent
            super().__init__(server_params_copy, *tool_names)
        else:
            # Non-dict params, no headers possible
            self._auth_headers = {}
            super().__init__(server_params, *tool_names)
    
    def _apply_httpx_patch(self):
        """Monkey-patch httpx.AsyncClient to inject headers."""
        original_init = httpx.AsyncClient.__init__
        auth_headers = self._auth_headers
        
        @wraps(original_init)
        def patched_init(client_self, *args, **kwargs):
            # Get existing headers
            existing_headers = kwargs.get('headers', {})
            if isinstance(existing_headers, dict):
                # Merge our headers
                merged_headers = {**auth_headers, **existing_headers}
                kwargs['headers'] = merged_headers
                logger.debug(f"Injected headers into httpx.AsyncClient: {list(auth_headers.keys())}")
            
            # Also ensure headers are preserved on redirects
            if 'follow_redirects' not in kwargs:
                kwargs['follow_redirects'] = True
            
            # Call original init
            original_init(client_self, *args, **kwargs)
        
        # Apply the patch
        httpx.AsyncClient.__init__ = patched_init
        self._original_httpx_init = original_init
        logger.debug("Applied httpx.AsyncClient monkey patch")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and restore original httpx if patched."""
        # Restore original httpx.AsyncClient.__init__ if we patched it
        if hasattr(self, '_original_httpx_init'):
            httpx.AsyncClient.__init__ = self._original_httpx_init
            logger.debug("Restored original httpx.AsyncClient")
        
        # Call parent exit
        return super().__exit__(exc_type, exc_val, exc_tb)
    
    def __enter__(self) -> List[BaseTool]:
        """Enter context manager."""
        if self._auth_headers:
            logger.debug(f"TraiaMCPAdapter: Using authenticated connection")
        
        return super().__enter__()


def create_mcp_adapter(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    transport: str = "streamable-http",
    tool_names: Optional[List[str]] = None
) -> TraiaMCPAdapter:
    """
    Create a Traia MCP adapter with optional headers.
    
    Args:
        url: MCP server URL
        headers: Optional dictionary of headers to include in requests
        transport: Transport type (default: streamable-http)
        tool_names: Optional list of tool names to filter
    
    Returns:
        TraiaMCPAdapter configured with or without headers
    
    Example:
        ```python
        # With headers
        adapter = create_mcp_adapter(
            url="https://news-mcp.example.com/mcp",
            headers={"Authorization": "Bearer YOUR_API_KEY"}
        )
        
        # Without headers
        adapter = create_mcp_adapter(
            url="https://news-mcp.example.com/mcp"
        )
        
        with adapter as tools:
            agent = Agent(tools=tools)
        ```
    """
    server_params = {
        "url": url,
        "transport": transport
    }
    
    if headers:
        server_params["headers"] = headers
    
    if tool_names:
        return TraiaMCPAdapter(server_params, *tool_names)
    else:
        return TraiaMCPAdapter(server_params)


def create_mcp_adapter_with_auth(
    url: str,
    api_key: str,
    auth_header: str = "Authorization",
    auth_prefix: str = "Bearer",
    transport: str = "streamable-http",
    tool_names: Optional[List[str]] = None
) -> TraiaMCPAdapter:
    """
    Create a Traia MCP adapter with authentication.
    
    Args:
        url: MCP server URL
        api_key: API key for authentication
        auth_header: Header name for auth (default: Authorization)
        auth_prefix: Auth scheme prefix (default: Bearer)
        transport: Transport type (default: streamable-http)
        tool_names: Optional list of tool names to filter
    
    Returns:
        TraiaMCPAdapter configured with auth headers
    
    Example:
        ```python
        adapter = create_mcp_adapter_with_auth(
            url="https://news-mcp.example.com/mcp",
            api_key="your-api-key"
        )
        
        with adapter as tools:
            # Tools will include Authorization header in all requests
            agent = Agent(tools=tools)
        ```
    """
    headers = {}
    if auth_prefix:
        headers[auth_header] = f"{auth_prefix} {api_key}"
    else:
        headers[auth_header] = api_key
    
    return create_mcp_adapter(url, headers, transport, tool_names)


# Backwards compatibility aliases
HeaderMCPAdapter = TraiaMCPAdapter
create_mcp_adapter_with_headers = create_mcp_adapter


# Usage examples
USAGE_GUIDE = """
TraiaMCPAdapter Usage Guide
==========================

The TraiaMCPAdapter seamlessly handles both authenticated and non-authenticated
MCP connections. It extracts headers from server_params and injects them into
all HTTP requests when using streamable-http transport.

Basic Usage
-----------
```python
from traia_iatp.mcp import TraiaMCPAdapter

# Standard connection (no authentication)
server_params = {
    "url": "http://localhost:8000/mcp",
    "transport": "streamable-http"
}

# Authenticated connection
server_params = {
    "url": "http://localhost:8000/mcp",
    "transport": "streamable-http",
    "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
    }
}

# Use the same way regardless of authentication
with TraiaMCPAdapter(server_params) as tools:
    agent = Agent(
        role="My Agent",
        tools=tools
    )
```

Using Helper Functions
----------------------
```python
from traia_iatp.mcp import create_mcp_adapter_with_auth

# Create authenticated adapter
adapter = create_mcp_adapter_with_auth(
    url="http://localhost:8000/mcp",
    api_key="your-api-key"
)

with adapter as tools:
    # Use authenticated tools
    pass
```

Multiple Headers
----------------
```python
adapter = create_mcp_adapter(
    url="http://localhost:8000/mcp",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "X-API-Version": "v1",
        "X-Client-ID": "my-client"
    }
)
```

With Tool Filtering
-------------------
```python
adapter = create_mcp_adapter_with_auth(
    url="http://localhost:8000/mcp",
    api_key="your-api-key",
    tool_names=["search_news", "get_api_info"]
)
```

Server-Side Authentication
--------------------------
For MCP servers that require authentication, implement FastMCP middleware:

```python
from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request, get_context
from starlette.requests import Request

class AuthMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        try:
            # Access the raw HTTP request
            request: Request = get_http_request()
            
            # Extract bearer token from Authorization header
            auth = request.headers.get("Authorization", "")
            token = auth[7:].strip() if auth.lower().startswith("bearer ") else None
            
            if not token:
                # Check X-API-KEY header as alternative
                token = request.headers.get("X-API-KEY", "")
            
            if token:
                # Store the API key in the context state
                if hasattr(context, 'state'):
                    context.state.api_key = token
                else:
                    # Try to store it in the request state as fallback
                    request.state.api_key = token
        except Exception as e:
            logger.debug(f"Could not extract API key from request: {e}")
        
        return await call_next(context)

mcp = FastMCP("My Server", middleware=[AuthMiddleware()])

def get_session_api_key(context: Context) -> Optional[str]:
    '''Get the API key for the current session.'''
    try:
        # Try to get the API key from the context state
        if hasattr(context, 'state') and hasattr(context.state, 'api_key'):
            return context.state.api_key
        
        # Fallback: try to get it from the current HTTP request
        try:
            request: Request = get_http_request()
            if hasattr(request.state, 'api_key'):
                return request.state.api_key
        except Exception:
            pass
        
        # If we're in a tool context, try to get the context using the dependency
        try:
            ctx = get_context()
            if hasattr(ctx, 'state') and hasattr(ctx.state, 'api_key'):
                return ctx.state.api_key
        except Exception:
            pass
    except Exception as e:
        logger.debug(f"Could not retrieve API key from context: {e}")
    
    return None
```

Note: Headers are only applicable for streamable-http transport.
For stdio or SSE transports, authentication must be handled differently.
"""


__all__ = [
    'TraiaMCPAdapter',
    'HeaderMCPAdapter',  # Alias for backward compatibility
    'create_mcp_adapter',
    'create_mcp_adapter_with_auth',
    'create_mcp_adapter_with_headers',  # Alias
    'USAGE_GUIDE'
] 