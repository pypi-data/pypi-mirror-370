# Traia IATP

[![PyPI version](https://badge.fury.io/py/traia-iatp.svg)](https://badge.fury.io/py/traia-iatp)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Traia IATP** is an Inter-Agent Transfer Protocol (IATP) package that enables AI agents to utilize other AI agents as tools via the A2A (Agent-to-Agent) protocol. This implementation allows CrewAI agents to act as both IATP servers (utility agents) and clients.

## Features

- 🤖 **Utility Agent Creation**: Convert MCP servers into IATP-compatible utility agents
- 🔌 **IATP Client Tools**: Enable CrewAI crews to use utility agents as tools via IATP protocol
- 🌐 **Protocol Support**: HTTP/2 with SSE streaming and optional gRPC for high-performance scenarios
- 📊 **Registry Management**: MongoDB-based registry for discovering utility agents
- 🐳 **Docker Support**: Complete containerization for deployment
- 🐳 **Local Docker Deployment**: Complete containerization for local deployment

## Installation

### From PyPI (Recommended)

```bash
pip install traia-iatp
```

### From Source

```bash
git clone https://github.com/Traia-IO/IATP.git
cd IATP
pip install -e .
```

### Development Installation

```bash
# Install with all dependencies for development
pip install -e ".[dev]"
```

## Quick Start

### 1. Creating a Utility Agency (IATP Server)

```python
import asyncio
from traia_iatp import MCPServer, MCPServerType, IATPServerAgentGenerator

async def create_utility_agency():
    # Define an MCP server
    mcp_server = MCPServer(
        name="example-mcp-server",
        url="http://example-mcp-server:8080",
        server_type=MCPServerType.STREAMABLE_HTTP,
        description="Example MCP server that provides utility functions"
    )
    
    # Generate and deploy utility agency
    generator = IATPServerAgentGenerator()
    agency = await generator.create_from_mcp(mcp_server)
    
    # Deploy locally with Docker
    await generator.deploy_local(agency)
```

### 2. Using Utility Agencies in CrewAI (IATP Client)

```python
from crewai import Agent, Task, Crew
from traia_iatp import find_utility_agent
from traia_iatp.client import A2AToolkit

# Find available utility agents by agent_id
agent = find_utility_agent(agent_id="finbert-mcp-traia-utility-agent")

if agent:
    # Get the IATP endpoint
    endpoint = agent.base_url
    if agent.endpoints and 'iatp_endpoint' in agent.endpoints:
        endpoint = agent.endpoints['iatp_endpoint']
    
    # Create tool from agent endpoint
    finbert_tool = A2AToolkit.create_tool_from_endpoint(
        endpoint=endpoint,
        name=agent.name,
        description=agent.description,
        timeout=300,
        retry_attempts=1,
        supports_streaming=False,
        iatp_endpoint=endpoint
    )
    
    # Use in CrewAI agent
    sentiment_analyst = Agent(
        role="Financial Sentiment Analyst",
        goal="Analyze sentiment of financial texts using FinBERT models",
        backstory="Expert financial sentiment analyst with deep knowledge of market psychology",
        tools=[finbert_tool],
        verbose=True,
        allow_delegation=False
    )
    
    # Create task
    task = Task(
        description="Analyze the sentiment of: 'Apple Inc. reported record quarterly earnings'",
        expected_output="Sentiment classification with confidence score and investment implications",
        agent=sentiment_analyst
    )
    
    # Run crew
    crew = Crew(agents=[sentiment_analyst], tasks=[task])
    result = crew.kickoff()
```

#### Alternative: Batch Tool Creation

For creating multiple tools at once, you can use the convenience function:

```python
from traia_iatp.client import create_utility_agency_tools

# Search and create tools in batch
tools = create_utility_agency_tools(
    query="sentiment analysis",
    tags=["finbert", "nlp"],
    capabilities=["sentiment_analysis"]
)

# Use all found tools in an agent
agent = Agent(
    role="Multi-Tool Analyst",
    tools=tools,
    goal="Analyze using multiple available utility agents"
)
```

### 3. CLI Usage

The package includes a powerful CLI for managing utility agencies:

```bash
# First, register an MCP server in the registry
traia-iatp register-mcp \
    --name "Trading MCP" \
    --url "http://localhost:8000/mcp" \
    --description "Trading MCP server" \
    --capability "trading" \
    --capability "crypto"

# Create a utility agency from registered MCP server
traia-iatp create-agency \
    --name "My Trading Agent" \
    --description "Advanced trading utility agent" \
    --mcp-name "Trading MCP" \
    --deploy

# List available utility agencies
traia-iatp list-agencies

# Search for agencies by capability
traia-iatp search-agencies --query "trading crypto"

# Deploy from a generated agency directory
traia-iatp deploy ./utility_agencies/my-trading-agent --port 8001

# Find available tools for CrewAI
traia-iatp find-tools --tag "trading" --capability "crypto"

# List registered MCP servers
traia-iatp list-mcp-servers

# Show example CrewAI integration code
traia-iatp example-crew
```

## Architecture

### IATP Operation Modes

The IATP protocol supports two distinct operation modes:

#### 1. Synchronous JSON-RPC Mode
For simple request-response patterns:
- Client sends: `message/send` request via JSON-RPC
- Server processes the request using CrewAI agents  
- Server returns: A single `Message` result

#### 2. Streaming SSE Mode
For real-time data and long-running operations:
- Client sends: `message/send` request via JSON-RPC
- Server returns: Stream of events via Server-Sent Events (SSE)
- Supports progress updates, partial results, and completion notifications

### Component Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   CrewAI Agent      │───▶│   IATP Client       │───▶│   Utility Agency    │
│   (A2A Client)      │    │   (HTTP/2 + gRPC)   │    │   (A2A Server)      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────────┐
                                                       │   MCP Server        │
                                                       │   (Tools Provider)  │
                                                       └─────────────────────┘
```

## Key Components

### Server Components (`traia_iatp.server`)
- **Template Generation**: Jinja2 templates for creating utility agents
- **HTTP/2 + SSE Support**: Modern protocol support with streaming
- **gRPC Integration**: Optional high-performance protocol support
- **Docker Containerization**: Complete deployment packaging

### Client Components (`traia_iatp.client`)
- **CrewAI Integration**: Native tools for CrewAI agents
- **HTTP/2 Client**: Persistent connections with multiplexing
- **SSE Streaming**: Real-time data consumption
- **Connection Management**: Pooling and retry logic

### Registry Components (`traia_iatp.registry`)
- **MongoDB Integration**: Persistent storage and search
- **Vector Search**: Embedding-based capability discovery
- **Atlas Search**: Full-text search capabilities
- **Agent Discovery**: Find agents by capability, tags, or description

## Environment Variables

```bash
# MongoDB Configuration (choose one method)
MONGODB_CONNECTION_STRING="mongodb+srv://..."
# OR
MONGODB_USER="username"
MONGODB_PASSWORD="password"
# OR X.509 Certificate
MONGODB_X509_CERT_FILE="/path/to/cert.pem"

# Optional: Custom MongoDB cluster
MONGODB_CLUSTER_URI="custom-cluster.mongodb.net"
MONGODB_DATABASE_NAME="custom_db"

# OpenAI for embeddings (optional)
OPENAI_API_KEY="your-openai-key"

# MCP Server Authentication (as needed)
MCP_API_KEY="your-mcp-api-key"
```

## Examples

### Advanced IATP Integration

```python
from traia_iatp import find_utility_agent
from traia_iatp.client import A2AToolkit

# Find multiple utility agents
trading_agent = find_utility_agent(agent_id="trading-mcp-agent")
sentiment_agent = find_utility_agent(agent_id="finbert-mcp-agent") 

tools = []
for agent in [trading_agent, sentiment_agent]:
    if agent:
        # Get endpoint and create tool
        endpoint = agent.endpoints.get('iatp_endpoint', agent.base_url)
        tool = A2AToolkit.create_tool_from_endpoint(
            endpoint=endpoint,
            name=agent.name,
            description=agent.description,
            iatp_endpoint=endpoint
        )
        tools.append(tool)

# Use multiple IATP tools in one agent
multi_tool_agent = Agent(
    role="Multi-Domain Analyst", 
    goal="Analyze markets using multiple specialized AI agents",
    tools=tools,
    backstory="Expert analyst with access to specialized AI agents for trading and sentiment analysis"
)
```

### Local Docker Deployment

```python
from traia_iatp.utils.docker_utils import LocalDockerRunner
from pathlib import Path

# Deploy a generated agency locally (not yet configured properly)
runner = LocalDockerRunner()
deployment_info = await runner.run_agent_docker(
    agent_path=Path("./utility_agencies/my-trading-agent"),
    port=8000,
    detached=True
)

if deployment_info["success"]:
    print(f"Agency deployed at: {deployment_info['iatp_endpoint']}")
    print(f"Container: {deployment_info['container_name']}")
    print(f"Stop with: {deployment_info['stop_command']}")
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Traia-IO/IATP.git
cd IATP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run with coverage
pytest --cov=traia_iatp --cov-report=html
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

This is a private code base hence only members of Dcentralab can contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: [https://pypi.org/project/traia-iatp](https://pypi.org/project/traia-iatp)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Traia-IO/IATP/issues)
- 💬 **Community**: [Visit our website](https://traia.io)
- 📧 **Email**: support@traia.io

## Related Projects

- [A2A Protocol](https://github.com/google-a2a/A2A) - Agent-to-Agent communication protocol
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Framework for orchestrating role-playing AI agents
- [FastMCP](https://github.com/modelcontextprotocol/fastmcp) - Fast implementation of Model Context Protocol

---

**Made with ❤️ by the Traia Team** 