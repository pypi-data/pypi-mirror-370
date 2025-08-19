# AgentCore Memory

AgentCore Memory provides both short-term session memory and long-term memory storage, enabling the creation of context-aware agents that can retain conversation history and learn from interactions.

## Key Features

- **Short-term Memory**: Session-based memory with configurable retention (up to 365 days)
- **Long-term Memory**: Persistent storage for important information
- **Encryption**: Data encrypted at rest and in transit
- **Semantic Search**: Find relevant memories using semantic similarity
- **Memory Types**: Support for different memory types (episodic, semantic, procedural)
- **Automatic Cleanup**: Configurable memory retention policies

## Memory Types

### Session Memory (Short-term)
```python
from bedrock_agentcore.memory import SessionMemory

session_memory = SessionMemory(
    session_id="user-123-session",
    retention_days=30
)

# Store conversation context
session_memory.store("user_preference", {
    "language": "English",
    "communication_style": "formal",
    "topics_of_interest": ["technology", "business"]
})

# Retrieve context
preferences = session_memory.retrieve("user_preference")
```

### Long-term Memory (Persistent)
```python
from bedrock_agentcore.memory import LongTermMemory

long_term_memory = LongTermMemory(
    agent_id="customer-support-agent",
    memory_type="semantic"
)

# Store important facts
long_term_memory.store("customer_info", {
    "customer_id": "cust-456",
    "name": "John Doe",
    "account_type": "premium",
    "previous_issues": ["billing", "technical_support"],
    "satisfaction_score": 4.5
})

# Retrieve with semantic search
relevant_info = long_term_memory.search(
    query="customer billing issues",
    limit=5
)
```

## Basic Usage

### Setting Up Memory
```python
from bedrock_agentcore.memory import MemoryManager
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

memory_manager = MemoryManager(
    agent_id="my-agent",
    session_retention_days=90,
    enable_long_term_memory=True
)

app.add_middleware(memory_manager.middleware)
```

### Storing Memories
```python
from strands import Agent, tool

@tool
def remember_user_info(user_id: str, info: dict) -> str:
    """Store user information in memory."""
    memory_manager.store_memory(
        memory_type="user_profile",
        key=f"user_{user_id}",
        content=info,
        tags=["user_info", "profile"]
    )
    return f"Remembered information for user {user_id}"

@tool
def remember_conversation(conversation_summary: str) -> str:
    """Store conversation summary in memory."""
    memory_manager.store_memory(
        memory_type="conversation",
        content={
            "summary": conversation_summary,
            "timestamp": memory_manager.get_current_timestamp(),
            "importance": "high"
        },
        tags=["conversation", "summary"]
    )
    return "Conversation summary stored"
```

### Retrieving Memories
```python
@tool
def recall_user_info(user_id: str) -> str:
    """Retrieve user information from memory."""
    user_info = memory_manager.retrieve_memory(
        key=f"user_{user_id}",
        memory_type="user_profile"
    )
    
    if user_info:
        return f"User info: {user_info}"
    else:
        return f"No information found for user {user_id}"

@tool
def search_conversations(query: str) -> str:
    """Search previous conversations."""
    results = memory_manager.search_memories(
        query=query,
        memory_type="conversation",
        limit=3
    )
    
    summaries = []
    for result in results:
        summaries.append(f"- {result['content']['summary']} (Score: {result['score']:.2f})")
    
    return "Relevant conversations:\n" + "\n".join(summaries)
```

## Advanced Memory Operations

### Episodic Memory
```python
from bedrock_agentcore.memory import EpisodicMemory

episodic_memory = EpisodicMemory(agent_id="my-agent")

@tool
def remember_event(event_description: str, context: dict) -> str:
    """Store an episodic memory of an event."""
    episode = {
        "description": event_description,
        "context": context,
        "timestamp": episodic_memory.get_current_timestamp(),
        "location": context.get("location", "unknown"),
        "participants": context.get("participants", [])
    }
    
    episodic_memory.store_episode(episode)
    return f"Remembered event: {event_description}"

@tool
def recall_similar_events(event_query: str) -> str:
    """Recall similar past events."""
    similar_events = episodic_memory.find_similar_episodes(
        query=event_query,
        similarity_threshold=0.7,
        limit=3
    )
    
    if similar_events:
        descriptions = [event["description"] for event in similar_events]
        return "Similar past events:\n" + "\n".join(f"- {desc}" for desc in descriptions)
    else:
        return "No similar events found in memory"
```

### Semantic Memory
```python
from bedrock_agentcore.memory import SemanticMemory

semantic_memory = SemanticMemory(agent_id="my-agent")

@tool
def learn_fact(fact: str, category: str) -> str:
    """Learn and store a new fact."""
    semantic_memory.store_fact(
        fact=fact,
        category=category,
        confidence=0.9,
        source="user_input"
    )
    return f"Learned new fact in category '{category}': {fact}"

@tool
def retrieve_knowledge(topic: str) -> str:
    """Retrieve knowledge about a topic."""
    facts = semantic_memory.get_facts_about(
        topic=topic,
        confidence_threshold=0.7
    )
    
    if facts:
        fact_list = [f"- {fact['content']} (Confidence: {fact['confidence']:.2f})" 
                    for fact in facts]
        return f"Knowledge about {topic}:\n" + "\n".join(fact_list)
    else:
        return f"No knowledge found about {topic}"
```

### Procedural Memory
```python
from bedrock_agentcore.memory import ProceduralMemory

procedural_memory = ProceduralMemory(agent_id="my-agent")

@tool
def learn_procedure(procedure_name: str, steps: list) -> str:
    """Learn a new procedure."""
    procedure = {
        "name": procedure_name,
        "steps": steps,
        "success_rate": 1.0,
        "last_used": None
    }
    
    procedural_memory.store_procedure(procedure)
    return f"Learned procedure: {procedure_name}"

@tool
def execute_procedure(procedure_name: str) -> str:
    """Execute a learned procedure."""
    procedure = procedural_memory.get_procedure(procedure_name)
    
    if procedure:
        steps = procedure["steps"]
        procedural_memory.update_usage(procedure_name)
        
        return f"Executing {procedure_name}:\n" + "\n".join(f"{i+1}. {step}" 
                                                           for i, step in enumerate(steps))
    else:
        return f"Procedure '{procedure_name}' not found in memory"
```

## Memory Configuration

### Retention Policies
```python
from bedrock_agentcore.memory import RetentionPolicy

# Configure different retention policies
retention_policies = {
    "user_profiles": RetentionPolicy(days=365, priority="high"),
    "conversations": RetentionPolicy(days=90, priority="medium"),
    "temporary_data": RetentionPolicy(days=7, priority="low"),
    "important_facts": RetentionPolicy(days=-1, priority="critical")  # Never expire
}

memory_manager.set_retention_policies(retention_policies)
```

### Memory Encryption
```python
from bedrock_agentcore.memory import EncryptionConfig

encryption_config = EncryptionConfig(
    encryption_key_id="",
    enable_field_level_encryption=True,
    sensitive_fields=["user_data", "personal_info", "credentials"]
)

memory_manager.configure_encryption(encryption_config)
```

### Memory Indexing
```python
from bedrock_agentcore.memory import IndexConfig

index_config = IndexConfig(
    enable_semantic_search=True,
    embedding_model="amazon.titan-embed-text-v1",
    index_fields=["content", "tags", "category"],
    similarity_threshold=0.75
)

memory_manager.configure_indexing(index_config)
```

## Memory Analytics

### Memory Usage Statistics
```python
@tool
def get_memory_stats() -> str:
    """Get memory usage statistics."""
    stats = memory_manager.get_memory_statistics()
    
    return f"""Memory Statistics:
- Total memories stored: {stats['total_memories']}
- Session memories: {stats['session_memories']}
- Long-term memories: {stats['long_term_memories']}
- Storage used: {stats['storage_mb']:.2f} MB
- Most accessed memories: {', '.join(stats['top_accessed'])}
- Memory types: {', '.join(stats['memory_types'])}
"""

@tool
def analyze_memory_patterns() -> str:
    """Analyze memory access patterns."""
    patterns = memory_manager.analyze_access_patterns()
    
    insights = []
    insights.append(f"Most frequently accessed: {patterns['most_frequent']}")
    insights.append(f"Recent access trend: {patterns['trend']}")
    insights.append(f"Peak usage time: {patterns['peak_time']}")
    
    return "Memory Access Patterns:\n" + "\n".join(f"- {insight}" for insight in insights)
```

### Memory Optimization
```python
@tool
def optimize_memory() -> str:
    """Optimize memory storage and cleanup old entries."""
    optimization_result = memory_manager.optimize_memory()
    
    return f"""Memory Optimization Complete:
- Memories cleaned up: {optimization_result['cleaned_up']}
- Storage freed: {optimization_result['storage_freed_mb']:.2f} MB
- Indexes rebuilt: {optimization_result['indexes_rebuilt']}
- Performance improvement: {optimization_result['performance_gain']:.1f}%
"""
```

## Integration Example

```python
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryManager
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

# Initialize memory manager
memory_manager = MemoryManager(
    agent_id="customer-service-agent",
    session_retention_days=180,
    enable_long_term_memory=True
)

app.add_middleware(memory_manager.middleware)

# Add memory tools to agent
agent.add_tool(remember_user_info)
agent.add_tool(recall_user_info)
agent.add_tool(search_conversations)
agent.add_tool(remember_event)
agent.add_tool(learn_fact)
agent.add_tool(retrieve_knowledge)

@app.entrypoint
def invoke(payload):
    # Extract session information
    session_id = payload.get("session_id", "default")
    user_id = payload.get("user_id")
    
    # Set memory context
    memory_manager.set_session_context(session_id, user_id)
    
    # Process user message
    user_message = payload.get("prompt")
    
    # Retrieve relevant context from memory
    context = memory_manager.get_relevant_context(user_message)
    
    # Add context to the prompt
    enhanced_prompt = f"Context: {context}\n\nUser: {user_message}"
    
    # Process with agent
    result = agent(enhanced_prompt)
    
    # Store conversation in memory
    memory_manager.store_conversation_turn(
        user_message=user_message,
        agent_response=result.message,
        session_id=session_id
    )
    
    return {"result": result.message}
```

## Best Practices

1. **Memory Hygiene**: Regularly clean up old and irrelevant memories
2. **Privacy**: Be mindful of storing sensitive information
3. **Performance**: Use appropriate indexing for fast retrieval
4. **Context Relevance**: Store only relevant context to avoid noise
5. **Memory Types**: Use appropriate memory types for different kinds of information
6. **Retention Policies**: Set appropriate retention periods for different memory types
7. **Encryption**: Always encrypt sensitive memories
8. **Monitoring**: Monitor memory usage and performance regularly
