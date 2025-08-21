# AgentCore Observability

AgentCore Observability provides advanced tracing, debugging, and real-time monitoring capabilities for AI agents in production environments.

## Key Features

- **Distributed Tracing**: Track requests across multiple services and components
- **Real-time Monitoring**: Monitor agent performance and health metrics
- **CloudWatch Integration**: Native integration with Amazon CloudWatch
- **OpenTelemetry Support**: Compatible with OpenTelemetry standards
- **Custom Metrics**: Define and track custom business metrics
- **Alerting**: Set up alerts for performance issues and errors

## Setting Up Observability

### Basic Configuration
```python
from bedrock_agentcore.observability import ObservabilityClient
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
observability = ObservabilityClient(
    service_name="my-agent",
    environment="production",
    enable_tracing=True,
    enable_metrics=True,
    enable_logging=True
)

app.add_middleware(observability.middleware)
```

### CloudWatch Integration
```python
from bedrock_agentcore.observability import CloudWatchConfig

cloudwatch_config = CloudWatchConfig(
    region="us-east-1",
    namespace="AgentCore/MyAgent",
    log_group="/aws/agentcore/my-agent"
)

observability.configure_cloudwatch(cloudwatch_config)
```

## Tracing

### Automatic Tracing
```python
from bedrock_agentcore.observability import trace

@trace(operation_name="process_user_request")
def process_request(user_input: str) -> str:
    """Process user request with automatic tracing."""
    # Your processing logic here
    return "Processed: " + user_input
```

### Manual Tracing
```python
from bedrock_agentcore.observability import Tracer

tracer = Tracer("my-agent")

def complex_operation():
    with tracer.start_span("database_query") as span:
        span.set_attribute("query_type", "SELECT")
        span.set_attribute("table", "users")
        
        # Database operation
        result = query_database()
        
        span.set_attribute("result_count", len(result))
        return result
```

### Distributed Tracing
```python
from bedrock_agentcore.observability import DistributedTracer

distributed_tracer = DistributedTracer()

@distributed_tracer.trace_async
async def call_external_service(service_url: str):
    """Call external service with distributed tracing."""
    headers = distributed_tracer.inject_headers()
    response = await http_client.get(service_url, headers=headers)
    return response
```

## Metrics

### Built-in Metrics
AgentCore automatically tracks:
- Request count and rate
- Response time percentiles
- Error rates
- Memory usage
- CPU utilization

### Custom Metrics
```python
from bedrock_agentcore.observability import MetricsClient

metrics = MetricsClient()

# Counter metric
metrics.increment("user_requests_total", tags={"endpoint": "/chat"})

# Gauge metric
metrics.gauge("active_sessions", 42)

# Histogram metric
metrics.histogram("response_time_ms", 150.5)

# Timer context manager
with metrics.timer("processing_time"):
    # Your processing logic
    process_data()
```

### Business Metrics
```python
from bedrock_agentcore.observability import BusinessMetrics

business_metrics = BusinessMetrics()

# Track business-specific events
business_metrics.track_event("user_satisfaction", {
    "rating": 5,
    "category": "helpful_response",
    "user_id": "user123"
})

# Track conversion metrics
business_metrics.track_conversion("task_completion", {
    "task_type": "data_analysis",
    "success": True,
    "duration_seconds": 45
})
```

## Logging

### Structured Logging
```python
from bedrock_agentcore.observability import Logger

logger = Logger("my-agent")

# Structured log entries
logger.info("User request processed", {
    "user_id": "user123",
    "request_type": "chat",
    "response_time_ms": 250,
    "success": True
})

logger.error("External API call failed", {
    "api_endpoint": "https://api.example.com/data",
    "error_code": "TIMEOUT",
    "retry_count": 3
})
```

### Log Correlation
```python
from bedrock_agentcore.observability import CorrelationLogger

correlation_logger = CorrelationLogger()

def handle_request(request_id: str, user_input: str):
    with correlation_logger.correlation_context(request_id=request_id):
        logger.info("Processing request", {"input_length": len(user_input)})
        
        result = process_input(user_input)
        
        logger.info("Request completed", {"output_length": len(result)})
        return result
```

## Alerting

### CloudWatch Alarms
```python
from bedrock_agentcore.observability import AlertManager

alert_manager = AlertManager()

# Error rate alarm
alert_manager.create_alarm(
    name="HighErrorRate",
    metric="error_rate",
    threshold=0.05,  # 5%
    comparison="GreaterThanThreshold",
    evaluation_periods=2,
    notification_topic="arn:aws:sns:us-east-1:123456789012:agent-alerts"
)

# Response time alarm
alert_manager.create_alarm(
    name="HighResponseTime",
    metric="response_time_p95",
    threshold=5000,  # 5 seconds
    comparison="GreaterThanThreshold",
    evaluation_periods=3
)
```

### Custom Alerts
```python
from bedrock_agentcore.observability import CustomAlert

def check_agent_health():
    """Custom health check function."""
    # Your health check logic
    if memory_usage > 0.9:
        return False, "High memory usage"
    if error_rate > 0.1:
        return False, "High error rate"
    return True, "Healthy"

custom_alert = CustomAlert(
    name="AgentHealthCheck",
    check_function=check_agent_health,
    interval_seconds=60,
    notification_topic="agent-health-alerts"
)

custom_alert.start()
```

## Dashboard Creation

### CloudWatch Dashboard
```python
from bedrock_agentcore.observability import DashboardBuilder

dashboard = DashboardBuilder("MyAgentDashboard")

# Add metrics widgets
dashboard.add_metric_widget(
    title="Request Rate",
    metrics=["requests_per_second"],
    period=300
)

dashboard.add_metric_widget(
    title="Error Rate",
    metrics=["error_rate"],
    period=300,
    yAxis={"left": {"min": 0, "max": 1}}
)

dashboard.add_log_widget(
    title="Recent Errors",
    log_group="/aws/agentcore/my-agent",
    query="fields @timestamp, @message | filter @message like /ERROR/"
)

# Deploy dashboard
dashboard.deploy()
```

## Performance Monitoring

### Agent Performance Metrics
```python
from bedrock_agentcore.observability import PerformanceMonitor

performance_monitor = PerformanceMonitor()

@performance_monitor.monitor_performance
def agent_inference(user_input: str) -> str:
    """Monitor agent inference performance."""
    # Agent processing logic
    return process_with_llm(user_input)

# Get performance insights
insights = performance_monitor.get_insights()
print(f"Average response time: {insights.avg_response_time}ms")
print(f"95th percentile: {insights.p95_response_time}ms")
print(f"Error rate: {insights.error_rate}%")
```

### Resource Utilization
```python
from bedrock_agentcore.observability import ResourceMonitor

resource_monitor = ResourceMonitor()

# Monitor system resources
resource_monitor.track_memory_usage()
resource_monitor.track_cpu_usage()
resource_monitor.track_disk_usage()

# Get resource utilization report
report = resource_monitor.get_utilization_report()
```

## Example: Complete Observability Setup

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.observability import (
    ObservabilityClient, 
    CloudWatchConfig,
    AlertManager,
    DashboardBuilder
)
from strands import Agent, tool

# Initialize observability
observability = ObservabilityClient(
    service_name="customer-support-agent",
    environment="production"
)

cloudwatch_config = CloudWatchConfig(
    region="us-east-1",
    namespace="AgentCore/CustomerSupport",
    log_group="/aws/agentcore/customer-support"
)

observability.configure_cloudwatch(cloudwatch_config)

# Set up alerts
alert_manager = AlertManager()
alert_manager.create_alarm(
    name="CustomerSupportErrorRate",
    metric="error_rate",
    threshold=0.02,
    notification_topic="customer-support-alerts"
)

# Create dashboard
dashboard = DashboardBuilder("CustomerSupportDashboard")
dashboard.add_metric_widget("Request Rate", ["requests_per_second"])
dashboard.add_metric_widget("Customer Satisfaction", ["satisfaction_score"])
dashboard.deploy()

# Initialize app with observability
app = BedrockAgentCoreApp()
app.add_middleware(observability.middleware)

agent = Agent()

@tool
@observability.trace(operation_name="resolve_customer_issue")
def resolve_customer_issue(issue_description: str) -> str:
    """Resolve customer issue with full observability."""
    observability.metrics.increment("customer_issues_total")
    
    with observability.timer("issue_resolution_time"):
        # Process the issue
        resolution = process_issue(issue_description)
        
        # Track satisfaction
        observability.metrics.gauge("satisfaction_score", 4.5)
        
        return resolution

agent.add_tool(resolve_customer_issue)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    result = agent(user_message)
    return {"result": result.message}
```
