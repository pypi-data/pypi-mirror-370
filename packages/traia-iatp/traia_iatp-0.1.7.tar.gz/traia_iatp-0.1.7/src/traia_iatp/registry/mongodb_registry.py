"""MongoDB registry for utility agents and MCP servers (write operations only).

This module handles all write operations for the IATP registry:
- Adding utility agents and MCP servers
- Updating agent information and health status
- Managing agent lifecycle (activation/deactivation)
- Registry statistics

For search and query operations, use iatp_search_api.py instead.
"""

import logging
import time
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo import server_api
from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect
from pymongo.database import Database
from pymongo.collection import Collection
import os

# Handle imports for both module and script usage
if __name__ == "__main__":
    # When running as a script, import directly
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.traia_iatp.core.models import UtilityAgentRegistryEntry, UtilityAgent
    from src.traia_iatp.registry.embeddings import get_embedding_service
    from ..utils import get_now_in_utc
else:
    # When imported as a module
    from ..core.models import UtilityAgentRegistryEntry, UtilityAgent
    from .embeddings import get_embedding_service
    from ..utils import get_now_in_utc

logger = logging.getLogger(__name__)

CLUSTER_URI = "traia-iatp-cluster.yzwjvgd.mongodb.net/?retryWrites=true&w=majority&appName=Traia-IATP-Cluster"
DATABASE_NAME = "iatp"


def get_collection_names():
    """Get environment-specific collection names."""
    env = os.getenv("ENV", "test").lower()
    
    # Validate environment
    valid_envs = ["test", "staging", "prod"]
    if env not in valid_envs:
        logger.warning(f"Invalid ENV '{env}', defaulting to 'test'. Valid values: {valid_envs}")
        env = "test"
    
    return {
        "utility_agent": f"iatp-utility-agent-registry-{env}",
        "mcp_server": f"iatp-mcp-server-registry-{env}"
    }


def get_search_index_names():
    """Get environment-specific search index names."""
    env = os.getenv("ENV", "test").lower()
    
    # Validate environment
    valid_envs = ["test", "staging", "prod"]
    if env not in valid_envs:
        env = "test"
    
    return {
        "utility_agent_atlas_search": f"utility_agent_atlas_search_{env}",
        "utility_agent_vector_search": f"utility_agent_vector_search_{env}",
        "mcp_server_atlas_search": f"mcp_server_atlas_search_{env}",
        "mcp_server_vector_search": f"mcp_server_vector_search_{env}"
    }


def _create_mongodb_client_with_retry(connection_string: str, max_retries: int = 3) -> MongoClient:
    """Create MongoDB client with retry logic for connection resilience."""
    for attempt in range(max_retries):
        try:
            client = MongoClient(
                connection_string,
                server_api=server_api.ServerApi('1'),
                serverSelectionTimeoutMS=15000,  # 15 second timeout
                connectTimeoutMS=10000,          # 10 second connect timeout
                socketTimeoutMS=30000,           # 30 second socket timeout
                maxPoolSize=10,                  # Connection pool size
                retryWrites=True                 # Enable retryable writes
            )
            # Test the connection
            client.admin.command('ping')
            logger.info(f"MongoDB connection established successfully (attempt {attempt + 1})")
            return client
        except (ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect, Exception) as e:
            error_msg = str(e).lower()
            is_connection_error = any(term in error_msg for term in ['ssl', 'tls', 'handshake', 'timeout', 'network'])
            
            if attempt < max_retries - 1 and is_connection_error:
                delay = (2 ** attempt) + (attempt * 0.5)  # Exponential backoff with jitter
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                logger.info(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} MongoDB connection attempts failed")
                raise


class UtilityAgentRegistry:
    """Cloud MongoDB-based registry for utility agents (write operations only).
    
    This class handles all write operations for utility agents:
    - Adding new agents to the registry
    - Updating agent information and health status
    - Managing agent lifecycle
    - Registry statistics
    
    For search and query operations, use iatp_search_api.py instead.
    """
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = DATABASE_NAME):
        """Initialize MongoDB registry for cloud usage.
        
        Args:
            connection_string: MongoDB connection string (should be a cloud MongoDB URI)
            database_name: Name of the database to use
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            # Try X.509 certificate authentication first
            cert_file = os.getenv("MONGODB_X509_CERT_FILE")
            if cert_file and os.path.exists(cert_file):
                # For X.509 authentication, we need to extract the subject from the certificate
                # to use as the username. MongoDB Atlas typically uses the full DN as username.
                # The connection string format for X.509 is:
                # mongodb+srv://cluster.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509
                # Extract just the cluster hostname without query parameters
                cluster_host = CLUSTER_URI.split('?')[0]
                self.connection_string = f"mongodb+srv://{cluster_host}?authSource=$external&authMechanism=MONGODB-X509&tls=true&tlsCertificateKeyFile={cert_file}"
                logger.info(f"Using X.509 certificate authentication from {cert_file}")
            else:
                # Fallback to username/password authentication
                user = os.getenv("MONGODB_USER")
                password = os.getenv("MONGODB_PASSWORD")
                if user and password:
                    self.connection_string = f"mongodb+srv://{user}:{password}@{CLUSTER_URI}"
                    logger.info("Using username/password authentication")
                else:
                    # Try connection string as last resort
                    self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
                    if not self.connection_string:
                        raise ValueError(
                            "MongoDB authentication required. Please provide either:\n"
                            "1. MONGODB_X509_CERT_FILE - Path to X.509 certificate file\n"
                            "2. MONGODB_USER and MONGODB_PASSWORD - Username and password\n"
                            "3. MONGODB_CONNECTION_STRING - Full connection string"
                        )
        
        self.database_name = database_name
        self.client = _create_mongodb_client_with_retry(self.connection_string)
        self.db: Database = self.client[self.database_name]
        
        # Get environment-specific collection name
        collection_names = get_collection_names()
        self.registry: Collection = self.db[collection_names["utility_agent"]]
        logger.info(f"Using collection: {collection_names['utility_agent']}")
        
        # Create indexes for efficient searching (only if they don't exist)
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure indexes exist for efficient searching."""
        existing_indexes = [idx['name'] for idx in self.registry.list_indexes()]
        
        # NOTE: Atlas Search and Vector Search indexes must be created through Atlas UI or API
        # See atlas_search_indexes.json and ATLAS_SEARCH_SETUP.md for instructions
        
        # Only create regular indexes (not text search)
        index_specs = [
            ("agent_id", "agent_id_index", True),  # unique
            ("name", "name_index", True),  # unique
            ("base_url", "base_url_index", True),  # unique - base URL is the primary endpoint
            ("is_active", "is_active_index", False),
            ("tags", "tags_index", False),
            ("capabilities", "capabilities_index", False),
            ([("registered_at", ASCENDING)], "registered_at_index", False)
        ]
        
        for spec, index_name, is_unique in index_specs:
            if index_name not in existing_indexes:
                try:
                    if isinstance(spec, list):
                        self.registry.create_index(spec, name=index_name)
                    else:
                        self.registry.create_index(spec, name=index_name, unique=is_unique)
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {e}")
    
    async def add_utility_agent(self, agent: UtilityAgent, tags: List[str] = None) -> UtilityAgentRegistryEntry:
        """Add a utility agent to the cloud registry.
        
        Args:
            agent: UtilityAgent object with endpoints configured
            tags: Optional additional tags for search
            
        Returns:
            UtilityAgentRegistryEntry created or updated
        """
        # Check if agent with same name already exists
        existing = self.registry.find_one({"name": agent.name})
        
        if existing:
            # Update the existing entry with the same name
            agent_id = existing["agent_id"]
            logger.warning(f"Agent with name '{agent.name}' already exists (ID: {agent_id}). Updating it.")
        else:
            agent_id = agent.id
        
        # Generate embeddings if enabled
        description_embedding = None
        tags_embedding = None
        capabilities_embedding = None
        agent_card_embedding = None
        search_text_embedding = None
        
        if os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true":
            try:
                embedding_service = get_embedding_service()
                
                # Generate embedding for description
                if agent.description:
                    description_embedding = await embedding_service.generate_embedding(agent.description)
                
                # Generate embedding for tags (concatenated)
                if tags or agent.tags:
                    all_tags = list(set((tags or []) + agent.tags))
                    tags_text = " ".join(all_tags)
                    tags_embedding = await embedding_service.generate_embedding(tags_text)
                
                # Generate embedding for capabilities
                if agent.capabilities:
                    capabilities_text = " ".join(agent.capabilities)
                    capabilities_embedding = await embedding_service.generate_embedding(capabilities_text)
                
                # Generate embedding for agent card
                if agent.agent_card:
                    # Create comprehensive agent card text
                    agent_card_parts = [
                        agent.agent_card.name,
                        agent.agent_card.description
                    ]
                    
                    # Add skills information
                    for skill in agent.agent_card.skills:
                        agent_card_parts.append(skill.name)
                        agent_card_parts.append(skill.description)
                        agent_card_parts.extend(skill.examples)
                        agent_card_parts.extend(skill.tags)
                    
                    agent_card_text = " ".join(filter(None, agent_card_parts))
                    agent_card_embedding = await embedding_service.generate_embedding(agent_card_text)
                
                # Note: We'll generate search text embedding after creating the entry
                    
                logger.info(f"Generated embeddings for agent {agent.name}")
            except Exception as e:
                logger.warning(f"Failed to generate embeddings: {e}. Proceeding without embeddings.")
        
        # Create entry with enhanced fields
        entry = UtilityAgentRegistryEntry(
            agent_id=agent_id,
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities,
            tags=tags or agent.tags,
            metadata=agent.metadata
        )
        
        # Add agent card if available
        if agent.agent_card:
            entry.agent_card = agent.agent_card
            entry.skills = agent.agent_card.skills
        
        # Add endpoints if available
        if agent.endpoints:
            entry.endpoints = agent.endpoints
            # Store base_url for indexing since all endpoints are derived from it
            entry.base_url = agent.endpoints.base_url
        
        # Generate search text from available data
        search_text_parts = [agent.name, agent.description]
        search_text_parts.extend(agent.capabilities)
        search_text_parts.extend(tags or agent.tags)
        
        # Add agent card information to search text
        if agent.agent_card:
            search_text_parts.append(agent.agent_card.name)
            search_text_parts.append(agent.agent_card.description)
            for skill in agent.agent_card.skills:
                search_text_parts.append(skill.name)
                search_text_parts.append(skill.description)
                search_text_parts.extend(skill.examples)
                search_text_parts.extend(skill.tags)
        
        # Set the generated search text
        entry.search_text = " ".join(filter(None, search_text_parts))
        
        # Generate embedding for the search text we just created
        if os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true" and entry.search_text:
            try:
                embedding_service = get_embedding_service()
                search_text_embedding = await embedding_service.generate_embedding(entry.search_text)
            except Exception as e:
                logger.warning(f"Failed to generate search text embedding: {e}")
        
        # Insert or update in cloud MongoDB
        # Convert to dict and ensure all values are JSON-serializable
        entry_dict = entry.model_dump(mode='json')
        
        # Add embeddings if available
        embeddings = {}
        if description_embedding:
            embeddings["description"] = description_embedding
        if tags_embedding:
            embeddings["tags"] = tags_embedding
        if capabilities_embedding:
            embeddings["capabilities"] = capabilities_embedding
        if agent_card_embedding:
            embeddings["agent_card"] = agent_card_embedding
        if search_text_embedding:
            embeddings["search_text"] = search_text_embedding
        
        if embeddings:
            entry_dict["embeddings"] = embeddings
        
        # Store the full UtilityAgent data as well
        agent_dict = agent.model_dump(mode='json')
        entry_dict["utility_agent_data"] = agent_dict
        
        result = self.registry.replace_one(
            {"agent_id": agent_id},  # Use agent_id as the key for upsert
            entry_dict,
            upsert=True
        )
        
        if result.upserted_id:
            logger.info(f"Added new agent {agent.name} (ID: {agent_id}) to cloud registry")
        else:
            logger.info(f"Updated existing agent {agent.name} (ID: {agent_id}) in cloud registry")
            
        return entry
    

    

    

    

    

    
    async def get_agent_by_id(self, agent_id: str) -> Optional[UtilityAgentRegistryEntry]:
        """Get a specific agent by ID from cloud registry."""
        doc = self.registry.find_one({"agent_id": agent_id})
        if doc:
            doc.pop("_id", None)
            return UtilityAgentRegistryEntry(**doc)
        return None
    
    async def update_health_status(self, agent_id: str, is_healthy: bool = True) -> bool:
        """Update health status of an agent in cloud registry."""
        update = {
            "$set": {
                "last_health_check": get_now_in_utc(),
                "is_active": is_healthy
            }
        }
        
        result = self.registry.update_one(
            {"agent_id": agent_id},
            update
        )
        return result.modified_count > 0
    
    async def update_agent_base_url(self, agent_id: str, new_base_url: str) -> bool:
        """Update the base URL for an agent.
        
        This will also update the endpoints configuration with new derived URLs.
        
        Args:
            agent_id: ID of the agent to update
            new_base_url: New base URL for the agent
            
        Returns:
            True if update was successful
        """
        # Fetch the current agent to get streaming configuration
        doc = self.registry.find_one({"agent_id": agent_id})
        if not doc:
            return False
            
        # Create new endpoints based on the new base URL
        from ..utils.iatp_utils import create_iatp_endpoints
        supports_streaming = doc.get("endpoints", {}).get("streaming_endpoint") is not None
        new_endpoints = create_iatp_endpoints(new_base_url, supports_streaming)
        
        result = self.registry.update_one(
            {"agent_id": agent_id},
            {"$set": {
                "base_url": new_base_url, 
                "endpoints": new_endpoints.model_dump(mode='json'),
                "updated_at": get_now_in_utc()
            }}
        )
        return result.modified_count > 0
    
    async def add_tags(self, agent_id: str, tags: List[str]) -> bool:
        """Add tags to an agent."""
        result = self.registry.update_one(
            {"agent_id": agent_id},
            {"$addToSet": {"tags": {"$each": tags}}}
        )
        return result.modified_count > 0
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry (soft delete by deactivating)."""
        result = self.registry.update_one(
            {"agent_id": agent_id},
            {"$set": {"is_active": False, "deactivated_at": get_now_in_utc()}}
        )
        return result.modified_count > 0
    
    async def update_utility_agent(self, agent_id: str, update_data: Dict[str, Any]) -> bool:
        """Update utility agent data in the registry.
        
        Args:
            agent_id: The ID of the agent to update
            update_data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = get_now_in_utc()
        
        result = self.registry.update_one(
            {"agent_id": agent_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated utility agent {agent_id} with {len(update_data)} fields")
            return True
        else:
            logger.warning(f"No utility agent found with ID {agent_id} or no changes made")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_agents = self.registry.count_documents({})
        active_agents = self.registry.count_documents({"is_active": True})
        
        # Get capability distribution
        pipeline = [
            {"$match": {"is_active": True}},
            {"$unwind": "$capabilities"},
            {"$group": {"_id": "$capabilities", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        capability_dist = list(self.registry.aggregate(pipeline))
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "top_capabilities": [{"capability": item["_id"], "count": item["count"]} for item in capability_dist]
        }
    
    def close(self):
        """Close the MongoDB connection."""
        self.client.close()


class MCPServerRegistry:
    """Registry for MCP servers in cloud MongoDB (write operations only).
    
    This class handles all write operations for MCP servers:
    - Adding new MCP servers to the registry
    - Updating server information
    - Managing server lifecycle
    
    For search and query operations, use iatp_search_api.py instead.
    """
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "iatp"):
        """Initialize MCP Server registry."""
        if connection_string:
            self.connection_string = connection_string
        else:
            # Try X.509 certificate authentication first
            cert_file = os.getenv("MONGODB_X509_CERT_FILE")
            if cert_file and os.path.exists(cert_file):
                # For X.509 authentication, we need to extract the subject from the certificate
                # to use as the username. MongoDB Atlas typically uses the full DN as username.
                # The connection string format for X.509 is:
                # mongodb+srv://cluster.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509
                # Extract just the cluster hostname without query parameters
                cluster_host = CLUSTER_URI.split('?')[0]
                self.connection_string = f"mongodb+srv://{cluster_host}?authSource=$external&authMechanism=MONGODB-X509&tls=true&tlsCertificateKeyFile={cert_file}"
                logger.info(f"Using X.509 certificate authentication from {cert_file}")
            else:
                # Fallback to username/password authentication
                user = os.getenv("MONGODB_USER")
                password = os.getenv("MONGODB_PASSWORD")
                if user and password:
                    self.connection_string = f"mongodb+srv://{user}:{password}@{CLUSTER_URI}"
                    logger.info("Using username/password authentication")
                else:
                    # Try connection string as last resort
                    self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
                    if not self.connection_string:
                        raise ValueError(
                            "MongoDB authentication required. Please provide either:\n"
                            "1. MONGODB_X509_CERT_FILE - Path to X.509 certificate file\n"
                            "2. MONGODB_USER and MONGODB_PASSWORD - Username and password\n"
                            "3. MONGODB_CONNECTION_STRING - Full connection string"
                        )
        
        self.client = _create_mongodb_client_with_retry(self.connection_string)
        self.db: Database = self.client[database_name]
        
        # Get environment-specific collection name
        collection_names = get_collection_names()
        self.collection: Collection = self.db[collection_names["mcp_server"]]
        logger.info(f"Using collection: {collection_names['mcp_server']}")
        
        # Ensure indexes
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure indexes exist."""
        existing_indexes = [idx['name'] for idx in self.collection.list_indexes()]
        
        # NOTE: Atlas Search and Vector Search indexes must be created through Atlas UI or API
        # See atlas_search_indexes.json and ATLAS_SEARCH_SETUP.md for instructions
        
        # Only create regular indexes (not text search)
        if 'name_index' not in existing_indexes:
            self.collection.create_index("name", unique=True, name='name_index')
    
    async def add_mcp_server(
        self,
        name: str,
        url: str,
        description: str,
        server_type: str = "streamable-http",
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add an MCP server to the registry with retry logic."""
        # Generate embeddings if enabled
        description_embedding = None
        capabilities_embedding = None
        
        if os.getenv("ENABLE_EMBEDDINGS", "true").lower() == "true":
            try:
                embedding_service = get_embedding_service()
                
                # Generate embedding for description
                if description:
                    description_embedding = await embedding_service.generate_embedding(description)
                
                # Generate embedding for capabilities (concatenated)
                if capabilities:
                    capabilities_text = " ".join(capabilities)
                    capabilities_embedding = await embedding_service.generate_embedding(capabilities_text)
                    
                logger.info(f"Generated embeddings for MCP server {name}")
            except Exception as e:
                logger.warning(f"Failed to generate embeddings: {e}. Proceeding without embeddings.")
        
        doc = {
            "name": name,
            "url": url,
            "description": description,
            "server_type": server_type,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "registered_at": get_now_in_utc(),
            "is_active": True
        }
        
        # Add embeddings if available
        if description_embedding:
            doc["description_embedding"] = description_embedding
        if capabilities_embedding:
            doc["capabilities_embedding"] = capabilities_embedding
        
        # Retry database operation with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Upsert by name
                result = self.collection.replace_one(
                    {"name": name},
                    doc,
                    upsert=True
                )
                
                if result.upserted_id:
                    logger.info(f"Added new MCP server {name} to registry")
                else:
                    logger.info(f"Updated existing MCP server {name} in registry")
                    
                return str(result.upserted_id or result.matched_count)
                
            except (ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect, Exception) as e:
                error_msg = str(e).lower()
                is_retryable = any(term in error_msg for term in ['ssl', 'tls', 'handshake', 'timeout', 'network', 'connection'])
                
                if attempt < max_retries - 1 and is_retryable:
                    delay = (2 ** attempt) + (attempt * 0.2)  # Exponential backoff with jitter
                    logger.warning(f"Database operation attempt {attempt + 1} failed: {e}")
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Failed to add MCP server {name} after {max_retries} attempts")
                    raise
    

    

    

    

    
    async def get_mcp_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an MCP server by name."""
        doc = self.collection.find_one({"name": name})
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        return None
    
    def close(self):
        """Close the connection."""
        self.client.close()


if __name__ == "__main__":
    import asyncio
    import sys
    import uuid
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # No additional imports needed
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def test_registries():
        """Test both registries."""
        print("\n=== MongoDB Registry Test ===")
        print(f"Environment: {os.getenv('ENV', 'test')}")
        collection_names = get_collection_names()
        print(f"Collections: {collection_names}")
        
        # Test required environment variables
        if not os.getenv("MONGODB_READWRITE_CONNECTION_STRING"):
            if not os.getenv("MONGODB_USER") or not os.getenv("MONGODB_PASSWORD"):
                print("\nERROR: Please set MONGODB_READWRITE_CONNECTION_STRING or MONGODB_USER/PASSWORD environment variables")
                return
        
        # Test UtilityAgentRegistry
        print("\n--- Testing UtilityAgentRegistry ---")
        try:
            agent_registry = UtilityAgentRegistry()
            print(f"✓ Connected to MongoDB")
            print(f"✓ Using database: {agent_registry.database_name}")
            print(f"✓ Using collection: {collection_names['utility_agent']}")
            
            # Create test agent
            test_agent = UtilityAgent(
                id=str(uuid.uuid4()),
                name="Test Weather Agent",
                description="A test agent for weather analysis",
                mcp_server_id="test-mcp-server-id",
                capabilities=["weather_current", "weather_forecast"],
                tags=["weather", "test"],
                metadata={
                    "test": True,
                    "created_by": "test_script"
                }
            )
            
            # Create test agent with endpoints
            from ..utils.iatp_utils import create_iatp_endpoints
            test_agent.endpoints = create_iatp_endpoints("http://weather-agent:8100", supports_streaming=True)
            
            # Add to registry
            entry = await agent_registry.add_utility_agent(
                test_agent, 
                tags=["weather", "test", "api"]
            )
            print(f"✓ Added test agent: {entry.name} (ID: {entry.agent_id})")
            
            # Note: Query methods moved to iatp_search_api.py
            print(f"✓ Agent added successfully - use iatp_search_api.py for queries")
            
            # Get statistics
            stats = await agent_registry.get_statistics()
            print(f"✓ Registry statistics: {stats}")
            
            # Update health status - use the returned entry's agent_id
            updated = await agent_registry.update_health_status(entry.agent_id)
            print(f"✓ Updated health status: {updated}")
            
            agent_registry.close()
            
        except Exception as e:
            print(f"✗ UtilityAgentRegistry error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test MCPServerRegistry
        print("\n--- Testing MCPServerRegistry ---")
        try:
            # Need to set MONGODB_URI for MCPServerRegistry
            if not os.getenv("MONGODB_URI"):
                os.environ["MONGODB_URI"] = f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PASSWORD')}@{CLUSTER_URI}"
            
            mcp_registry = MCPServerRegistry()
            print(f"✓ Connected to MongoDB")
            print(f"✓ Using collection: {collection_names['mcp_server']}")
            
            # Add test MCP server
            server_id = await mcp_registry.add_mcp_server(
                name="test-weather-mcp",
                url="http://weather-mcp:8080",
                description="Test weather MCP server",
                server_type="streamable-http",
                capabilities=["weather", "forecast"],
                metadata={"version": "1.0.0"}
            )
            print(f"✓ Added test MCP server: test-weather-mcp")
            
            # Note: Query methods moved to iatp_search_api.py
            print(f"✓ MCP server added successfully - use iatp_search_api.py for queries")
            
            # Get specific server
            server = await mcp_registry.get_mcp_server("test-weather-mcp")
            if server:
                print(f"✓ Retrieved MCP server: {server['name']}")
            
            mcp_registry.close()
            
        except Exception as e:
            print(f"✗ MCPServerRegistry error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== Test Complete ===")
    
    # Run the test
    asyncio.run(test_registries()) 