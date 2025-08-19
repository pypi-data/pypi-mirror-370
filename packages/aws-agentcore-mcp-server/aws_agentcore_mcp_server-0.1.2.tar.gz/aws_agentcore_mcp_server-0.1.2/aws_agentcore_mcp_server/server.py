from importlib import resources

from mcp.server.fastmcp import FastMCP

pkg_resources = resources.files("aws_agentcore_mcp_server")

mcp = FastMCP(
    "aws-agentcore-mcp-server",
    instructions="""
    # AWS AgentCore MCP Server

    This server provides tools to access AWS AgentCore documentation.
    AWS AgentCore is a comprehensive framework for building, securing, monitoring, 
    and managing AI agents at scale on Amazon Bedrock.

    The full documentation can be found at https://docs.aws.amazon.com/bedrock-agentcore/.
""",
)


@mcp.tool()
async def quickstart() -> str:
    """Quickstart documentation for AWS AgentCore SDK."""
    return pkg_resources.joinpath("content", "quickstart.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_identity() -> str:
    """Documentation on AgentCore Identity for secure agent authentication and authorization."""
    return pkg_resources.joinpath("content", "identity.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_gateway() -> str:
    """Documentation on AgentCore Gateway for integrating external APIs and services."""
    return pkg_resources.joinpath("content", "gateway.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_observability() -> str:
    """Documentation on AgentCore Observability for monitoring and debugging agents."""
    return pkg_resources.joinpath("content", "observability.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_code_interpreter() -> str:
    """Documentation on AgentCore Code Interpreter for executing code in agents."""
    return pkg_resources.joinpath("content", "code_interpreter.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_memory() -> str:
    """Documentation on AgentCore Memory for building context-aware agents."""
    return pkg_resources.joinpath("content", "memory.md").read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def agentcore_tools() -> str:
    """Documentation on integrating tools with AWS AgentCore agents."""
    return pkg_resources.joinpath("content", "tools.md").read_text(
        encoding="utf-8"
    )


def main():
    mcp.run()
