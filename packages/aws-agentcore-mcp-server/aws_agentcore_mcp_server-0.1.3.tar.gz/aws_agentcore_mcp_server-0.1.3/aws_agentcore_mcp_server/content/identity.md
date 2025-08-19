# AgentCore Identity

AgentCore Identity provides centralized management of agent identities and credentials, ensuring secure authentication and authorization for AI agents.

## Key Features

- **Identity Directory**: Organize and manage agent identities
- **Authorizer**: Validate access requests and permissions
- **Resource Credential Provider**: Access downstream services (Google, GitHub, etc.)
- **Token Vault**: Securely store OAuth tokens and API keys

## Authentication Methods

### AWS Sigv4
```python
from bedrock_agentcore.identity import IdentityClient

identity_client = IdentityClient()
credentials = identity_client.get_aws_credentials(
    agent_id="my-agent",
    service="s3"
)
```

### OAuth 2.0 Flow
```python
from bedrock_agentcore.identity import OAuthProvider

oauth_provider = OAuthProvider()
token = oauth_provider.get_access_token(
    provider="github",
    agent_id="my-agent"
)
```

### API Key Management
```python
from bedrock_agentcore.identity import APIKeyManager

api_key_manager = APIKeyManager()
api_key = api_key_manager.get_api_key(
    service="external-api",
    agent_id="my-agent"
)
```

## Setting Up Agent Identity

1. **Create an agent identity**:
   ```python
   from bedrock_agentcore.identity import IdentityManager
   
   identity_manager = IdentityManager()
   agent_identity = identity_manager.create_identity(
       agent_id="my-agent",
       name="My AI Agent",
       description="A helpful AI assistant"
   )
   ```

2. **Configure permissions**:
   ```python
   identity_manager.grant_permission(
       agent_id="my-agent",
       resource="s3://my-bucket/*",
       actions=["s3:GetObject", "s3:PutObject"]
   )
   ```

3. **Add external service credentials**:
   ```python
   identity_manager.add_oauth_provider(
       agent_id="my-agent",
       provider="github",
       client_id="your-client-id",
       client_secret="your-client-secret"
   )
   ```

## Security Best Practices

- Use least privilege principle for agent permissions
- Regularly rotate OAuth tokens and API keys
- Monitor agent access patterns through CloudTrail
- Implement proper error handling for authentication failures
- Use encrypted storage for sensitive credentials

## Integration with Other AgentCore Components

AgentCore Identity seamlessly integrates with:
- **Gateway**: Provides credentials for external API calls
- **Observability**: Logs authentication events for monitoring
- **Memory**: Secures access to stored agent context
- **Code Interpreter**: Manages permissions for code execution

## Example: Multi-Service Agent

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.identity import IdentityClient
from strands import Agent, tool

app = BedrockAgentCoreApp()
agent = Agent()
identity_client = IdentityClient()

@tool
def access_github_repo(repo_name: str) -> str:
    """Access a GitHub repository using OAuth credentials."""
    token = identity_client.get_oauth_token(
        provider="github",
        agent_id="my-agent"
    )
    # Use token to access GitHub API
    return f"Accessed repository: {repo_name}"

@tool
def read_s3_file(bucket: str, key: str) -> str:
    """Read a file from S3 using AWS credentials."""
    credentials = identity_client.get_aws_credentials(
        agent_id="my-agent",
        service="s3"
    )
    # Use credentials to access S3
    return f"Read file: s3://{bucket}/{key}"

agent.add_tool(access_github_repo)
agent.add_tool(read_s3_file)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    result = agent(user_message)
    return {"result": result.message}
```
