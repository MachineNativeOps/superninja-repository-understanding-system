"""
MCP Integration Layer: Model Context Protocol integration.

This package provides MCP client functionality for tool discovery,
invocation, and security.
"""

from .a2a_client import (
    A2AClient,
    A2AMessage,
    A2AMessageType,
    A2AProtocolVersion,
    AgentCapabilities,
    AgentInfo,
    DelegationRequest,
    DelegationResponse,
)
from .mcp_client import (
    MCPClient,
    MCPServerConfig,
    MCPTool,
    MCPToolCall,
    MCPToolResult,
    MCPTransportType,
)
from .mcp_security import (
    AccessPolicy,
    AuthConfig,
    AuthMethod,
    MCPSecurity,
    SecurityContext,
)
from .tool_router import RoutingPolicy, RoutingStrategy, ToolEndpoint, ToolRouter
from .tool_schemas import (
    ParameterSchema,
    SchemaConverter,
    SchemaFormat,
    SchemaValidator,
    ToolSchema,
    ToolSchemas,
)

__all__ = [
    # MCP Client
    "MCPClient",
    "MCPServerConfig",
    "MCPTransportType",
    "MCPTool",
    "MCPToolCall",
    "MCPToolResult",
    # Tool Router
    "ToolRouter",
    "ToolEndpoint",
    "RoutingPolicy",
    "RoutingStrategy",
    # Tool Schemas
    "ToolSchemas",
    "ToolSchema",
    "ParameterSchema",
    "SchemaValidator",
    "SchemaConverter",
    "SchemaFormat",
    # A2A Client
    "A2AClient",
    "AgentInfo",
    "AgentCapabilities",
    "A2AMessage",
    "DelegationRequest",
    "DelegationResponse",
    "A2AMessageType",
    "A2AProtocolVersion",
    # MCP Security
    "MCPSecurity",
    "AccessPolicy",
    "SecurityContext",
    "AuthConfig",
    "AuthMethod",
]
