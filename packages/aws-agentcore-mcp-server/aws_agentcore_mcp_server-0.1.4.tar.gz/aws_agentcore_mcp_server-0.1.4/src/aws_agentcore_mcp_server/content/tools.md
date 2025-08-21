# AgentCore Tools Integration

AWS AgentCore provides comprehensive tools integration capabilities, allowing you to extend your AI agents with external APIs, AWS services, and custom functionality.

## Core Tool Types

### AWS Service Tools
```python
from bedrock_agentcore.tools import AWSServiceTool
from strands import Agent, tool

@tool
def read_s3_object(bucket: str, key: str) -> str:
    """Read an object from S3."""
    s3_tool = AWSServiceTool("s3")
    response = s3_tool.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode('utf-8')

@tool
def send_sns_notification(topic_arn: str, message: str, subject: str = None) -> str:
    """Send a notification via SNS."""
    sns_tool = AWSServiceTool("sns")
    response = sns_tool.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    return f"Message sent with ID: {response['MessageId']}"

@tool
def query_dynamodb(table_name: str, key: dict) -> dict:
    """Query a DynamoDB table."""
    dynamodb_tool = AWSServiceTool("dynamodb")
    response = dynamodb_tool.get_item(
        TableName=table_name,
        Key=key
    )
    return response.get('Item', {})
```

### External API Tools
```python
from bedrock_agentcore.tools import HTTPTool
import json

@tool
def call_weather_api(city: str) -> str:
    """Get weather information for a city."""
    weather_tool = HTTPTool(
        base_url="https://api.openweathermap.org/data/2.5",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    
    response = weather_tool.get(
        endpoint="/weather",
        params={"q": city, "units": "metric"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return f"Weather in {city}: {data['weather'][0]['description']}, {data['main']['temp']}°C"
    else:
        return f"Failed to get weather data: {response.status_code}"

@tool
def search_github_repos(query: str, language: str = None) -> str:
    """Search GitHub repositories."""
    github_tool = HTTPTool(
        base_url="https://api.github.com",
        headers={"Accept": "application/vnd.github.v3+json"}
    )
    
    search_params = {"q": query}
    if language:
        search_params["q"] += f" language:{language}"
    
    response = github_tool.get("/search/repositories", params=search_params)
    
    if response.status_code == 200:
        data = response.json()
        repos = data['items'][:5]  # Top 5 results
        
        result = f"Found {data['total_count']} repositories:\n"
        for repo in repos:
            result += f"- {repo['full_name']}: {repo['description']}\n"
        
        return result
    else:
        return f"Search failed: {response.status_code}"
```

### Database Tools
```python
from bedrock_agentcore.tools import DatabaseTool

@tool
def query_customer_database(customer_id: str) -> dict:
    """Query customer information from database."""
    db_tool = DatabaseTool(
        connection_string="postgresql://user:pass@host:5432/dbname"
    )
    
    query = """
    SELECT customer_id, name, email, account_type, created_date
    FROM customers 
    WHERE customer_id = %s
    """
    
    result = db_tool.execute_query(query, (customer_id,))
    return result[0] if result else {}

@tool
def update_customer_preferences(customer_id: str, preferences: dict) -> str:
    """Update customer preferences in database."""
    db_tool = DatabaseTool(
        connection_string="postgresql://user:pass@host:5432/dbname"
    )
    
    query = """
    UPDATE customer_preferences 
    SET preferences = %s, updated_date = NOW()
    WHERE customer_id = %s
    """
    
    db_tool.execute_query(query, (json.dumps(preferences), customer_id))
    return f"Updated preferences for customer {customer_id}"
```

## Tool Configuration

### Tool Registry
```python
from bedrock_agentcore.tools import ToolRegistry

# Create a tool registry
tool_registry = ToolRegistry()

# Register tools with metadata
tool_registry.register_tool(
    name="weather_lookup",
    function=call_weather_api,
    description="Get current weather information for any city",
    parameters={
        "city": {
            "type": "string",
            "description": "The city name to get weather for",
            "required": True
        }
    },
    category="external_api",
    rate_limit={"calls_per_minute": 60}
)

tool_registry.register_tool(
    name="s3_reader",
    function=read_s3_object,
    description="Read content from S3 objects",
    parameters={
        "bucket": {"type": "string", "required": True},
        "key": {"type": "string", "required": True}
    },
    category="aws_service",
    permissions=["s3:GetObject"]
)
```

### Tool Authentication
```python
from bedrock_agentcore.tools import ToolAuthenticator

# Configure authentication for different tool types
auth_config = {
    "aws_services": {
        "type": "iam_role",
        "role_arn": "arn:aws:iam::123456789012:role/AgentCoreToolsRole"
    },
    "external_apis": {
        "github": {
            "type": "oauth",
            "client_id": "your_github_client_id",
            "client_secret": "your_github_client_secret"
        },
        "weather_api": {
            "type": "api_key",
            "key": "your_weather_api_key",
            "header": "X-API-Key"
        }
    },
    "databases": {
        "customer_db": {
            "type": "connection_string",
            "connection": "postgresql://user:pass@host:5432/dbname"
        }
    }
}

authenticator = ToolAuthenticator(auth_config)
```

## Advanced Tool Features

### Tool Chaining
```python
from bedrock_agentcore.tools import ToolChain

@tool
def analyze_customer_sentiment(customer_id: str) -> str:
    """Analyze customer sentiment from recent interactions."""
    
    # Chain multiple tools together
    chain = ToolChain()
    
    # Step 1: Get customer data
    customer_data = chain.execute(
        tool="query_customer_database",
        params={"customer_id": customer_id}
    )
    
    # Step 2: Get recent support tickets
    tickets = chain.execute(
        tool="get_support_tickets",
        params={"customer_id": customer_id, "days": 30}
    )
    
    # Step 3: Analyze sentiment
    sentiment_analysis = chain.execute(
        tool="analyze_text_sentiment",
        params={"text": " ".join([ticket["description"] for ticket in tickets])}
    )
    
    return f"Customer {customer_data['name']} sentiment: {sentiment_analysis['sentiment']} (confidence: {sentiment_analysis['confidence']})"
```

### Tool Caching
```python
from bedrock_agentcore.tools import ToolCache

# Configure caching for expensive operations
cache_config = {
    "weather_lookup": {"ttl": 600, "max_size": 100},  # 10 minutes
    "github_search": {"ttl": 3600, "max_size": 50},   # 1 hour
    "database_query": {"ttl": 300, "max_size": 200}   # 5 minutes
}

tool_cache = ToolCache(cache_config)

@tool
def cached_weather_lookup(city: str) -> str:
    """Get weather with caching."""
    cache_key = f"weather_{city.lower()}"
    
    # Check cache first
    cached_result = tool_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Call API if not cached
    result = call_weather_api(city)
    
    # Store in cache
    tool_cache.set(cache_key, result)
    
    return result
```

### Tool Monitoring
```python
from bedrock_agentcore.tools import ToolMonitor

tool_monitor = ToolMonitor()

@tool
def monitored_api_call(endpoint: str, params: dict) -> dict:
    """Make an API call with monitoring."""
    
    with tool_monitor.track_execution("external_api_call") as tracker:
        tracker.set_metadata({
            "endpoint": endpoint,
            "params_count": len(params)
        })
        
        try:
            response = make_api_call(endpoint, params)
            tracker.set_result_metadata({
                "status_code": response.status_code,
                "response_size": len(response.content)
            })
            return response.json()
            
        except Exception as e:
            tracker.set_error(str(e))
            raise
```

## Tool Security

### Input Validation
```python
from bedrock_agentcore.tools import InputValidator

def validate_s3_params(bucket: str, key: str) -> tuple[bool, str]:
    """Validate S3 parameters."""
    if not bucket or not isinstance(bucket, str):
        return False, "Bucket name must be a non-empty string"
    
    if not key or not isinstance(key, str):
        return False, "Object key must be a non-empty string"
    
    # Check for path traversal
    if ".." in key or key.startswith("/"):
        return False, "Invalid object key format"
    
    return True, "Valid"

@tool
def secure_s3_read(bucket: str, key: str) -> str:
    """Securely read from S3 with validation."""
    is_valid, message = validate_s3_params(bucket, key)
    
    if not is_valid:
        return f"Validation error: {message}"
    
    return read_s3_object(bucket, key)
```

### Rate Limiting
```python
from bedrock_agentcore.tools import RateLimiter

rate_limiter = RateLimiter({
    "external_api": {"calls_per_minute": 60, "burst": 10},
    "database": {"calls_per_minute": 100, "burst": 20},
    "aws_service": {"calls_per_minute": 200, "burst": 50}
})

@tool
def rate_limited_api_call(endpoint: str) -> dict:
    """Make rate-limited API call."""
    if not rate_limiter.allow_request("external_api"):
        return {"error": "Rate limit exceeded"}
    
    return make_api_call(endpoint)
```

## Tool Integration Patterns

### Microservice Integration
```python
from bedrock_agentcore.tools import MicroserviceTool

@tool
def call_user_service(user_id: str, action: str) -> dict:
    """Call user microservice."""
    user_service = MicroserviceTool(
        service_name="user-service",
        base_url="https://user-service.internal.com",
        auth_type="service_token"
    )
    
    return user_service.call(f"/users/{user_id}/{action}")

@tool
def call_notification_service(message: dict) -> str:
    """Send notification via microservice."""
    notification_service = MicroserviceTool(
        service_name="notification-service",
        base_url="https://notification-service.internal.com"
    )
    
    response = notification_service.post("/notifications", json=message)
    return f"Notification sent: {response['id']}"
```

### Event-Driven Tools
```python
from bedrock_agentcore.tools import EventDrivenTool

@tool
def trigger_workflow(workflow_name: str, payload: dict) -> str:
    """Trigger a workflow via events."""
    event_tool = EventDrivenTool(
        event_bus="arn:aws:events:us-east-1:123456789012:event-bus/agent-events"
    )
    
    event_tool.publish_event(
        source="agentcore.tools",
        detail_type="WorkflowTrigger",
        detail={
            "workflow_name": workflow_name,
            "payload": payload,
            "triggered_by": "agent"
        }
    )
    
    return f"Workflow '{workflow_name}' triggered"
```

## Complete Integration Example

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.tools import ToolRegistry, ToolAuthenticator, ToolMonitor
from strands import Agent

# Initialize components
app = BedrockAgentCoreApp()
agent = Agent()
tool_registry = ToolRegistry()
tool_monitor = ToolMonitor()

# Configure authentication
auth_config = {
    "aws_services": {
        "type": "iam_role",
        "role_arn": "arn:aws:iam::123456789012:role/AgentToolsRole"
    },
    "external_apis": {
        "weather": {"type": "api_key", "key": "weather_api_key"}
    }
}

authenticator = ToolAuthenticator(auth_config)

# Register and configure tools
tools = [
    read_s3_object,
    send_sns_notification,
    call_weather_api,
    query_customer_database,
    analyze_customer_sentiment
]

for tool_func in tools:
    tool_registry.register_tool_from_function(tool_func)
    agent.add_tool(tool_func)

# Add middleware
app.add_middleware(authenticator.middleware)
app.add_middleware(tool_monitor.middleware)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    
    # Process with agent and tools
    result = agent(user_message)
    
    # Get tool usage statistics
    tool_stats = tool_monitor.get_usage_stats()
    
    return {
        "result": result.message,
        "tool_usage": tool_stats
    }

if __name__ == "__main__":
    app.run()
```

## Best Practices

1. **Tool Organization**: Group related tools and use clear naming conventions
2. **Error Handling**: Implement robust error handling for all external calls
3. **Security**: Always validate inputs and use appropriate authentication
4. **Performance**: Use caching and rate limiting for expensive operations
5. **Monitoring**: Track tool usage and performance metrics
6. **Documentation**: Provide clear descriptions and parameter specifications
7. **Testing**: Test tools independently before integrating with agents
8. **Versioning**: Version your tools for backward compatibility
