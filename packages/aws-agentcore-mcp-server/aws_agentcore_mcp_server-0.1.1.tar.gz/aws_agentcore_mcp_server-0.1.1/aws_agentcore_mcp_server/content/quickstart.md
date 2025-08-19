# AWS AgentCore Quickstart

AWS AgentCore is a comprehensive framework for building, securing, monitoring, and managing AI agents at scale on Amazon Bedrock.

## Installation

Install the AWS AgentCore SDK and dependencies:

```bash
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit
```

## Basic Agent Setup

Create a simple agent script (`my_agent.py`):

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
```

## Running Locally

Execute your agent locally:

```bash
python my_agent.py
```

## Deployment with AgentCore Starter Toolkit

1. **Configure your agent**:
   ```bash
   agentcore configure --entrypoint my_agent.py -er <YOUR_IAM_ROLE_ARN>
   ```

2. **Deploy to AWS**:
   ```bash
   agentcore launch
   ```

This automates Docker image creation, ECR repository setup, and cloud deployment.

## Key Components

- **AgentCore Identity**: Centralized management of agent identities and credentials
- **AgentCore Gateway**: Universal integration layer for APIs and external services
- **AgentCore Observability**: Advanced tracing and monitoring capabilities
- **AgentCore Code Interpreter**: Secure code execution within sandboxed sessions
- **AgentCore Memory**: Short-term and long-term memory storage for context-aware agents

## Next Steps

- Explore [AgentCore Identity](agentcore_identity) for secure authentication
- Learn about [AgentCore Tools](agentcore_tools) for extending agent capabilities
- Set up [AgentCore Observability](agentcore_observability) for monitoring
- Use [AgentCore Code Interpreter](agentcore_code_interpreter) for dynamic computations
- Implement [AgentCore Memory](agentcore_memory) for persistent context
- Configure [AgentCore Gateway](agentcore_gateway) for external integrations
