# Installation Guide

## Local Installation

1. **Clone and install the MCP server**:
   ```bash
   cd aws-agentcore-mcp-server
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Test the installation**:
   ```bash
   python test_server.py
   ```

## Configure with AI Tools

### Amazon Q Developer CLI

Add to `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "aws-agentcore": {
      "command": "python",
      "args": ["-m", "aws_agentcore_mcp_server"],
      "cwd": "/path/to/aws-agentcore-mcp-server"
    }
  }
}
```

### Claude Code

```bash
claude mcp add aws-agentcore python -m aws_agentcore_mcp_server
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aws-agentcore": {
      "command": "python",
      "args": ["-m", "aws_agentcore_mcp_server"],
      "cwd": "/path/to/aws-agentcore-mcp-server"
    }
  }
}
```

## Available Tools

- `quickstart()` - Get started with AWS AgentCore
- `agentcore_identity()` - Secure authentication and authorization
- `agentcore_gateway()` - External API integration
- `agentcore_observability()` - Monitoring and debugging
- `agentcore_code_interpreter()` - Secure code execution
- `agentcore_memory()` - Context-aware memory management
- `agentcore_tools()` - Tool integration patterns
