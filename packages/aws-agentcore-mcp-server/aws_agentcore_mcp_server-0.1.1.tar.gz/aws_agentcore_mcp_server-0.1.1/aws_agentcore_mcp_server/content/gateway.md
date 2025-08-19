# AgentCore Gateway

AgentCore Gateway acts as a universal integration layer, converting APIs, AWS Lambda functions, or databases into tools compatible with the agent ecosystem.

## Key Features

- **Universal API Integration**: Convert any REST API into agent tools
- **Dual-sided Security**: OAuth-based inbound authorization plus IAM/API key outbound calls
- **Protocol Translation**: Seamlessly translate between different API formats
- **Rate Limiting**: Built-in protection against API abuse
- **Caching**: Improve performance with intelligent response caching

## Setting Up Gateway Integration

### Basic API Integration
```python
from bedrock_agentcore.gateway import GatewayClient
from strands import Agent, tool

gateway_client = GatewayClient()

@tool
def call_external_api(endpoint: str, params: dict) -> dict:
    """Call an external API through AgentCore Gateway."""
    response = gateway_client.call_api(
        endpoint=endpoint,
        method="GET",
        params=params,
        auth_type="oauth"
    )
    return response.json()
```

### Lambda Function Integration
```python
from bedrock_agentcore.gateway import LambdaIntegration

lambda_integration = LambdaIntegration()

@tool
def invoke_lambda_function(function_name: str, payload: dict) -> dict:
    """Invoke a Lambda function through AgentCore Gateway."""
    response = lambda_integration.invoke(
        function_name=function_name,
        payload=payload
    )
    return response
```

### Database Integration
```python
from bedrock_agentcore.gateway import DatabaseIntegration

db_integration = DatabaseIntegration()

@tool
def query_database(query: str) -> list:
    """Query a database through AgentCore Gateway."""
    results = db_integration.execute_query(
        query=query,
        database="my-database"
    )
    return results
```

## Configuration

### Gateway Configuration File
```yaml
# gateway-config.yaml
gateway:
  name: "my-agent-gateway"
  version: "1.0"
  
integrations:
  - name: "github-api"
    type: "rest-api"
    base_url: "https://api.github.com"
    auth:
      type: "oauth"
      provider: "github"
    rate_limit:
      requests_per_minute: 60
      
  - name: "student-info-system"
    type: "rest-api"
    base_url: "https://sis.university.edu/api"
    auth:
      type: "api-key"
      header: "X-API-Key"
    cache:
      ttl: 300  # 5 minutes
      
  - name: "data-processor"
    type: "lambda"
    function_name: "data-processing-function"
    region: "us-east-1"
```

### Loading Configuration
```python
from bedrock_agentcore.gateway import Gateway

gateway = Gateway.from_config("gateway-config.yaml")
```

## Security Configuration

### OAuth Integration
```python
from bedrock_agentcore.gateway import OAuthConfig

oauth_config = OAuthConfig(
    provider="custom-provider",
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token",
    scopes=["read", "write"]
)

gateway.add_oauth_provider(oauth_config)
```

### API Key Configuration
```python
from bedrock_agentcore.gateway import APIKeyConfig

api_key_config = APIKeyConfig(
    name="external-service",
    key="your-api-key",
    header="Authorization",
    prefix="Bearer "
)

gateway.add_api_key_provider(api_key_config)
```

## Advanced Features

### Request/Response Transformation
```python
from bedrock_agentcore.gateway import Transformer

def transform_request(request):
    """Transform request before sending to external API."""
    request.headers["User-Agent"] = "AgentCore/1.0"
    return request

def transform_response(response):
    """Transform response before returning to agent."""
    return {
        "data": response.json(),
        "status": response.status_code,
        "timestamp": response.headers.get("Date")
    }

gateway.add_transformer(
    name="github-api",
    request_transformer=transform_request,
    response_transformer=transform_response
)
```

### Error Handling
```python
from bedrock_agentcore.gateway import ErrorHandler

def handle_api_error(error):
    """Handle API errors gracefully."""
    if error.status_code == 429:
        return {"error": "Rate limit exceeded", "retry_after": 60}
    elif error.status_code == 401:
        return {"error": "Authentication failed"}
    else:
        return {"error": f"API error: {error.message}"}

gateway.add_error_handler("github-api", handle_api_error)
```

## Example: Educational System Integration

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.gateway import Gateway
from strands import Agent, tool

app = BedrockAgentCoreApp()
agent = Agent()
gateway = Gateway.from_config("education-gateway.yaml")

@tool
def get_student_info(student_id: str) -> dict:
    """Get student information from the student information system."""
    return gateway.call_api(
        integration="student-info-system",
        endpoint=f"/students/{student_id}",
        method="GET"
    )

@tool
def get_course_schedule(course_id: str) -> dict:
    """Get course schedule from the learning management system."""
    return gateway.call_api(
        integration="lms-api",
        endpoint=f"/courses/{course_id}/schedule",
        method="GET"
    )

@tool
def process_enrollment_data(data: dict) -> dict:
    """Process enrollment data using a Lambda function."""
    return gateway.invoke_lambda(
        integration="data-processor",
        payload=data
    )

agent.add_tool(get_student_info)
agent.add_tool(get_course_schedule)
agent.add_tool(process_enrollment_data)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    result = agent(user_message)
    return {"result": result.message}
```

## Monitoring and Debugging

Gateway provides built-in monitoring capabilities:

```python
# Enable request/response logging
gateway.enable_logging(level="DEBUG")

# Add custom metrics
gateway.add_metric("api_calls_total", "counter")
gateway.add_metric("api_response_time", "histogram")

# Monitor gateway health
health_status = gateway.get_health_status()
```
