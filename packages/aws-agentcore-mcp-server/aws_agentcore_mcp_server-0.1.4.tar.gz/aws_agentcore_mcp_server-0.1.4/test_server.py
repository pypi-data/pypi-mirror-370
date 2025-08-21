#!/usr/bin/env python3
"""Simple test script for AWS AgentCore MCP Server."""

import asyncio
from aws_agentcore_mcp_server.server import (
    quickstart, agentcore_identity, agentcore_gateway, 
    agentcore_observability, agentcore_code_interpreter, 
    agentcore_memory, agentcore_tools
)

async def test_tools():
    """Test all available tools."""
    print("Testing AWS AgentCore MCP Server tools...")
    
    # Test quickstart
    result = await quickstart()
    print(f"✓ quickstart tool works (content length: {len(result)} chars)")
    
    # Test identity
    result = await agentcore_identity()
    print(f"✓ agentcore_identity tool works (content length: {len(result)} chars)")
    
    # Test gateway
    result = await agentcore_gateway()
    print(f"✓ agentcore_gateway tool works (content length: {len(result)} chars)")
    
    # Test observability
    result = await agentcore_observability()
    print(f"✓ agentcore_observability tool works (content length: {len(result)} chars)")
    
    # Test code interpreter
    result = await agentcore_code_interpreter()
    print(f"✓ agentcore_code_interpreter tool works (content length: {len(result)} chars)")
    
    # Test memory
    result = await agentcore_memory()
    print(f"✓ agentcore_memory tool works (content length: {len(result)} chars)")
    
    # Test tools
    result = await agentcore_tools()
    print(f"✓ agentcore_tools tool works (content length: {len(result)} chars)")
    
    print("\n✅ All tools working correctly!")

if __name__ == "__main__":
    asyncio.run(test_tools())
